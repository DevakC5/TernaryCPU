"""Train XOR with TritModule+autograd to verify end-to-end learning."""

from trinary.ai2.trit_module import TritLinear, TritSequential
from trinary.ai2.trit_loss import TritCrossEntropyLoss, TritMSELoss
from trinary.ai2.trit_trainer import TritTrainer


def make_xor_classification():
    """XOR as 2-class: target is class index 0 or 1."""
    return [
        ([0, 0], 0),   # -1 XOR -1 = -1 → class 0
        ([0, 2], 1),   # -1 XOR +1 = +1 → class 1
        ([2, 0], 1),   # +1 XOR -1 = +1 → class 1
        ([2, 2], 0),   # +1 XOR +1 = -1 → class 0
    ]


def make_xor_regression():
    """XOR as 2-output regression."""
    return [
        ([0, 0], [2, 0]),   # class 0: [+1, -1]
        ([0, 2], [0, 2]),   # class 1: [-1, +1]
        ([2, 0], [0, 2]),   # class 1: [-1, +1]
        ([2, 2], [2, 0]),   # class 0: [+1, -1]
    ]


def train_xor_classification():
    print("=== XOR Classification (CrossEntropy) ===")
    model = TritSequential(
        TritLinear(2, 4, bias=True, seed=0),
        TritLinear(4, 2, bias=True, seed=1),
    )
    criterion = TritCrossEntropyLoss()
    trainer = TritTrainer(model, criterion)
    dataset = make_xor_classification()
    print(f"Before: acc={trainer.evaluate(dataset):.2%}")
    history = trainer.train(dataset, epochs=200, verbose=True)
    final_acc = trainer.evaluate(dataset)
    print(f"After:  acc={final_acc:.2%}")
    return final_acc, history


def train_xor_regression():
    print("\n=== XOR Regression (MSE) ===")
    model = TritSequential(
        TritLinear(2, 4, bias=True, seed=0),
        TritLinear(4, 2, bias=True, seed=1),
    )
    criterion = TritMSELoss()
    trainer = TritTrainer(model, criterion)
    dataset = make_xor_regression()
    print(f"Before: acc={trainer.evaluate(dataset):.2%}")
    history = trainer.train(dataset, epochs=200, verbose=True)
    final_acc = trainer.evaluate(dataset)
    print(f"After:  acc={final_acc:.2%}")
    return final_acc, history


if __name__ == '__main__':
    acc1, h1 = train_xor_classification()
    acc2, h2 = train_xor_regression()
    print(f"\nSummary: Classification={acc1:.0%}  Regression={acc2:.0%}")
