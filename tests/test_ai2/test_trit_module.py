"""Tests for trit_module.py — TritModule, TritLinear, TritSequential."""

import pytest
from trinary.ai2.trit_module import TritModule, TritLinear, TritSequential, TritTanh


class TestTritLinear:
    def test_forward_output(self):
        mod = TritLinear(3, 2, bias=True, seed=0)
        out = mod([2, 1, 0])
        assert len(out) == 2
        assert all(v in (0, 1, 2) for v in out)

    def test_no_bias(self):
        mod = TritLinear(2, 4, bias=False, seed=1)
        out = mod([2, 0])
        assert len(out) == 4

    def test_parameters(self):
        mod = TritLinear(3, 2, bias=True, seed=0)
        params = mod.parameters()
        assert 'weight' in params
        assert 'bias' in params
        assert len(params['weight']) == 2 * 3

    def test_forward_raw(self):
        mod = TritLinear(3, 2, bias=False, seed=0)
        raw = mod.forward_raw([2, 1, 0])
        assert len(raw) == 2

    def test_repr(self):
        mod = TritLinear(3, 5)
        assert 'TritLinear' in repr(mod)
        assert '3' in repr(mod)


class TestTritSequential:
    def test_chain(self):
        mod = TritSequential(
            TritLinear(2, 3, bias=True, seed=0),
            TritLinear(3, 2, bias=True, seed=1),
        )
        out = mod([2, 0])
        assert len(out) == 2
        assert all(v in (0, 1, 2) for v in out)

    def test_parameters_recursive(self):
        mod = TritSequential(
            TritLinear(2, 3, bias=True, seed=0),
            TritLinear(3, 2, bias=False, seed=1),
        )
        params = mod.parameters()
        assert '0.weight' in params
        assert '0.bias' in params
        assert '1.weight' in params
        assert '1.bias' not in params

    def test_named_modules(self):
        mod = TritSequential(
            TritLinear(2, 3, seed=0),
        )
        names = [name for name, _ in mod.named_modules()]
        assert '0' in names
        assert '' in names

    def test_repr(self):
        mod = TritSequential(TritLinear(2, 3))
        assert 'TritSequential' in repr(mod)


class TestTritTanh:
    def test_forward(self):
        tanh = TritTanh()
        out = tanh([0, 1, 2])
        assert all(v in (0, 1, 2) for v in out)
