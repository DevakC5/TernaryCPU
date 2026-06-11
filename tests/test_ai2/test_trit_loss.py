"""Tests for trit_loss.py — TritMSELoss, TritCrossEntropyLoss."""

import pytest
from trinary.ai2.trit_loss import TritMSELoss, TritCrossEntropyLoss, _argmax


class TestArgmax:
    def test_basic(self):
        assert _argmax([2, 0, 1]) == 0
        assert _argmax([0, 2, 1]) == 1
        assert _argmax([0, 1, 2]) == 2

    def test_ties(self):
        assert _argmax([2, 2, 0]) == 0  # first is returned


class TestTritMSELoss:
    def test_forward_output(self):
        criterion = TritMSELoss()
        loss = criterion([2, 0], [2, 0])
        assert loss[0] in (0, 1, 2)

    def test_gradient_length(self):
        criterion = TritMSELoss()
        grad = criterion.gradient([2, 0, 1], [0, 2, 1])
        assert len(grad) == 3
        assert all(g in (-1, 0, 1) for g in grad)

    def test_zero_gradient_when_equal(self):
        criterion = TritMSELoss()
        grad = criterion.gradient([2, 0], [2, 0])
        assert grad == [0, 0]

    def test_gradient_sign(self):
        criterion = TritMSELoss()
        grad = criterion.gradient([2, 0], [0, 2])
        # pred[0]=+(+1), target[0]=0(-1): diff=+2 → grad=+1
        # pred[1]=0(-1), target[1]=2(+1): diff=-2 → grad=-1
        assert grad[0] == 1
        assert grad[1] == -1


class TestTritCrossEntropyLoss:
    def test_forward_correct(self):
        criterion = TritCrossEntropyLoss()
        loss = criterion([2, 0, 1], 0)
        assert loss[0] == 1  # correct, loss is 1 (neutral trit)

    def test_forward_incorrect(self):
        criterion = TritCrossEntropyLoss()
        loss = criterion([0, 2, 0], 0)
        assert loss[0] == 0  # wrong, loss is 0 (negative)

    def test_gradient_correct(self):
        criterion = TritCrossEntropyLoss()
        grad = criterion.gradient([2, 0, 0], 0)
        assert grad == [0, 0, 0]  # correct → no gradient

    def test_gradient_incorrect(self):
        criterion = TritCrossEntropyLoss()
        # pred argmax = 1, target = 0
        grad = criterion.gradient([0, 2, 0], 0)
        assert grad[0] == 1   # push target class up
        assert grad[1] == -1  # pull wrong class down
        assert grad[2] == 0

    def test_repr(self):
        assert 'TritMSELoss' in repr(TritMSELoss())
        assert 'TritCrossEntropyLoss' in repr(TritCrossEntropyLoss())
