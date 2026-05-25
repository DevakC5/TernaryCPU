"""Tests for branch predictor."""

import pytest
from trinary.hardware.branch_predictor import BranchPredictor


class TestBranchPredictor:
    def test_always_taken(self):
        bp = BranchPredictor(mode='always_taken')
        assert bp.predict(0)
        assert bp.predict(100)

    def test_always_not_taken(self):
        bp = BranchPredictor(mode='always_not_taken')
        assert not bp.predict(0)

    def test_two_bit_initial_predict_taken(self):
        bp = BranchPredictor(mode='two_bit')
        assert bp.predict(0)

    def test_two_bit_update_not_taken(self):
        bp = BranchPredictor(mode='two_bit')
        bp.predict(0)
        bp.update(0, False)
        assert bp.mispredictions == 0

    def test_two_bit_becomes_not_taken(self):
        bp = BranchPredictor(mode='two_bit')
        for _ in range(3):
            bp.update(0, False)
        assert not bp.predict(0)

    def test_accuracy(self):
        bp = BranchPredictor(mode='always_taken')
        bp.predict(0)
        bp.record_mispredict()
        assert bp.accuracy < 1.0

    def test_reset(self):
        bp = BranchPredictor(mode='two_bit')
        bp.predict(0)
        bp.record_mispredict()
        bp.reset()
        assert bp.predictions == 0
        assert bp.accuracy == 1.0

    def test_stats(self):
        bp = BranchPredictor(mode='two_bit')
        stats = bp.stats()
        assert stats["mode"] == "two_bit"
        assert "accuracy" in stats
