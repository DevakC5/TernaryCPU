"""TritModule + Autograd — reimagined trinary AI architecture.

Trit-native computation graph with LUT-based arithmetic,
tape-based autograd, and trit-only weight updates.

Key classes:
    TritLinear, TritSequential, TritTanh        — building blocks
    TritTape                                     — autograd recording
    TritMSELoss, TritCrossEntropyLoss           — loss functions
    TritTrainer                                  — gradient descent trainer
"""

from trinary.ai2.trit_math import (
    TRIT_ADD, TRIT_MUL, DOT_TERM,
    ternary_step, trit_dot, trit_matmul, trit_linear, trit_add_trit,
)
from trinary.ai2.trit_module import TritModule, TritLinear, TritLinearMixed, TritSequential, TritTanh
from trinary.ai2.trit_graph import TritTape
from trinary.ai2.trit_loss import TritMSELoss, TritCrossEntropyLoss
from trinary.ai2.trit_trainer import TritTrainer, TritTrainerMixed

__all__ = [
    'TRIT_ADD', 'TRIT_MUL', 'DOT_TERM',
    'ternary_step', 'trit_dot', 'trit_matmul', 'trit_linear', 'trit_add_trit',
    'TritModule', 'TritLinear', 'TritLinearMixed', 'TritSequential', 'TritTanh',
    'TritTape',
    'TritMSELoss', 'TritCrossEntropyLoss',
    'TritTrainer', 'TritTrainerMixed',
]
