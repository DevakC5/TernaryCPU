"""ASCII visualization for ternary tensor operations."""


def render_simd_lanes(registers, lanes=4):
    """Render SIMD lanes as ASCII.

    Args:
        registers: List of trit values (length = lanes).
        lanes: Number of lanes.

    Returns:
        str: ASCII art.
    """
    lines = ["SIMD Lanes:"]
    for i in range(lanes):
        val = registers[i] if i < len(registers) else "?"
        arrow = ">" if i == 0 else " "
        signed = {-1: "-", 0: "0", 1: "+"}
        s = signed.get(val, "?")
        lines.append(f"  {arrow} Lane{i}: [{val}] ({s})")
    lines.append(f"  {'─' * (lanes * 4 + 4)}")
    return "\n".join(lines)


def render_tensor_matrix(matrix, label="Tensor"):
    """Render a 2D tensor matrix as ASCII.

    Args:
        matrix: List of lists of trit values.
        label: Optional label.

    Returns:
        str: ASCII art.
    """
    if not matrix or not matrix[0]:
        return f"{label}: []"
    rows = len(matrix)
    cols = len(matrix[0])
    lines = [f"{label} [{rows}×{cols}]:", "  ┌" + "─" * (cols * 4 + 1) + "┐"]
    for row in matrix:
        vals = " ".join(str(v) for v in row)
        lines.append(f"  │ {vals} │")
    lines.append("  └" + "─" * (cols * 4 + 1) + "┘")
    return "\n".join(lines)


def render_matmul(a, b, result=None):
    """Render matrix multiplication as ASCII.

    Args:
        a: First matrix as list of lists.
        b: Second matrix as list of lists.
        result: Optional result matrix.

    Returns:
        str: ASCII art.
    """
    lines = ["Tensor Core — Matrix Multiply:", ""]
    a_str = render_tensor_matrix(a, "A").split("\n")
    b_str = render_tensor_matrix(b, "B").split("\n")
    max_a = max(len(l) for l in a_str)
    for i in range(max(len(a_str), len(b_str))):
        left = a_str[i] if i < len(a_str) else ""
        right = b_str[i] if i < len(b_str) else ""
        sep = " × " if i == len(a_str) // 2 else "   "
        lines.append(f"  {left}{sep}{right}")
    if result is not None:
        lines.append("")
        lines.append("  =")
        lines.append("")
        res_str = render_tensor_matrix(result, "C").split("\n")
        for l in res_str:
            lines.append(f"  {l}")
    return "\n".join(lines)


def render_packed_trits(data, bytes_per_row=8):
    """Render packed trit storage as ASCII.

    Args:
        data: List of trit values.
        bytes_per_row: How many bytes to show per row.

    Returns:
        str: ASCII art.
    """
    lines = ["Packed Trit Storage:", ""]
    for i in range(0, len(data), bytes_per_row * 4):
        chunk = data[i:i + bytes_per_row * 4]
        trits = " ".join(str(v) for v in chunk)
        addr_str = f"@{i:04x}"
        lines.append(f"  {addr_str}: [{trits}]")
    return "\n".join(lines)


def render_accelerator(accel):
    """Render full accelerator state as ASCII.

    Args:
        accel: TernaryTensorAccelerator instance.

    Returns:
        str: ASCII art.
    """
    lines = ["╔══════════════════════════════════════╗"]
    lines.append("║  Ternary Tensor Accelerator State  ║")
    lines.append("╚══════════════════════════════════════╝")
    lines.append("")
    lines.append(f"  Memory:   {len(accel.memory._slots)}/{accel.memory.capacity} slots")
    total_trits = sum(len(s) for s in accel.memory._slots.values())
    lines.append(f"  Trits:    {total_trits}")
    lines.append(f"  Cycles:   {accel.cycles}")
    lines.append(f"  SIMD:     {accel.simd.lanes} lanes")
    lines.append(f"  Program:  PC={accel._program_counter}")
    lines.append("")
    if accel.memory._slots:
        lines.append("  Allocated Tensors:")
        for tid, arr in list(accel.memory._slots.items())[:4]:
            data = arr.to_list()
            shape = accel.memory.get_shape(tid)
            shape_str = f" {shape[0]}×{shape[1]}" if shape else ""
            preview = " ".join(str(v) for v in data[:6])
            if len(data) > 6:
                preview += "..."
            lines.append(f"    [{tid}]{shape_str}: [{preview}]")
        if len(accel.memory._slots) > 4:
            lines.append(f"    ... and {len(accel.memory._slots) - 4} more")
    return "\n".join(lines)


def render_pipeline(pipeline_ops):
    """Render a tensor pipeline as ASCII.

    Args:
        pipeline_ops: List of operation name strings.

    Returns:
        str: ASCII art.
    """
    lines = ["Tensor Pipeline:"]
    for i, op in enumerate(pipeline_ops):
        prefix = "┌─" if i == 0 else "├─"
        suffix = "─┐" if i == len(pipeline_ops) - 1 else "─┤"
        lines.append(f"  {prefix}{op:^10}{suffix}")
        if i < len(pipeline_ops) - 1:
            lines.append(f"  │{'─'*8}│")
    return "\n".join(lines)


def render_gpu(gpu):
    """Render full GPU architecture as ASCII.

    Args:
        gpu: TernaryGPU instance.

    Returns:
        str: ASCII art.
    """
    lines = ["╔══════════════════════════════════════════════╗"]
    lines.append("║           Ternary GPU Architecture           ║")
    lines.append("╚══════════════════════════════════════════════╝")
    lines.append("")
    lines.append(f"  Workgroups:  {len(gpu.workgroups)}")
    if gpu.workgroups:
        pes_per_wg = gpu.workgroups[0].pe_count()
        warps_per_wg = gpu.workgroups[0].num_warps()
        lines.append(f"  PEs/WG:      {pes_per_wg}")
        lines.append(f"  Warps/WG:    {warps_per_wg}")
        lines.append(f"  Warp size:   {gpu.warp_size}")
    lines.append(f"  Total PEs:   {gpu.total_pes()}")
    lines.append(f"  Total warps: {gpu.total_warps()}")
    lines.append(f"  Streams:     {len(gpu.streams)}")
    lines.append(f"  Cycles:      {gpu.cycles}")
    lines.append("")
    for wg in gpu.workgroups:
        lines.append(f"  ┌─ Workgroup {wg.wg_id} ──────────────────────")
        lines.append(f"  │ PEs: {wg.pe_count()}  Warps: {wg.num_warps()}"
                     f"  Shared mem: {len(wg.shared_mem)} trits")
        for warp in wg.warps:
            pe_ids = [pe.pe_id for pe in warp.pes]
            lines.append(f"  │  Warp{warp.warp_id}: PEs {pe_ids}"
                        f"  active={warp.active}")
        lines.append(f"  └──────────────────────────────────────")
    return "\n".join(lines)


def render_warp(warp):
    """Render a single warp's state as ASCII.

    Args:
        warp: Warp instance.

    Returns:
        str: ASCII art.
    """
    lines = [f"Warp {warp.warp_id} ({len(warp.pes)} PEs, active={warp.active}):"]
    signed = {-1: "-", 0: "0", 1: "+"}
    for pe in warp.pes:
        data = pe.local_mem.to_list() if len(pe.local_mem) > 0 else []
        result = pe.result
        data_str = " ".join(str(v) for v in data[:8])
        if len(data) > 8:
            data_str += "..."
        result_str = f"→ {result}" if result is not None else ""
        lines.append(f"  PE{pe.pe_id}: [{data_str}] {result_str}")
    return "\n".join(lines)


def render_streams(gpu):
    """Render GPU stream states as ASCII.

    Args:
        gpu: TernaryGPU instance.

    Returns:
        str: ASCII art.
    """
    if not gpu.streams:
        return "No streams configured."
    lines = ["GPU Streams:"]
    for sid, stream in gpu.streams.items():
        queued = len(stream._queue)
        completed = len(stream._completed)
        lines.append(f"  Stream {sid}: queued={queued} completed={completed}")
    return "\n".join(lines)
