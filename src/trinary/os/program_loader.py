from trinary.assembler import Assembler


class ProgramLoader:
    def __init__(self, memory):
        self.memory = memory
        self.asm = Assembler()
        self._programs = {}

    def register_program(self, name, source):
        program, labels = self.asm.assemble(source)
        self._programs[name.upper()] = (program, labels)

    def load(self, name):
        name = name.upper()
        entry = self._programs.get(name)
        if entry is None:
            return None
        return entry[0]

    def get_labels(self, name):
        name = name.upper()
        entry = self._programs.get(name)
        if entry is None:
            return {}
        return entry[1]

    def list_programs(self):
        return list(self._programs.keys())
