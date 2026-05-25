from trinary.display import (
    DisplayMemoryMap,
    PixelDisplay,
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

    def test_hello_ternary_demo(self):
        from trinary.cpu import CPU
        from trinary.assembler import Assembler
        from trinary.ui.demos import DEMOS
        asm = Assembler()
        source = DEMOS["HELLO TERNARY"]
        program, labels = asm.assemble(source)
        cpu = CPU()
        cpu.load_program(program)
        cpu.run(verbose=False)
        display = DisplayMemoryMap()
        chars = display.read_display(cpu.memory)
        rendered = "".join(chars[:13]).strip()
        assert rendered == "HELLO TERNARY"

class TestPixelDisplay:
    def setup_method(self):
        self.pd = PixelDisplay()

    def test_buffer_size(self):
        assert len(self.pd.get_buffer()) == 27
        for row in self.pd.get_buffer():
            assert len(row) == 27

    def test_initial_all_black(self):
        for y in range(27):
            for x in range(27):
                assert self.pd.get_pixel(x, y) == 0

    def test_set_and_get_pixel(self):
        self.pd.set_pixel(13, 13, 2)
        assert self.pd.get_pixel(13, 13) == 2
        assert self.pd.get_pixel(0, 0) == 0

    def test_set_pixel_clamps_bounds(self):
        self.pd.set_pixel(-1, 0, 2)
        self.pd.set_pixel(0, -1, 2)
        self.pd.set_pixel(27, 0, 2)
        self.pd.set_pixel(0, 27, 2)
        for y in range(27):
            for x in range(27):
                assert self.pd.get_pixel(x, y) == 0

    def test_set_pixel_invalid_color(self):
        self.pd.set_pixel(0, 0, 3)
        assert self.pd.get_pixel(0, 0) == 0
        self.pd.set_pixel(0, 0, -1)
        assert self.pd.get_pixel(0, 0) == 0
        self.pd.set_pixel(0, 0, 1)
        assert self.pd.get_pixel(0, 0) == 1

    def test_clear(self):
        self.pd.set_pixel(0, 0, 2)
        self.pd.set_pixel(26, 26, 1)
        self.pd.clear()
        for y in range(27):
            for x in range(27):
                assert self.pd.get_pixel(x, y) == 0

    def test_draw_line_horizontal(self):
        self.pd.draw_line(0, 13, 26, 13, 2)
        for x in range(27):
            assert self.pd.get_pixel(x, 13) == 2
        assert self.pd.get_pixel(0, 12) == 0
        assert self.pd.get_pixel(0, 14) == 0

    def test_draw_line_vertical(self):
        self.pd.draw_line(13, 0, 13, 26, 2)
        for y in range(27):
            assert self.pd.get_pixel(13, y) == 2

    def test_draw_line_diagonal(self):
        self.pd.draw_line(0, 0, 26, 26, 2)
        for i in range(27):
            assert self.pd.get_pixel(i, i) == 2

    def test_draw_line_reverse(self):
        self.pd.draw_line(26, 26, 0, 0, 2)
        for i in range(27):
            assert self.pd.get_pixel(i, i) == 2

    def test_demo_diagonal(self):
        from trinary.demo_programs import demo_pixel_diagonal
        p = demo_pixel_diagonal()
        assert p.get_pixel(0, 0) == 2
        assert p.get_pixel(26, 26) == 2
        assert p.get_pixel(26, 0) == 1
        assert p.get_pixel(0, 26) == 1

    def test_demo_checkerboard(self):
        from trinary.demo_programs import demo_pixel_checkerboard
        p = demo_pixel_checkerboard()
        assert p.get_pixel(0, 0) == 1
        assert p.get_pixel(3, 0) == 0
        assert p.get_pixel(0, 3) == 0
        assert p.get_pixel(3, 3) == 1

    def test_demo_smiley(self):
        from trinary.demo_programs import demo_pixel_smiley
        p = demo_pixel_smiley()
        assert p.get_pixel(8, 8) == 2
        assert p.get_pixel(18, 8) == 2
        assert p.get_pixel(13, 19) == 2

    def test_keyboard_buffer_address(self):
        from trinary.cpu import CPU
        from trinary.conversion import decimal_to_ternary as d2t
        cpu = CPU()
        assert cpu.memory.size > 260
        cpu.memory.store(260, d2t(65))
        assert cpu.memory.load(260) == d2t(65)

    def test_cpu_reads_keyboard_via_loadm(self):
        from trinary.cpu import CPU
        from trinary.conversion import decimal_to_ternary as d2t, ternary_to_decimal as t2d
        cpu = CPU()
        cpu.memory.store(260, d2t(65))
        cpu.load_program(["LOADM 260 R0", "HALT"])
        cpu.run(verbose=False)
        assert t2d(cpu.registers.store("R0")) == 65

    def test_keyboard_echo_via_program(self):
        from trinary.cpu import CPU
        from trinary.assembler import Assembler
        from trinary.conversion import decimal_to_ternary as d2t, ternary_to_decimal as t2d
        cpu = CPU()
        source = """
start:
    LOAD R0 21102     # ternary 21102 = decimal 200 (VRAM start)
    LOAD R2 1
loop:
    LOADM 260 R1
    LOAD R3 0
    CMP R1 R3
    JZ loop
    STOREM R0 R1
    CLR R1
    STOREM 260 R1
    HALT
"""
        asm = Assembler()
        program, labels = asm.assemble(source)
        cpu.load_program(program)
        cpu.memory.store(260, d2t(65))
        cpu.run(verbose=False)
        stored = cpu.memory.load(200)
        assert t2d(stored) == 65
        assert cpu.memory.load(260) == d2t(0)

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
