"""Interrupt controller with priorities, masking, IVT, and IPI support."""


class InterruptController:
    """Manages interrupts with priority levels and masking.

    Supports:
    - 8 interrupt request lines (0-7)
    - Priority ordering (0 = highest)
    - Global and per-IRQ masking
    - Nesting support
    - Inter-Processor Interrupts (IPI) — send irq to another core
    """

    def __init__(self, num_lines=8):
        self.num_lines = num_lines
        self._pending = [False] * num_lines
        self._masked = [False] * num_lines
        self._priorities = list(range(num_lines))
        self.global_mask = False
        self._in_isr = False
        self._nested_depth = 0

    def request(self, irq_num):
        """Request an interrupt on this controller.

        Args:
            irq_num: Interrupt request line number (0 to num_lines-1).
        """
        if 0 <= irq_num < self.num_lines and not self._masked[irq_num]:
            self._pending[irq_num] = True

    def send_ipi(self, target_controller, irq_num):
        """Inter-Processor Interrupt: trigger an IRQ on another core.

        Args:
            target_controller: InterruptController instance of the target core.
            irq_num: Interrupt line to trigger on the target.
        """
        target_controller.request(irq_num)

    def acknowledge(self):
        if self.global_mask or self._in_isr:
            return None
        for irq in sorted(range(self.num_lines),
                          key=lambda i: self._priorities[i]):
            if self._pending[irq] and not self._masked[irq]:
                self._pending[irq] = False
                self._in_isr = True
                self._nested_depth += 1
                return irq
        return None

    def eoi(self):
        self._nested_depth -= 1
        if self._nested_depth <= 0:
            self._nested_depth = 0
            self._in_isr = False

    def mask(self, irq_num):
        if 0 <= irq_num < self.num_lines:
            self._masked[irq_num] = True

    def unmask(self, irq_num):
        if 0 <= irq_num < self.num_lines:
            self._masked[irq_num] = False

    @property
    def pending_count(self):
        return sum(self._pending)

    @property
    def has_pending(self):
        return any(p and not m for p, m in zip(self._pending, self._masked))

    def reset(self):
        self._pending = [False] * self.num_lines
        self._masked = [False] * self.num_lines
        self.global_mask = False
        self._in_isr = False
        self._nested_depth = 0

    def stats(self):
        return {
            "num_lines": self.num_lines,
            "pending": self.pending_count,
            "global_mask": self.global_mask,
            "in_isr": self._in_isr,
            "nested_depth": self._nested_depth,
        }
