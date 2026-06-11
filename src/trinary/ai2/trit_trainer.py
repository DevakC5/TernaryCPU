"""TritTrainer — gradient descent trainer for trit neural networks.

Updates weights by adding their trit gradients directly:
  new_w[i] = TRIT_ADD[w[i]][grad_trit[i]]
where grad_trit encodes {-1, 0, +1} change direction.
"""

from trinary.ai2.trit_module import TritModule
from trinary.ai2.trit_loss import TritLoss
from trinary.ai2.trit_graph import TritTape
from trinary.ai2.trit_math import TRIT_ADD


def _signed_from_trit(t: int) -> int:
    """Convert gradient trit to signed value for accumulation."""
    if t == 0:
        return -1
    if t == 1:
        return 0
    return 1


def _trit_from_signed(s: int) -> int:
    """Convert accumulated signed gradient back to trit."""
    if s < -1:
        return 0
    if s > 1:
        return 2
    if s == -1:
        return 0
    if s == 0:
        return 1
    return 2


class TritTrainer:
    """Trains a TritModule using tape-based autograd and trit update rules.

    Args:
        model: TritModule to train
        criterion: TritLoss instance
    """

    def __init__(self, model: TritModule, criterion: TritLoss):
        self.model = model
        self.criterion = criterion
        self.grads = {}

    def _compute_grads(self, x: list, target) -> dict:
        """Forward-backward, return gradient dict."""
        with TritTape(model=self.model) as tape:
            out = self.model(x)
            loss = self.criterion(out, target)
        return loss[0], tape.backward()

    def train_step(self, x: list, target) -> int:
        """Single forward-backward-update step.

        Args:
            x: input trit list
            target: target (list for MSE, int index for CrossEntropy)

        Returns:
            loss trit {0,1,2}
        """
        loss, grads = self._compute_grads(x, target)
        self.apply_gradients(grads)
        return loss

    def train_batch(self, batch: list) -> float:
        """Accumulate gradients over batch, then apply once.

        Args:
            batch: list of (x, target) pairs

        Returns:
            average loss over batch
        """
        acc_grads = {}
        total_loss = 0
        for x, target in batch:
            loss, grads = self._compute_grads(x, target)
            total_loss += loss
            for path, g in grads.items():
                if path not in acc_grads:
                    acc_grads[path] = [0] * len(g)
                for i in range(len(g)):
                    acc_grads[path][i] += _signed_from_trit(g[i])

        # Convert accumulated signed gradients to trits
        final_grads = {}
        for path, acc in acc_grads.items():
            final_grads[path] = [_trit_from_signed(v) for v in acc]

        self.apply_gradients(final_grads)
        return total_loss / len(batch)

    def apply_gradients(self, grads: dict):
        """Apply gradient dict to model parameters.

        Update rule: param[i] = TRIT_ADD[param[i]][grad_trit[i]]
        where grad_trit encodes {-1, 0, +1} movement.
        """
        for path, grad in grads.items():
            parts = path.split('.')
            mod = self._resolve_module(parts[:-1])
            param_name = parts[-1]
            if mod is None or param_name not in mod._params:
                continue
            param = mod._params[param_name]
            for i in range(min(len(param), len(grad))):
                param[i] = TRIT_ADD[param[i]][grad[i]]

    def train(self, dataset: list, epochs: int = 100,
              verbose: bool = True) -> dict:
        """Full training loop over dataset using full-batch updates.

        Args:
            dataset: list of (x, target) pairs
            epochs: number of passes
            verbose: print progress

        Returns:
            history dict with 'loss' and 'accuracy' lists
        """
        history = {'loss': [], 'accuracy': []}
        for epoch in range(epochs):
            avg_loss = self.train_batch(dataset)
            acc = self.evaluate(dataset)
            history['loss'].append(avg_loss)
            history['accuracy'].append(acc)
            if verbose and (epoch + 1) % max(1, epochs // 10) == 0:
                print(f"  Epoch {epoch+1}/{epochs}  loss={avg_loss:.2f}  acc={acc:.2%}")
        return history

class TritTrainerMixed(TritTrainer):
    """Mixed-precision trainer using float shadows + STE.

    Uses TritLinearMixed layers with float shadow weights.
    Gradients are applied to float shadows, then trit weights
    are re-quantized.
    """

    def train_batch(self, batch: list) -> float:
        acc_grads = {}
        total_loss = 0
        for x, target in batch:
            loss, grads = self._compute_grads(x, target)
            total_loss += loss
            for path, g in grads.items():
                if path not in acc_grads:
                    acc_grads[path] = [0] * len(g)
                for i in range(len(g)):
                    acc_grads[path][i] += _signed_from_trit(g[i])

        # For mixed-precision layers: apply raw accumulated signed gradients directly
        # to float shadows.  No trit conversion — preserves gradient magnitude.
        for path, acc in acc_grads.items():
            parts = path.split('.')
            mod = self._resolve_module(parts[:-1])
            if mod is None:
                continue
            if hasattr(mod, 'apply_ste_gradients'):
                mod._apply_ste_raw(acc, parts[-1], mod.lr)
            else:
                # Regular TritLinear: clamp to {-1,0,+1} and use TRIT_ADD
                g = [_trit_from_signed(v) for v in acc]
                self._apply_to_param(mod, parts[-1], g)

        return total_loss / len(batch)

    def _apply_to_param(self, mod, param_name, grad):
        if param_name in mod._params:
            param = mod._params[param_name]
            for i in range(min(len(param), len(grad))):
                param[i] = TRIT_ADD[param[i]][grad[i]]

    def _resolve_module(self, name_parts: list) -> TritModule | None:
        mod = self.model
        for part in name_parts:
            if part == '':
                continue
            if part not in mod._modules:
                return None
            mod = mod._modules[part]
        return mod

    def compute_accuracy(self, x: list, target) -> float:
        """Compute accuracy for a single example."""
        out = self.model(x)
        if isinstance(target, int):
            from trinary.ai2.trit_loss import _argmax
            return 1.0 if _argmax(out) == target else 0.0
        correct = all(
            out[i] == target[i]
            for i in range(len(out))
        )
        return 1.0 if correct else 0.0

    def evaluate(self, dataset: list) -> float:
        """Evaluate accuracy over a list of (x, target) pairs."""
        if not dataset:
            return 0.0
        total = 0.0
        for x, target in dataset:
            total += self.compute_accuracy(x, target)
        return total / len(dataset)


