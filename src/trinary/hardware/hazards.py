"""Hazard detection and forwarding for the 5-stage pipeline."""


class HazardUnit:
    """Detects RAW hazards and inserts stalls or forwards.

    Tracks:
    - Which registers are being written by which pipeline stage
    - Which registers are needed by which stage
    """

    FORWARD_EX_TO_EX = 1
    FORWARD_MEM_TO_EX = 2
    FORWARD_WB_TO_EX = 3
    STALL = 4

    def __init__(self):
        self.stalls_inserted = 0
        self.forwards_detected = 0

    def detect_raw(self, ex_reg_write, mem_reg_write, wb_reg_write,
                   id_reg_read1, id_reg_read2):
        """Detect RAW hazard between execute stage and ID stage.

        Args:
            ex_reg_write: Register being written by EX stage (or None).
            mem_reg_write: Register being written by MEM stage (or None).
            wb_reg_write: Register being written by WB stage (or None).
            id_reg_read1: Register read by current instruction (or None).
            id_reg_read2: Second register read (or None).

        Returns:
            int: FORWARD_* constant or STALL.
        """
        if ex_reg_write is not None and (ex_reg_write == id_reg_read1 or ex_reg_write == id_reg_read2):
            self.forwards_detected += 1
            return self.FORWARD_EX_TO_EX
        if mem_reg_write is not None and (mem_reg_write == id_reg_read1 or mem_reg_write == id_reg_read2):
            self.forwards_detected += 1
            return self.FORWARD_MEM_TO_EX
        if wb_reg_write is not None and (wb_reg_write == id_reg_read1 or wb_reg_write == id_reg_read2):
            self.forwards_detected += 1
            return self.FORWARD_WB_TO_EX
        return None

    def need_stall(self, ex_reg_write, id_reg_read1, id_reg_read2):
        """Check if a stall is needed (load-use hazard).

        A load instruction in EX means the result isn't ready
        until MEM, so the next instruction must stall.

        Args:
            ex_reg_write: Register being loaded in EX (or None).
            id_reg_read1: First register read in ID (or None).
            id_reg_read2: Second register read in ID (or None).

        Returns:
            bool: True if stall needed.
        """
        if ex_reg_write is not None and (
            ex_reg_write == id_reg_read1 or ex_reg_write == id_reg_read2
        ):
            self.stalls_inserted += 1
            return True
        return False

    def insert_bubble(self):
        self.stalls_inserted += 1

    def reset(self):
        self.stalls_inserted = 0
        self.forwards_detected = 0

    def stats(self):
        return {
            "stalls_inserted": self.stalls_inserted,
            "forwards_detected": self.forwards_detected,
        }
