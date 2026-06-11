"""TritTape — tape-based autograd for trit neural networks.

Records the forward computation graph and computes trit-native
gradients via reverse-mode automatic differentiation.

Gradients flow as signed ints {-1, 0, +1} internally and are
converted to trits {0, 1, 2} for updates.
"""

from trinary.ai2.trit_module import TritModule, TritLinear
from trinary.ai2.trit_loss import TritLoss
from trinary.ai2.trit_math import DOT_TERM

_T2S = [-1, 0, 1]

# Global active tape (set by TritTape.__enter__)
_TAPE_ACTIVE = None


class TritTape:
    """Records forward passes and computes trit gradients.

    Usage:
        with TritTape() as tape:
            out = criterion(model(x), target)
        grads = tape.backward()
        trainer.apply_gradients(grads)
    """

    def __init__(self, model=None):
        self._records = []
        self._module_map = {}  # id(module) → path string
        self._prev_active = None
        if model is not None:
            self._build_module_map(model)

    def _build_module_map(self, mod, prefix=''):
        for name, child in mod._modules.items():
            child_path = name if not prefix else f"{prefix}.{name}"
            self._module_map[id(child)] = child_path
            self._build_module_map(child, child_path)

    def _param_path(self, module, param_name):
        mid = id(module)
        if mid in self._module_map:
            return f"{self._module_map[mid]}.{param_name}"
        return param_name

    def __enter__(self):
        global _TAPE_ACTIVE
        self._prev_active = _TAPE_ACTIVE
        _TAPE_ACTIVE = self
        self._records.clear()
        return self

    def __exit__(self, *args):
        global _TAPE_ACTIVE
        _TAPE_ACTIVE = self._prev_active

    def backward(self):
        """Compute trit gradients for all recorded modules.

        Returns:
            dict of {param_path: gradient_trit_list}
        """
        grads = {}

        if not self._records:
            return grads

        # Start gradient backprop from the last record
        last_mod, last_args, last_out = self._records[-1]

        if isinstance(last_mod, TritLoss):
            grad_output_signed = last_mod.gradient(*last_args)
        else:
            grad_output_signed = [1] * len(last_out)

        for module, args, out in reversed(self._records):
            if isinstance(module, TritLoss):
                continue
            elif isinstance(module, TritLinear):
                inp = args[0] if args else []
                inp_grad_signed, w_grad, b_grad = _backward_linear(
                    module, inp, out, grad_output_signed
                )
                self._store_grads(grads, module, 'weight', w_grad)
                if b_grad is not None:
                    self._store_grads(grads, module, 'bias', b_grad)
                grad_output_signed = inp_grad_signed
            else:
                pass

        return grads

    def _store_grads(self, grads, module, param_name, grad_signed):
        path = self._param_path(module, param_name)
        grads[path] = [_to_trit(g) for g in grad_signed]


def _to_signed(trit: int) -> int:
    return _T2S[trit]


def _to_trit(signed: int) -> int:
    if signed < -1:
        return 0
    if signed > 1:
        return 2
    return 0 if signed == -1 else (1 if signed == 0 else 2)


def _backward_linear(module, inp, out, grad_out_signed):
    w = module._params['weight']
    in_f = module.in_features
    out_f = module.out_features
    has_bias = 'bias' in module._params

    dt = DOT_TERM
    w_grad = [0] * len(w)
    b_grad = [0] * out_f if has_bias else None
    inp_grad = [0] * in_f

    for i in range(out_f):
        gz = grad_out_signed[i]
        if gz == 0:
            continue
        base = i * in_f
        for j in range(in_f):
            sx = _to_signed(inp[j])
            w_grad[base + j] += gz * sx
            sw = _to_signed(w[base + j])
            inp_grad[j] += gz * sw
        if has_bias:
            b_grad[i] += gz

    w_grad = [_clamp(g) for g in w_grad]
    inp_grad = [_clamp(g) for g in inp_grad]
    if has_bias:
        b_grad = [_clamp(g) for g in b_grad]

    return inp_grad, w_grad, b_grad


def _clamp(v: int) -> int:
    if v < -1:
        return -1
    if v > 1:
        return 1
    return v
