from trinary.assembler import Assembler


class TestAssembler:
    def test_no_labels(self):
        asm = Assembler()
        prog, labels = asm.assemble("LOAD R0 10\nHALT")
        assert prog == ["LOAD R0 10", "HALT"]
        assert labels == {}

    def test_label_resolution(self):
        asm = Assembler()
        source = """
start:
    LOAD R0 10
    JMP done
done:
    HALT
"""
        prog, labels = asm.assemble(source)
        assert labels == {"start": 0, "done": 2}
        assert prog == ["LOAD R0 10", "JMP 2", "HALT"]

    def test_comment_lines(self):
        asm = Assembler()
        source = "# comment\nLOAD R0 10\n# another\nHALT"
        prog, labels = asm.assemble(source)
        assert prog == ["LOAD R0 10", "HALT"]

    def test_inline_comments(self):
        asm = Assembler()
        source = "LOAD R0 10  # load value\nADD R0 R0  # double\nHALT"
        prog, labels = asm.assemble(source)
        assert prog == ["LOAD R0 10", "ADD R0 R0", "HALT"]

    def test_label_with_comment(self):
        asm = Assembler()
        source = """
start:  # entry point
    LOAD R0 1
    HALT  # stop
"""
        prog, labels = asm.assemble(source)
        assert labels == {"start": 0}
        assert prog == ["LOAD R0 1", "HALT"]
