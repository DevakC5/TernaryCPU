"""5-Stage pipeline with IF→ID→EX→MEM→WB stages.

Supports:
- Stage-by-stage instruction advancement
- Bubble insertion (stalls, NOPs)
- Pipeline flushing (branch mispredicts)
- Visualizable stage state
"""


class PipelineStage:
    def __init__(self, name):
        self.name = name
        self.instruction = None
        self.opcode = None
        self.operands = []
        self.bubble = True
        self.cycles_remaining = 1

    def insert(self, instruction, opcode=None, operands=None, cycles=1):
        self.instruction = instruction
        self.opcode = opcode
        self.operands = operands or []
        self.bubble = False
        self.cycles_remaining = cycles

    def insert_bubble(self):
        self.instruction = None
        self.opcode = None
        self.operands = []
        self.bubble = True
        self.cycles_remaining = 0

    def tick(self):
        if self.cycles_remaining > 0:
            self.cycles_remaining -= 1
        return self.cycles_remaining == 0 and not self.bubble

    @property
    def stalled(self):
        return self.cycles_remaining > 0 and not self.bubble

    def __repr__(self):
        if self.bubble:
            return f"[{self.name}: ---]"
        return f"[{self.name}: {self.opcode} {' '.join(self.operands)}]"


class Pipeline:
    """5-stage pipeline: IF → ID → EX → MEM → WB."""

    def __init__(self):
        self.if_stage = PipelineStage("IF")
        self.id_stage = PipelineStage("ID")
        self.ex_stage = PipelineStage("EX")
        self.mem_stage = PipelineStage("MEM")
        self.wb_stage = PipelineStage("WB")
        self.total_instructions = 0
        self.stall_cycles = 0
        self.flush_count = 0

    @property
    def stages(self):
        return [self.if_stage, self.id_stage, self.ex_stage, self.mem_stage, self.wb_stage]

    def advance(self):
        """Advance all pipeline stages by one cycle.

        Returns:
            str: Opcode that completed WB this cycle, or None.
        """
        completed = None
        if not self.wb_stage.bubble and self.wb_stage.tick():
            completed = self.wb_stage.opcode
            self.wb_stage.insert_bubble()
            self.total_instructions += 1
        if not self.mem_stage.bubble and self.mem_stage.tick():
            self.wb_stage.insert(self.mem_stage.instruction,
                                 self.mem_stage.opcode,
                                 self.mem_stage.operands)
            self.mem_stage.insert_bubble()
        else:
            self.wb_stage.insert_bubble()
        if not self.ex_stage.bubble and self.ex_stage.tick():
            self.mem_stage.insert(self.ex_stage.instruction,
                                  self.ex_stage.opcode,
                                  self.ex_stage.operands)
            self.ex_stage.insert_bubble()
        else:
            self.mem_stage.insert_bubble()
        if not self.id_stage.bubble and self.id_stage.tick():
            self.ex_stage.insert(self.id_stage.instruction,
                                 self.id_stage.opcode,
                                 self.id_stage.operands)
            self.id_stage.insert_bubble()
        else:
            self.ex_stage.insert_bubble()
        if not self.if_stage.bubble and self.if_stage.tick():
            self.id_stage.insert(self.if_stage.instruction,
                                 self.if_stage.opcode,
                                 self.if_stage.operands)
            self.if_stage.insert_bubble()
        else:
            self.id_stage.insert_bubble()
        self.if_stage.insert_bubble()
        return completed

    def fetch(self, instruction, opcode=None, operands=None, cycles=1):
        """Insert instruction into IF stage (fetch)."""
        self.if_stage.insert(instruction, opcode, operands, cycles)

    def stall(self):
        """Insert a bubble in IF (stall pipeline front)."""
        self.if_stage.insert_bubble()
        self.stall_cycles += 1

    def flush(self):
        """Flush IF, ID, EX stages (branch mispredict)."""
        self.if_stage.insert_bubble()
        self.id_stage.insert_bubble()
        self.ex_stage.insert_bubble()
        self.flush_count += 1

    @property
    def occupancy(self):
        return sum(1 for s in self.stages if not s.bubble)

    @property
    def busy(self):
        return any(not s.bubble for s in self.stages)

    def reset(self):
        for s in self.stages:
            s.insert_bubble()
        self.total_instructions = 0
        self.stall_cycles = 0
        self.flush_count = 0

    def stats(self):
        return {
            "total_instructions": self.total_instructions,
            "stall_cycles": self.stall_cycles,
            "flush_count": self.flush_count,
            "occupancy": self.occupancy,
        }

    def visualize(self, cycle=None):
        """Render pipeline state as ASCII."""
        lines = []
        if cycle is not None:
            lines.append(f"Cycle {cycle:>4} | {'IF':<8} | {'ID':<8} | {'EX':<8} | {'MEM':<8} | {'WB':<8}")
            lines.append("-" * 55)
        stage_names = ["IF", "ID", "EX", "MEM", "WB"]
        stages = self.stages
        parts = []
        for s in stages:
            if s.bubble:
                parts.append("---".center(8))
            else:
                label = s.opcode or "???"
                if s.stalled:
                    label += "*"
                parts.append(label.center(8))
        lines.append(f"       | {' | '.join(parts)}")
        return "\n".join(lines)
