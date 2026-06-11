"""Trit loss functions — trit-native loss modules with analytic gradients.

All losses participate in TritTape recording and provide a
gradient() method that returns signed gradients {-1,0,+1}
for backpropagation.
"""

from trinary.ai2.trit_module import TritModule
from trinary.ai2.trit_math import ternary_step

_T2S = [-1, 0, 1]

_TRIT_ARGMAX_LUT = [
    [0, 0, 0],  # pred [0/0/0] → argmax 0
    [0, 0, 0],  # [0,0,0] same
    [0, 0, 0],
]


def _argmax(vals: list) -> int:
    """Argmax over trit list. Lower trit = lower signed."""
    best_i = 0
    best_v = _T2S[vals[0]]
    for i in range(1, len(vals)):
        v = _T2S[vals[i]]
        if v > best_v:
            best_v = v
            best_i = i
    return best_i


class TritLoss(TritModule):
    """Base class for trit loss functions.

    Subclasses must implement:
        forward(self, prediction, target) -> [loss_trit]
        gradient(self, prediction, target) -> signed_gradient_list
    """

    def forward(self, prediction: list, target) -> list:
        raise NotImplementedError

    def gradient(self, prediction: list, target) -> list:
        """Return signed gradient dL/dprediction in {-1,0,+1}."""
        raise NotImplementedError


class TritMSELoss(TritLoss):
    """Mean squared error in signed space, collapsed to trit.

    For each output position i:
      diff_i = signed(pred[i]) - signed(target[i])  ∈ {-2,-1,0,1,2}
      loss = ternary_step(mean(|diff_i|))
      gradient[i] = sign(diff_i)  ∈ {-1,0,+1}
    """

    def forward(self, prediction: list, target: list) -> list:
        n = len(prediction)
        if n == 0:
            return [1]
        total = 0
        for i in range(n):
            diff = _T2S[prediction[i]] - _T2S[target[i]]
            total += abs(diff)
        mean_diff = total / n  # float, but we clamp
        return [ternary_step(int(mean_diff * 2))]

    def gradient(self, prediction: list, target: list) -> list:
        grad = []
        for i in range(len(prediction)):
            diff = _T2S[prediction[i]] - _T2S[target[i]]
            if diff > 0:
                grad.append(1)
            elif diff < 0:
                grad.append(-1)
            else:
                grad.append(0)
        return grad


class TritCrossEntropyLoss(TritLoss):
    """Cross-entropy-like loss for N-class classification.

    Target is an integer class index 0..N-1.
    Prediction is an N-element trit vector.

    Loss = 0 if argmax(prediction) == target, else 1.

    Gradient: if wrong,
      +1 at target index  (push prediction toward target)
      -1 at predicted argmax index  (pull away from wrong)
      0 elsewhere
    If correct, all zero gradient.
    """

    def forward(self, prediction: list, target: int) -> list:
        if _argmax(prediction) == target:
            return [1]
        return [0]

    def gradient(self, prediction: list, target: int) -> list:
        n = len(prediction)
        if _argmax(prediction) == target:
            return [0] * n
        grad = [0] * n
        predicted = _argmax(prediction)
        grad[target] = 1
        grad[predicted] = -1
        return grad
