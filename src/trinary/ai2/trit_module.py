"""TritModule — composable trit neural network building blocks.

Every module stores weights as flat lists of trits {0,1,2} and
operates on trit inputs/outputs.  No floating point anywhere.
"""

import random
from trinary.ai2.trit_math import trit_linear, trit_linear_raw, ternary_step


class TritModule:
    """Base class for all trit neural network modules.

    Subclasses override forward().  Parameters are stored as
    flat lists of trits {0,1,2} in self._params.

    Forward calls are automatically recorded on the active
    TritTape (if any).
    """

    def __init__(self):
        self._params: dict[str, list] = {}
        self._param_shapes: dict[str, tuple] = {}
        self._modules: dict[str, TritModule] = {}
        self.training = True

    def forward(self, *args) -> list:
        raise NotImplementedError

    def __call__(self, *args) -> list:
        out = self.forward(*args)
        _record_forward(self, args, out)
        return out

    def parameters(self) -> dict[str, list]:
        params = {}
        for name, val in self._params.items():
            params[name] = val
        for name, mod in self._modules.items():
            for k, v in mod.parameters().items():
                params[f"{name}.{k}"] = v
        return params

    def named_modules(self) -> list[tuple[str, 'TritModule']]:
        modules = [('', self)]
        for name, mod in self._modules.items():
            modules.append((name, mod))
            for subname, submod in mod.named_modules():
                if subname:
                    modules.append((f"{name}.{subname}", submod))
        return modules

    def __repr__(self):
        return f"{self.__class__.__name__}()"


def _record_forward(module, args, output):
    from trinary.ai2.trit_graph import _TAPE_ACTIVE
    if _TAPE_ACTIVE is not None:
        _TAPE_ACTIVE._records.append((module, args, output))


class TritLinear(TritModule):
    """Fully-connected linear layer with ternary_step activation.

    weight: flat trit list (out_features * in_features)
    bias: flat trit list (out_features) or None

    forward: output = ternary_step(W @ input + bias)
    """

    def __init__(self, in_features: int, out_features: int,
                 bias: bool = True, seed: int = 42):
        super().__init__()
        rng = random.Random(seed)
        n_w = out_features * in_features
        weights = [rng.randint(0, 2) for _ in range(n_w)]
        self._params['weight'] = weights
        self._param_shapes['weight'] = (out_features, in_features)
        if bias:
            self._params['bias'] = [rng.randint(0, 2) for _ in range(out_features)]
            self._param_shapes['bias'] = (out_features,)
        self.in_features = in_features
        self.out_features = out_features

    def forward(self, x: list) -> list:
        w = self._params['weight']
        b = self._params.get('bias')
        return trit_linear(w, b, x, self.in_features, self.out_features)

    def forward_raw(self, x: list) -> list:
        w = self._params['weight']
        b = self._params.get('bias')
        return trit_linear_raw(w, b, x, self.in_features, self.out_features)

    def __repr__(self):
        return f"TritLinear({self.in_features}, {self.out_features})"


class TritSequential(TritModule):
    """Chain of modules, each feeding into the next."""

    def __init__(self, *modules: TritModule):
        super().__init__()
        for i, mod in enumerate(modules):
            self._modules[str(i)] = mod

    def forward(self, x: list) -> list:
        current = x
        for mod in self._modules.values():
            current = mod(current)
        return current

    def __repr__(self):
        mods = ", ".join(repr(m) for m in self._modules.values())
        return f"TritSequential({mods})"


class TritLinearMixed(TritLinear):
    """Mixed-precision TritLinear with float shadow weights and STE.

    Stores real-valued shadow weights. Forward pass quantizes to
    trits, backward pass uses STE (identity through quantization),
    weight update accumulates in float space.

    This enables learning non-linear problems (XOR, etc.) that
    trit-only SGD cannot solve.
    """

    def __init__(self, in_features: int, out_features: int,
                 bias: bool = True, seed: int = 42, lr: float = 0.1):
        rng = random.Random(seed)
        scale = (2.0 / in_features) ** 0.5
        n_w = out_features * in_features
        self._float_weight = [rng.gauss(0, scale) for _ in range(n_w)]
        self._float_bias = [rng.gauss(0, scale) for _ in range(out_features)] if bias else None
        self.lr = lr
        self.in_features = in_features
        self.out_features = out_features
        self._params: dict[str, list] = {}
        self._param_shapes: dict[str, tuple] = {}
        self._modules: dict[str, TritModule] = {}
        self.training = True
        self._sync_trit_weights()

    def _ternarize(self, v: float) -> int:
        if v < -0.33:
            return 0
        if v > 0.33:
            return 2
        return 1

    def _sync_trit_weights(self):
        self._params['weight'] = [self._ternarize(v) for v in self._float_weight]
        self._param_shapes['weight'] = (self.out_features, self.in_features)
        if self._float_bias is not None:
            self._params['bias'] = [self._ternarize(v) for v in self._float_bias]
            self._param_shapes['bias'] = (self.out_features,)

    def _apply_ste_raw(self, raw_grad: list, param_name: str, lr: float):
        """Apply raw accumulated signed gradient to a float shadow.

        TRIT_ADD convention: grad_trit=0(signed -1) DECREASES weight,
        grad_trit=2(signed +1) INCREASES weight.  For float shadows
        the update is: shadow += lr * signed_grad.

        Args:
            raw_grad: list of ints (accumulated signed gradients)
            param_name: 'weight' or 'bias'
            lr: learning rate
        """
        if param_name == 'weight':
            shadow = self._float_weight
        elif param_name == 'bias' and self._float_bias is not None:
            shadow = self._float_bias
        else:
            return
        for i in range(min(len(raw_grad), len(shadow))):
            shadow[i] += lr * raw_grad[i]
        self._sync_trit_weights()

    def apply_ste_gradients(self, grads: dict, path_prefix: str = ''):
        """Apply gradients to float shadows using STE update.

        Args:
            grads: dict from tape.backward()
            path_prefix: path prefix for this module (e.g., '0')
        """
        w_path = f"{path_prefix}.weight" if path_prefix else 'weight'
        b_path = f"{path_prefix}.bias" if path_prefix else 'bias'

        if w_path in grads:
            g = grads[w_path]
            for i in range(min(len(g), len(self._float_weight))):
                signed_g = -1 if g[i] == 0 else (0 if g[i] == 1 else 1)
                self._float_weight[i] += self.lr * signed_g

        if b_path in grads and self._float_bias is not None:
            g = grads[b_path]
            for i in range(min(len(g), len(self._float_bias))):
                signed_g = -1 if g[i] == 0 else (0 if g[i] == 1 else 1)
                self._float_bias[i] += self.lr * signed_g

        self._sync_trit_weights()


class TritTanh(TritModule):
    """Ternary_step activation as a standalone module."""

    def forward(self, x: list) -> list:
        return [ternary_step(v) for v in x]
