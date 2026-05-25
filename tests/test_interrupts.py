"""Tests for interrupt controller."""

import pytest
from trinary.hardware.interrupts import InterruptController


class TestInterruptController:
    def test_create(self):
        ic = InterruptController()
        assert ic.num_lines == 8

    def test_request_and_acknowledge(self):
        ic = InterruptController()
        ic.request(0)
        irq = ic.acknowledge()
        assert irq == 0

    def test_priority(self):
        ic = InterruptController()
        ic.request(3)
        ic.request(0)
        irq = ic.acknowledge()
        assert irq == 0

    def test_masked_interrupt_not_acknowledged(self):
        ic = InterruptController()
        ic.mask(1)
        ic.request(1)
        irq = ic.acknowledge()
        assert irq is None

    def test_global_mask(self):
        ic = InterruptController()
        ic.global_mask = True
        ic.request(0)
        irq = ic.acknowledge()
        assert irq is None

    def test_eoi_clears_isr(self):
        ic = InterruptController()
        ic.request(0)
        ic.acknowledge()
        assert ic._in_isr
        ic.eoi()
        assert not ic._in_isr

    def test_multiple_pending(self):
        ic = InterruptController()
        ic.request(0)
        ic.request(1)
        assert ic.pending_count == 2

    def test_reset(self):
        ic = InterruptController()
        ic.request(0)
        ic.acknowledge()
        ic.reset()
        assert ic.pending_count == 0
        assert not ic._in_isr
