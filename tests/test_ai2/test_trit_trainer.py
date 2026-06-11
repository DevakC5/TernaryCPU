"""Tests for trit_trainer.py — TritTrainer with SGD."""

import pytest
from trinary.ai2.trit_module import TritLinear, TritSequential
from trinary.ai2.trit_loss import TritMSELoss, TritCrossEntropyLoss
from trinary.ai2.trit_trainer import TritTrainer
from trinary.ai2.trit_math import TRIT_ADD


def make_xor_dataset():
    """XOR problem: 4 patterns with 2 outputs."""
    return [
        ([2, 2], [0, 2]),   # 0 XOR 0 = 0 → [-1, +1] → target [0, 2]
        ([2, 0], [2, 0]),   # 0 XOR 1 = 1 → [+1, -1] → target [2, 0]
        ([0, 2], [2, 0]),   # 1 XOR 0 = 1 → [+1, -1] → target [2, 0]
        ([0, 0], [0, 2]),   # 1 XOR 1 = 0 → [-1, +1] → target [0, 2]
    ]


class TestTritTrainer:
    def test_train_step(self):
        model = TritLinear(2, 2, bias=True, seed=0)
        criterion = TritMSELoss()
        trainer = TritTrainer(model, criterion)
        loss = trainer.train_step([2, 0], [2, 0])
        assert loss in (0, 1, 2)

    def test_apply_gradients_changes_params(self):
        model = TritLinear(2, 2, bias=True, seed=0)
        w_before = list(model._params['weight'])
        b_before = list(model._params['bias'])

        from trinary.ai2.trit_graph import TritTape
        criterion = TritMSELoss()
        with TritTape() as tape:
            out = model([2, 0])
            loss = criterion(out, [2, 2])
        grads = tape.backward()
        trainer = TritTrainer(model, criterion)
        trainer.apply_gradients(grads)

        # Parameters should have changed (at least some)
        w_after = model._params['weight']
        changed = sum(1 for a, b in zip(w_before, w_after) if a != b)
        assert changed > 0, "parameters didn't change after gradient update"

    def test_evaluate(self):
        model = TritLinear(2, 2, bias=True, seed=0)
        criterion = TritMSELoss()
        trainer = TritTrainer(model, criterion)
        acc = trainer.evaluate(make_xor_dataset()[:2])
        assert 0.0 <= acc <= 1.0

    def test_compute_accuracy_mse(self):
        model = TritLinear(2, 2, bias=True, seed=42)
        model._params['weight'] = [2, 0, 0, 2]
        model._params['bias'] = [0, 2]
        trainer = TritTrainer(model, TritMSELoss())
        acc = trainer.compute_accuracy([2, 0], [2, 0])
        assert 0.0 <= acc <= 1.0

    def test_train_epoch(self):
        model = TritLinear(3, 2, bias=True, seed=0)
        criterion = TritMSELoss()
        trainer = TritTrainer(model, criterion)
        dataset = [([2, 1, 0], [2, 0]), ([0, 1, 2], [0, 2])]
        history = trainer.train(dataset, epochs=5, verbose=False)
        assert 'loss' in history
        assert 'accuracy' in history
        assert len(history['loss']) == 5

    def test_train_with_cross_entropy(self):
        model = TritSequential(
            TritLinear(2, 4, bias=True, seed=0),
            TritLinear(4, 2, bias=True, seed=1),
        )
        criterion = TritCrossEntropyLoss()
        trainer = TritTrainer(model, criterion)
        dataset = [([2, 0], 0), ([0, 2], 1)]
        history = trainer.train(dataset, epochs=3, verbose=False)
        assert len(history['loss']) == 3


def test_sgd_update_rule():
    """Verify SGD update uses TRIT_ADD correctly."""
    w = [1, 0, 2, 1]  # some weight
    g = [2, 0, 0, 2]  # some gradient trits
    w_new = [TRIT_ADD[w[i]][g[i]] for i in range(len(w))]
    assert all(v in (0, 1, 2) for v in w_new)
