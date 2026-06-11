"""Debug: test AND (linearly separable) then XOR with more epochs."""

from trinary.ai2.trit_module import TritLinear, TritSequential
from trinary.ai2.trit_loss import TritCrossEntropyLoss
from trinary.ai2.trit_trainer import TritTrainer

def make_and_dataset():
    """AND: target=1 only when both inputs are +1."""
    return [
        ([0, 0], 0),   # -1 AND -1 = -1 → 0
        ([0, 2], 0),   # -1 AND +1 = -1 → 0
        ([2, 0], 0),   # +1 AND -1 = -1 → 0
        ([2, 2], 1),   # +1 AND +1 = +1 → 1
    ]

def make_or_dataset():
    """OR: target=1 when either input is +1."""
    return [
        ([0, 0], 0),   # -1 OR -1 = -1 → 0
        ([0, 2], 1),   # -1 OR +1 = +1 → 1
        ([2, 0], 1),   # +1 OR -1 = +1 → 1
        ([2, 2], 1),   # +1 OR +1 = +1 → 1
    ]

def make_xor_dataset():
    return [
        ([0, 0], 0),
        ([0, 2], 1),
        ([2, 0], 1),
        ([2, 2], 0),
    ]

def train_and_eval(name, dataset, epochs=100, hidden=4):
    print(f"\n{'='*50}")
    print(f"{name} ({len(dataset)} examples, {epochs} epochs)")
    model = TritSequential(
        TritLinear(2, hidden, bias=True, seed=0),
        TritLinear(hidden, 2, bias=True, seed=1),
    )
    criterion = TritCrossEntropyLoss()
    trainer = TritTrainer(model, criterion)
    acc_before = trainer.evaluate(dataset)
    history = trainer.train(dataset, epochs=epochs, verbose=True)
    acc_after = trainer.evaluate(dataset)
    print(f"  Accuracy: {acc_before:.0%} → {acc_after:.0%}")
    return acc_after, history

# Test AND (linearly separable)
train_and_eval("AND", make_and_dataset(), epochs=200, hidden=2)

# Test OR (linearly separable)
train_and_eval("OR", make_or_dataset(), epochs=200, hidden=2)

# Test XOR with small and large hidden layer
train_and_eval("XOR hidden=4", make_xor_dataset(), epochs=500, hidden=4)
train_and_eval("XOR hidden=8", make_xor_dataset(), epochs=500, hidden=8)
train_and_eval("XOR hidden=16", make_xor_dataset(), epochs=500, hidden=16)
