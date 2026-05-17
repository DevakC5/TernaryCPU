from trinary.display import (
    DisplayMemoryMap,
    DISPLAY_START,
    DISPLAY_END,
    DISPLAY_SIZE,
)
from trinary.memory import Memory


class TestDisplayMemoryMap:
    def setup_method(self):
        self.display = DisplayMemoryMap()
        self.memory = Memory(256)

    def test_constants(self):
        assert DISPLAY_START == 200
        assert DISPLAY_END == 255
        assert DISPLAY_SIZE == 56

    def test_initial_display_is_all_spaces(self):
        chars = self.display.read_display(self.memory)
        assert len(chars) == 56
        assert all(c == " " for c in chars)

    def test_write_text_and_read(self):
        self.display.write_text(self.memory, "HI", offset=0)
        chars = self.display.read_display(self.memory)
        assert chars[0] == "H"
        assert chars[1] == "I"
        assert chars[2] == " "

    def test_write_text_with_offset(self):
        self.display.write_text(self.memory, "ABC", offset=5)
        chars = self.display.read_display(self.memory)
        assert chars[5] == "A"
        assert chars[6] == "B"
        assert chars[7] == "C"

    def test_write_text_truncated_at_end(self):
        self.display.write_text(self.memory, "X" * 60, offset=0)
        chars = self.display.read_display(self.memory)
        assert len(chars) == 56
        assert chars[55] == "X"

    def test_write_full_message(self):
        self.display.write_text(self.memory, "HELLO TERNARY VM", offset=0)
        chars = self.display.read_display(self.memory)
        assert "".join(chars[:17]).strip() == "HELLO TERNARY VM"

    def test_clear(self):
        self.display.write_text(self.memory, "SOMETHING", offset=0)
        self.display.clear(self.memory)
        chars = self.display.read_display(self.memory)
        assert all(c == " " for c in chars)

    def test_clear_repeated(self):
        self.display.clear(self.memory)
        chars = self.display.read_display(self.memory)
        assert all(c == " " for c in chars)

    def test_non_printable_becomes_dot(self):
        from trinary.conversion import decimal_to_ternary as d2t
        self.memory.store(DISPLAY_START, d2t(0))
        self.memory.store(DISPLAY_START + 1, d2t(7))
        self.memory.store(DISPLAY_START + 2, d2t(127))
        chars = self.display.read_display(self.memory)
        assert chars[0] == " "
        assert chars[1] == "."
        assert chars[2] == "."

    def test_roundtrip_through_memory(self):
        self.display.write_text(self.memory, "HELLO", offset=0)
        chars = self.display.read_display(self.memory)
        assert "".join(chars[:5]) == "HELLO"

    def test_write_at_various_offsets(self):
        self.display.write_text(self.memory, "A", offset=0)
        self.display.write_text(self.memory, "B", offset=10)
        self.display.write_text(self.memory, "C", offset=55)
        chars = self.display.read_display(self.memory)
        assert chars[0] == "A"
        assert chars[10] == "B"
        assert chars[55] == "C"


class TestDisplayWithCPU:
    def test_cpu_storem_and_loadm_exist(self):
        from trinary.cpu import CPU
        cpu = CPU()
        assert "STOREM" in cpu.OPCODES
        assert "LOADM" in cpu.OPCODES

    def test_cpu_writes_to_display_memory(self):
        from trinary.cpu import CPU
        cpu = CPU()
        cpu.load_program([
            "LOAD R0 2200",   # ASCII 'H' = 72 = ternary 2200
            "STOREM 200 R0",
            "HALT",
        ])
        cpu.run(verbose=False)
        from trinary.conversion import ternary_to_decimal
        val = cpu.memory.load(200)
        assert ternary_to_decimal(val) == ord("H")

    def test_cpu_reads_from_display_memory(self):
        from trinary.cpu import CPU
        from trinary.conversion import decimal_to_ternary
        cpu = CPU()
        cpu.memory.store(200, decimal_to_ternary(ord("Z")))
        cpu.load_program([
            "LOADM 200 R1",
            "HALT",
        ])
        cpu.run(verbose=False)
        from trinary.conversion import ternary_to_decimal
        assert ternary_to_decimal(cpu.registers.store("R1")) == ord("Z")

    def test_cpu_display_demo_end_to_end(self):
        from trinary.cpu import CPU
        from trinary.assembler import Assembler
        from trinary.ui.demos import DEMOS

        asm = Assembler()
        source = DEMOS["Hello Display"]
        program, labels = asm.assemble(source)
        cpu = CPU()
        cpu.load_program(program)
        cpu.run(verbose=False)

        display = DisplayMemoryMap()
        chars = display.read_display(cpu.memory)
        rendered = "".join(chars[:17]).strip()
        assert rendered == "HELLO TERNARY VM"
