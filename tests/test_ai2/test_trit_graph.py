"""Tests for trit_graph.py — TritTape autograd."""

import pytest
from trinary.ai2.trit_module import TritModule, TritLinear, TritSequential
from trinary.ai2.trit_graph import TritTape
from trinary.ai2.trit_loss import TritMSELoss, TritCrossEntropyLoss


class TestTritTapeBasic:
    def test_records_linear_forward(self):
        mod = TritLinear(2, 2, bias=False, seed=0)
        with TritTape() as tape:
            out = mod([2, 0])
        assert len(tape._records) == 1
        mod_rec, args, out_rec = tape._records[0]
        assert mod_rec is mod
        assert args[0] == [2, 0]
        assert out_rec == out

    def test_backward_returns_dict(self):
        mod = TritLinear(2, 2, bias=True, seed=0)
        with TritTape() as tape:
            out = mod([2, 0])
        grads = tape.backward()
        assert isinstance(grads, dict)
        assert len(grads) > 0

    def test_backward_weight_shape(self):
        mod = TritLinear(2, 3, bias=True, seed=0)
        with TritTape() as tape:
            out = mod([2, 0])
        grads = tape.backward()
        assert len(grads['weight']) == 2 * 3

    def test_backward_bias_shape(self):
        mod = TritLinear(3, 4, bias=True, seed=0)
        with TritTape() as tape:
            out = mod([2, 0, 1])
        grads = tape.backward()
        assert len(grads['bias']) == 4

    def test_no_bias(self):
        mod = TritLinear(2, 2, bias=False, seed=0)
        with TritTape() as tape:
            out = mod([2, 0])
        grads = tape.backward()
        assert 'bias' not in grads

    def test_gradients_are_trits(self):
        mod = TritLinear(2, 2, bias=True, seed=0)
        with TritTape() as tape:
            out = mod([2, 0])
        grads = tape.backward()
        for g in grads.values():
            for v in g:
                assert v in (0, 1, 2), f"gradient value {v} not a trit"

    def test_multiple_layers(self):
        mod = TritSequential(
            TritLinear(2, 3, bias=True, seed=0),
            TritLinear(3, 2, bias=True, seed=1),
        )
        with TritTape() as tape:
            out = mod([2, 0])
        grads = tape.backward()
        assert '0.weight' in grads or 'weight' in grads
        assert '1.weight' in grads or 'weight' in grads

    def test_empty_records(self):
        tape = TritTape()
        grads = tape.backward()
        assert grads == {}


class TestTritTapeWithLoss:
    def test_mse_loss_gradient(self):
        mod = TritLinear(2, 2, bias=True, seed=0)
        criterion = TritMSELoss()
        with TritTape() as tape:
            out = mod([2, 0])
            loss = criterion(out, [2, 0])
        grads = tape.backward()
        assert len(grads) > 0
        assert loss[0] in (0, 1, 2)

    def test_cross_entropy_gradient(self):
        mod = TritSequential(
            TritLinear(2, 3, bias=True, seed=0),
            TritLinear(3, 2, bias=True, seed=1),
        )
        criterion = TritCrossEntropyLoss()
        with TritTape() as tape:
            out = mod([2, 0])
            loss = criterion(out, 0)
        grads = tape.backward()
        assert len(grads) > 0

    def test_tape_clears_on_reentry(self):
        mod = TritLinear(2, 2, seed=0)
        with TritTape() as tape:
            mod([2, 0])
        n1 = len(tape._records)
        with TritTape() as tape2:
            mod([0, 2])
        assert len(tape2._records) == 1
