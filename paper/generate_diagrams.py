"""Generate PDF diagrams for the Trinary paper using matplotlib."""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import os

output_dir = os.path.dirname(os.path.abspath(__file__))

def pipeline_diagram():
    """5-stage pipeline diagram."""
    fig, ax = plt.subplots(figsize=(10, 3))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 3)
    ax.axis('off')

    stages = ['IF\nFetch', 'ID\nDecode', 'EX\nExecute', 'MEM\nMemory', 'WB\nWrite\nBack']
    colors = ['#4a90d9', '#50b86c', '#e8a838', '#d9664a', '#9b59b6']
    x_positions = [0.5, 2.5, 4.5, 6.5, 8.5]

    for i, (stage, color, x) in enumerate(zip(stages, colors, x_positions)):
        rect = mpatches.FancyBboxPatch((x, 0.5), 1.8, 2.0, boxstyle="round,pad=0.15",
                                        facecolor=color, alpha=0.85, edgecolor='white', linewidth=2)
        ax.add_patch(rect)
        ax.text(x + 0.9, 1.5, stage, ha='center', va='center', fontsize=10,
                fontweight='bold', color='white')
        if i < len(stages) - 1:
            ax.annotate('', xy=(x + 2.3, 1.5), xytext=(x + 1.8, 1.5),
                       arrowprops=dict(arrowstyle='->', color='white', lw=2.5))

    ax.set_facecolor('#1a1a2e')
    fig.patch.set_facecolor('#1a1a2e')
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'pipeline.pdf'), dpi=150, bbox_inches='tight',
                facecolor=fig.get_facecolor())
    plt.close()
    print("Generated pipeline.pdf")

def memory_map_diagram():
    """Default and extended memory maps side by side."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 6))
    
    for ax, title, ranges, colors, labels in [
        (ax1, 'Default Memory Map (512 cells)',
         [(0, 128, 'Program/Data'), (128, 200, 'Stack'), (200, 256, 'VRAM Text'),
          (256, 260, 'Reserved'), (260, 261, 'Keyboard'), (261, 512, 'Available')],
         ['#4a90d9', '#e8a838', '#50b86c', '#555555', '#d9664a', '#333333'],
         None),
        (ax2, 'Extended Memory Map (10000 cells)',
         [(0, 1000, 'Program/Data/Stack'), (1000, 5096, 'Framebuffer VRAM'),
          (5096, 9000, 'Available'), (9000, 9002, 'SDK Keyboard'), (9002, 10000, 'Available')],
         ['#4a90d9', '#50b86c', '#333333', '#d9664a', '#333333'],
         None)]:
        
        total = ranges[-1][1]
        y = 0
        for (start, end, label), color in zip(ranges, colors):
            height = (end - start) / total
            ax.barh(0, height, left=y, height=0.6, color=color, edgecolor='white', linewidth=0.5)
            mid = y + height / 2
            if height > 0.04:
                ax.text(mid, 0, f'{start}-{end-1}', ha='center', va='center', fontsize=7, color='white', fontweight='bold')
                ax.text(mid, -0.5, label, ha='center', va='top', fontsize=6, color='#cccccc')
            y += height
        
        ax.set_xlim(0, 1)
        ax.set_ylim(-1, 1)
        ax.axis('off')
        ax.set_title(title, fontsize=11, fontweight='bold', color='white', pad=15)
        ax.set_facecolor('#1a1a2e')

    fig.patch.set_facecolor('#1a1a2e')
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'memory_map.pdf'), dpi=150, bbox_inches='tight',
                facecolor=fig.get_facecolor())
    plt.close()
    print("Generated memory_map.pdf")

def system_stack_diagram():
    """Full system stack diagram."""
    fig, ax = plt.subplots(figsize=(8, 8))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 12)
    ax.axis('off')

    layers = [
        (10.0, 11.5, 'APPLICATION LAYER\nOS Shell, SDK Games, User Programs', '#1a5276'),
        (8.5, 10.0, 'TAL Compiler  |  Fantasy Console SDK', '#2e86c1'),
        (7.0, 8.5, 'ASSEMBLER\nTwo-pass: labels, branch resolution', '#1f618d'),
        (5.5, 7.0, 'MACHINE CODE ENCODER/DECODER\n27 opcodes, variable-length ternary strings', '#2980b9'),
        (4.0, 5.5, 'CPU\nFetch-decode-execute, 27 opcodes, 4 regs', '#2471a3'),
        (2.5, 4.0, 'ACCELERATOR  |  HARDWARE SIM\nTensor, SIMD, GPU  |  Pipeline, Cache, BP, DMA', '#1a5276'),
        (1.0, 2.5, 'ALU  |  Registers  |  Memory  |  Display  |  Arithmetic', '#154360'),
        (0.0, 1.0, 'conversion.py  |  logic.py  |  adder.py  |  native C backend', '#0e2f44'),
    ]

    for y_bot, y_top, label, color in layers:
        rect = mpatches.FancyBboxPatch((0.5, y_bot), 9.0, y_top - y_bot - 0.1,
                                        boxstyle="round,pad=0.1",
                                        facecolor=color, edgecolor='#5dade2', linewidth=1,
                                        alpha=0.9)
        ax.add_patch(rect)
        ax.text(5.0, (y_bot + y_top) / 2, label, ha='center', va='center',
                fontsize=8, color='white', fontweight='bold')

    ax.set_facecolor('#0a0a1a')
    fig.patch.set_facecolor('#0a0a1a')
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'system_stack.pdf'), dpi=150, bbox_inches='tight',
                facecolor=fig.get_facecolor())
    plt.close()
    print("Generated system_stack.pdf")

def gpu_hierarchy_diagram():
    """GPU hierarchy: PE → Workgroup → GPU."""
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 5)
    ax.axis('off')

    # GPU box
    gpu_rect = mpatches.FancyBboxPatch((0.3, 0.3), 9.4, 4.4,
                                         boxstyle="round,pad=0.2",
                                         facecolor='#1a1a3e', edgecolor='#8888ff',
                                         linewidth=3, alpha=0.9)
    ax.add_patch(gpu_rect)
    ax.text(5, 4.6, 'TernaryGPU', ha='center', va='top', fontsize=12,
            fontweight='bold', color='#8888ff')

    # Workgroups
    for wg_idx, (wx, ww) in enumerate([(0.8, 4.0), (5.2, 4.0)]):
        wg_rect = mpatches.FancyBboxPatch((wx, 0.8), ww, 3.2,
                                            boxstyle="round,pad=0.1",
                                            facecolor='#2a2a5e', edgecolor='#aa66ff',
                                            linewidth=2)
        ax.add_patch(wg_rect)
        ax.text(wx + ww/2, 3.7, f'Workgroup {wg_idx}', ha='center', va='center',
                fontsize=9, fontweight='bold', color='#aa66ff')

        # PEs within workgroup
        for pe_idx in range(6):
            px = wx + 0.2 + (pe_idx % 3) * 1.2
            py = 1.0 + (pe_idx // 3) * 1.3
            pe_rect = mpatches.FancyBboxPatch((px, py), 1.0, 1.0,
                                                boxstyle="round,pad=0.05",
                                                facecolor='#3a3a7e', edgecolor='#00ff88',
                                                linewidth=1)
            ax.add_patch(pe_rect)
            ax.text(px + 0.5, py + 0.5, f'PE{pe_idx+1}',
                    ha='center', va='center', fontsize=7, color='#00ff88')

    # Labels
    ax.text(2.8, 0.5, 'Processing Elements (PEs)', ha='center', fontsize=7, color='#888888')
    ax.text(7.2, 0.5, 'Processing Elements (PEs)', ha='center', fontsize=7, color='#888888')

    ax.set_facecolor('#0a0a1a')
    fig.patch.set_facecolor('#0a0a1a')
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'gpu_hierarchy.pdf'), dpi=150, bbox_inches='tight',
                facecolor=fig.get_facecolor())
    plt.close()
    print("Generated gpu_hierarchy.pdf")

def opcode_heatmap():
    """27-opcode heatmap showing opcode distribution."""
    fig, ax = plt.subplots(figsize=(8, 5))
    
    opcodes = [
        ('000', 'LOAD', 1), ('001', 'MOV', 1), ('002', 'CLR', 1),
        ('010', 'ADD', 1), ('011', 'SUB', 1), ('012', 'AND', 1),
        ('020', 'OR', 1), ('021', 'NOT', 1), ('022', 'CMP', 1),
        ('100', 'JMP', 1), ('101', 'JZ', 1), ('102', 'JNZ', 1),
        ('110', 'PUSH', 2), ('111', 'POP', 2), ('112', 'CALL', 3),
        ('120', 'RET', 3), ('121', 'HALT', 1), ('122', 'MUL', 3),
        ('200', 'DIV', 5), ('201', 'STOREM', 2), ('202', 'LOADM', 2),
        ('210', 'TVECADD', 4), ('211', 'TMATMUL', 20), ('212', 'TDOT', 6),
        ('220', 'TACT', 3), ('221', 'TLOADW', 10), ('222', 'TSTOREW', 10),
    ]
    
    cycles = [c for _, _, c in opcodes]
    names = [f'{n}\n({t})' for t, n, _ in opcodes]
    
    # Create heatmap-style scatter
    for i, (name, cycle) in enumerate(zip(names, cycles)):
        color = plt.cm.plasma(cycle / 20) if cycle <= 10 else plt.cm.plasma(0.9)
        size = 200 + cycle * 30
        ax.scatter(i % 9, -(i // 9), s=size, c=[color], edgecolors='white', linewidths=1, zorder=5)
        ax.text(i % 9, -(i // 9), str(cycle), ha='center', va='center',
                fontsize=8, fontweight='bold', color='white', zorder=6)
    
    ax.set_xticks(range(9))
    ax.set_yticks([0, -1, -2])
    ax.set_xticklabels(['']*9)
    ax.set_yticklabels(['Group 0\n(000-022)', 'Group 1\n(100-122)', 'Group 2\n(200-222)'])
    ax.set_xlabel('Position within group', fontsize=9, color='white')
    ax.set_title('27 Opcode Cycle Costs (bubble size ∝ cycles, color ∝ cost)',
                 fontsize=10, fontweight='bold', color='white')
    ax.set_facecolor('#1a1a2e')
    fig.patch.set_facecolor('#1a1a2e')
    ax.tick_params(colors='white')
    ax.spines['bottom'].set_color('#333')
    ax.spines['left'].set_color('#333')
    
    # Add opcode labels at top
    for i, (t, n, _) in enumerate(opcodes):
        ax.text(i % 9, 0.5, f'{t}\n{n}', ha='center', va='bottom',
                fontsize=5, color='#aaaaaa', rotation=45)

    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'opcode_heatmap.pdf'), dpi=150, bbox_inches='tight',
                facecolor=fig.get_facecolor())
    plt.close()
    print("Generated opcode_heatmap.pdf")

def benchmark_comparison():
    """Python vs C native benchmark bar chart."""
    fig, ax = plt.subplots(figsize=(8, 4))

    ops = ['Add', 'Mul', 'To\nDecimal', 'From\nDecimal', 'Full\nAdder']
    python_times = [2.1, 5.8, 1.5, 1.8, 245]
    c_times = [0.4, 1.1, 0.3, 0.4, 19]

    x = np.arange(len(ops))
    width = 0.35

    bars1 = ax.bar(x - width/2, python_times, width, label='Python', color='#d9664a', edgecolor='white')
    bars2 = ax.bar(x + width/2, c_times, width, label='C Native', color='#50b86c', edgecolor='white')

    for bar, val in zip(bars1, python_times):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 2,
                f'{val}', ha='center', va='bottom', fontsize=7, color='#d9664a')
    for bar, val in zip(bars2, c_times):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 2,
                f'{val}', ha='center', va='bottom', fontsize=7, color='#50b86c')

    ax.set_xticks(x)
    ax.set_xticklabels(ops, fontsize=8, color='white')
    ax.set_ylabel('Time (µs)', fontsize=9, color='white')
    ax.set_title('Python vs C Native: 1M Operations (lower is better)',
                 fontsize=10, fontweight='bold', color='white')
    ax.legend(fontsize=8)
    ax.set_facecolor('#1a1a2e')
    fig.patch.set_facecolor('#1a1a2e')
    ax.tick_params(colors='white')
    ax.spines['bottom'].set_color('#333')
    ax.spines['left'].set_color('#333')

    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'benchmarks.pdf'), dpi=150, bbox_inches='tight',
                facecolor=fig.get_facecolor())
    plt.close()
    print("Generated benchmarks.pdf")

def digit_efficiency():
    """Binary vs ternary digit count comparison."""
    fig, ax = plt.subplots(figsize=(8, 4))

    values = [10, 100, 1000, 10000, 100000, 1000000]
    binary_digits = [4, 7, 10, 14, 17, 20]
    ternary_digits = [3, 5, 7, 9, 11, 13]

    x = np.arange(len(values))
    width = 0.35

    ax.bar(x - width/2, binary_digits, width, label='Binary', color='#4a90d9', edgecolor='white')
    ax.bar(x + width/2, ternary_digits, width, label='Ternary', color='#50b86c', edgecolor='white')

    ax.set_xticks(x)
    ax.set_xticklabels([str(v) for v in values], fontsize=8, color='white')
    ax.set_xlabel('Decimal Value', fontsize=9, color='white')
    ax.set_ylabel('Digits Required', fontsize=9, color='white')
    ax.set_title('Digit Efficiency: Binary vs Ternary', fontsize=10, fontweight='bold', color='white')
    ax.legend(fontsize=8)
    ax.set_facecolor('#1a1a2e')
    fig.patch.set_facecolor('#1a1a2e')
    ax.tick_params(colors='white')
    ax.spines['bottom'].set_color('#333')
    ax.spines['left'].set_color('#333')

    for i, (b, t) in enumerate(zip(binary_digits, ternary_digits)):
        savings = int((1 - t/b) * 100)
        ax.text(i, max(b, t) + 0.5, f'{savings}%', ha='center', va='bottom',
                fontsize=8, fontweight='bold', color='#e8a838')

    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'digit_efficiency.pdf'), dpi=150, bbox_inches='tight',
                facecolor=fig.get_facecolor())
    plt.close()
    print("Generated digit_efficiency.pdf")

def test_growth():
    """Test suite growth chart."""
    fig, ax = plt.subplots(figsize=(8, 3.5))

    versions = ['v1.0.0\nInitial', 'v1.1.0\nExpansion', 'v2.0.0\nCurrent']
    test_counts = [113, 300, 594]
    colors = ['#4a90d9', '#e8a838', '#50b86c']

    bars = ax.bar(versions, test_counts, color=colors, edgecolor='white', linewidth=1.5, width=0.5)

    for bar, count in zip(bars, test_counts):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 8,
                str(count), ha='center', va='bottom', fontsize=11, fontweight='bold', color='white')

    ax.set_ylabel('Number of Tests', fontsize=9, color='white')
    ax.set_title('Test Suite Growth', fontsize=11, fontweight='bold', color='white')
    ax.set_facecolor('#1a1a2e')
    fig.patch.set_facecolor('#1a1a2e')
    ax.tick_params(colors='white')
    ax.spines['bottom'].set_color('#333')
    ax.spines['left'].set_color('#333')
    ax.set_ylim(0, 680)

    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'test_growth.pdf'), dpi=150, bbox_inches='tight',
                facecolor=fig.get_facecolor())
    plt.close()
    print("Generated test_growth.pdf")

def cpu_architecture():
    """CPU architecture block diagram."""
    fig, ax = plt.subplots(figsize=(10, 5.5))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6)
    ax.axis('off')

    # Main CPU box
    cpu = mpatches.FancyBboxPatch((0.3, 0.3), 9.4, 5.4, boxstyle="round,pad=0.2",
                                   facecolor='#1a1a3e', edgecolor='#00ff88', linewidth=3)
    ax.add_patch(cpu)
    ax.text(5, 5.6, 'CPU Core', ha='center', va='top', fontsize=13, fontweight='bold', color='#00ff88')

    # Control Unit
    cu = mpatches.FancyBboxPatch((0.8, 3.8), 3.0, 1.4, boxstyle="round,pad=0.1",
                                  facecolor='#2a2a5e', edgecolor='#8888ff', linewidth=2)
    ax.add_patch(cu)
    ax.text(2.3, 4.5, 'Control Unit\nFetch / Decode', ha='center', va='center', fontsize=8, color='white')

    # ALU
    alu = mpatches.FancyBboxPatch((4.5, 3.8), 2.5, 1.4, boxstyle="round,pad=0.1",
                                   facecolor='#3a1a3e', edgecolor='#d9664a', linewidth=2)
    ax.add_patch(alu)
    ax.text(5.75, 4.5, 'ALU\nADD/SUB/MUL/DIV\nAND/OR/NOT/CMP', ha='center', va='center', fontsize=7, color='white')

    # Registers
    reg = mpatches.FancyBboxPatch((7.5, 3.8), 2.2, 1.4, boxstyle="round,pad=0.1",
                                   facecolor='#1a3a2e', edgecolor='#e8a838', linewidth=2)
    ax.add_patch(reg)
    ax.text(8.6, 4.5, 'Registers\nR0-R3\nPC / SP', ha='center', va='center', fontsize=7, color='white')

    # Memory Interface
    mem_if = mpatches.FancyBboxPatch((0.8, 1.8), 3.0, 1.2, boxstyle="round,pad=0.1",
                                      facecolor='#2a2a5e', edgecolor='#50b86c', linewidth=2)
    ax.add_patch(mem_if)
    ax.text(2.3, 2.4, 'Memory Interface\nLOADM / STOREM', ha='center', va='center', fontsize=8, color='white')

    # Interrupt Controller
    intc = mpatches.FancyBboxPatch((4.5, 1.8), 2.5, 1.2, boxstyle="round,pad=0.1",
                                    facecolor='#3a1a2e', edgecolor='#9b59b6', linewidth=2)
    ax.add_patch(intc)
    ax.text(5.75, 2.4, 'Interrupt Control\nIVT / INT / IRET', ha='center', va='center', fontsize=7, color='white')

    # Stack
    stk = mpatches.FancyBboxPatch((7.5, 1.8), 2.2, 1.2, boxstyle="round,pad=0.1",
                                   facecolor='#1a2a3e', edgecolor='#e8a838', linewidth=2)
    ax.add_patch(stk)
    ax.text(8.6, 2.4, 'Stack\nPUSH / POP\nSP 255-128', ha='center', va='center', fontsize=7, color='white')

    # Bus Interface
    bus = mpatches.FancyBboxPatch((2.5, 0.6), 5.0, 0.8, boxstyle="round,pad=0.1",
                                   facecolor='#2a2a1e', edgecolor='#00ffcc', linewidth=2)
    ax.add_patch(bus)
    ax.text(5, 1.0, 'System Bus (CPU ↔ Memory ↔ Accelerator ↔ DMA ↔ Display)',
            ha='center', va='center', fontsize=8, color='#00ffcc')

    # Arrows between components
    ax.annotate('', xy=(3.8, 4.2), xytext=(4.5, 4.2), arrowprops=dict(arrowstyle='->', color='white', lw=1.5))
    ax.annotate('', xy=(7.0, 4.2), xytext=(7.5, 4.2), arrowprops=dict(arrowstyle='->', color='white', lw=1.5))
    ax.annotate('', xy=(2.3, 3.8), xytext=(2.3, 3.0), arrowprops=dict(arrowstyle='->', color='#50b86c', lw=1.5))
    ax.annotate('', xy=(5.75, 3.8), xytext=(5.75, 3.0), arrowprops=dict(arrowstyle='->', color='#9b59b6', lw=1.5))
    ax.annotate('', xy=(8.6, 3.8), xytext=(8.6, 3.0), arrowprops=dict(arrowstyle='->', color='#e8a838', lw=1.5))

    ax.set_facecolor('#0a0a1a')
    fig.patch.set_facecolor('#0a0a1a')
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'cpu_architecture.pdf'), dpi=150, bbox_inches='tight',
                facecolor=fig.get_facecolor())
    plt.close()
    print("Generated cpu_architecture.pdf")

def interrupt_flow():
    """Interrupt handling flowchart."""
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis('off')

    steps = [
        (4.5, 9.0, 'Interrupt Occurs\n(TIMER or INT n)', '#4a90d9'),
        (4.5, 7.5, 'Mark IRQ n as Pending', '#4a90d9'),
        (4.5, 6.0, 'CPU Checks iflag\nat Instruction Boundary', '#e8a838'),
        (4.5, 4.5, 'iflag True?\nInterrupts Enabled?', '#d9664a'),
        (2.5, 3.0, 'NO →\nContinue\nNormal\nExecution', '#50b86c'),
        (6.5, 3.0, 'YES\n→ Push PC+1 to Stack\n→ Disable Interrupts\n→ Jump to IVT[n]', '#9b59b6'),
        (6.5, 1.5, 'Handler Executes\n(Load / Store / Process)', '#4a90d9'),
        (6.5, 0.5, 'IRET\n→ Pop PC from Stack\n→ Re-enable Interrupts', '#e8a838'),
    ]

    for x, y, label, color in steps:
        rect = mpatches.FancyBboxPatch((x-1.8, y-0.5), 3.6, 1.0,
                                        boxstyle="round,pad=0.1",
                                        facecolor=color, alpha=0.85, edgecolor='white', linewidth=1.5)
        ax.add_patch(rect)
        ax.text(x, y, label, ha='center', va='center', fontsize=7, color='white', fontweight='bold')

    # Arrows
    arrow_config = dict(arrowstyle='->', color='white', lw=2)
    ax.annotate('', xy=(4.5, 8.5), xytext=(4.5, 8.0), arrowprops=arrow_config)
    ax.annotate('', xy=(4.5, 7.0), xytext=(4.5, 6.5), arrowprops=arrow_config)
    ax.annotate('', xy=(4.5, 5.5), xytext=(4.5, 5.0), arrowprops=arrow_config)
    # Split arrow to NO
    ax.annotate('', xy=(3.5, 4.5), xytext=(2.5, 3.5), arrowprops=dict(arrowstyle='->', color='#50b86c', lw=2))
    # Split arrow to YES
    ax.annotate('', xy=(5.5, 4.5), xytext=(6.5, 3.5), arrowprops=dict(arrowstyle='->', color='#9b59b6', lw=2))
    ax.annotate('', xy=(6.5, 2.5), xytext=(6.5, 2.0), arrowprops=arrow_config)
    ax.annotate('', xy=(6.5, 1.0), xytext=(6.5, 0.9), arrowprops=arrow_config)

    ax.set_facecolor('#0a0a1a')
    fig.patch.set_facecolor('#0a0a1a')
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'interrupt_flow.pdf'), dpi=150, bbox_inches='tight',
                facecolor=fig.get_facecolor())
    plt.close()
    print("Generated interrupt_flow.pdf")

def assembler_flow():
    """Two-pass assembler flowchart."""
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6)
    ax.axis('off')

    # Source code
    src = mpatches.FancyBboxPatch((3.5, 4.5), 3.0, 1.0, boxstyle="round,pad=0.1",
                                   facecolor='#4a90d9', alpha=0.85, edgecolor='white', linewidth=2)
    ax.add_patch(src)
    ax.text(5, 5.0, 'Assembly Source Code', ha='center', va='center', fontsize=9, color='white', fontweight='bold')

    # Pass 1
    p1 = mpatches.FancyBboxPatch((0.5, 2.5), 4.0, 1.5, boxstyle="round,pad=0.1",
                                  facecolor='#50b86c', alpha=0.85, edgecolor='white', linewidth=2)
    ax.add_patch(p1)
    ax.text(2.5, 3.25, 'Pass 1: Symbol Table', ha='center', va='center', fontsize=9, color='white', fontweight='bold')
    ax.text(2.5, 2.9, 'Scan labels, build label→address map', ha='center', va='center', fontsize=7, color='white')
    ax.text(2.5, 2.6, 'Accumulate instruction strings', ha='center', va='center', fontsize=7, color='white')

    # Pass 2
    p2 = mpatches.FancyBboxPatch((5.5, 2.5), 4.0, 1.5, boxstyle="round,pad=0.1",
                                  facecolor='#e8a838', alpha=0.85, edgecolor='white', linewidth=2)
    ax.add_patch(p2)
    ax.text(7.5, 3.25, 'Pass 2: Branch Resolution', ha='center', va='center', fontsize=9, color='white', fontweight='bold')
    ax.text(7.5, 2.9, 'Resolve JMP/JZ/JNZ/CALL targets', ha='center', va='center', fontsize=7, color='white')
    ax.text(7.5, 2.6, 'Replace labels with numeric addresses', ha='center', va='center', fontsize=7, color='white')

    # Output
    out = mpatches.FancyBboxPatch((3.5, 0.5), 3.0, 1.0, boxstyle="round,pad=0.1",
                                   facecolor='#d9664a', alpha=0.85, edgecolor='white', linewidth=2)
    ax.add_patch(out)
    ax.text(5, 1.0, 'Resolved Instruction List', ha='center', va='center', fontsize=9, color='white', fontweight='bold')

    # Arrows
    ax.annotate('', xy=(5, 4.5), xytext=(4.5, 4.0), arrowprops=dict(arrowstyle='->', color='white', lw=2))
    ax.annotate('', xy=(2.5, 2.5), xytext=(2.5, 2.0), arrowprops=dict(arrowstyle='->', color='white', lw=1.5))
    ax.annotate('', xy=(7.5, 2.5), xytext=(7.5, 2.0), arrowprops=dict(arrowstyle='->', color='white', lw=1.5))
    ax.annotate('', xy=(7.5, 2.0), xytext=(5, 1.5), arrowprops=dict(arrowstyle='->', color='white', lw=2))
    ax.annotate('', xy=(4.5, 4.0), xytext=(5.5, 4.0),
                arrowprops=dict(arrowstyle='->', color='white', lw=2, connectionstyle='arc3,rad=0.3'))

    # Labels
    ax.text(2.5, 4.8, '1', ha='center', fontsize=11, fontweight='bold', color='#50b86c')
    ax.text(7.5, 4.8, '2', ha='center', fontsize=11, fontweight='bold', color='#e8a838')

    ax.set_facecolor('#0a0a1a')
    fig.patch.set_facecolor('#0a0a1a')
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'assembler_flow.pdf'), dpi=150, bbox_inches='tight',
                facecolor=fig.get_facecolor())
    plt.close()
    print("Generated assembler_flow.pdf")

def memory_hierarchy():
    """Memory hierarchy diagram."""
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6)
    ax.axis('off')

    levels = [
        (0.5, 4.8, 'CPU Registers\n(R0-R3, PC, SP)', 9.0, 0.7, '#4a90d9', '4 ternary strings'),
        (0.5, 3.8, 'L1 Cache (I$ + D$)\n256B each, direct-mapped', 9.0, 0.7, '#50b86c', '512 bytes total'),
        (0.5, 2.8, 'Main Memory\n512 or 10,000 cells', 9.0, 0.7, '#e8a838', 'Variable-length ternary'),
        (0.5, 1.8, 'Packed Trit Storage\n4 trits per byte', 4.0, 0.7, '#d9664a', '~4x density'),
        (5.5, 1.8, 'VRAM Framebuffer\n1000-5095 (4096 cells)', 4.0, 0.7, '#9b59b6', '64x64 pixels'),
        (0.5, 0.8, 'Native C Backend\nlibternary.so (ctypes)', 9.0, 0.7, '#e8a838', 'Up to 13x speedup'),
    ]

    for x, y, label, w, h, color, note in levels:
        rect = mpatches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.1",
                                        facecolor=color, alpha=0.8, edgecolor='white', linewidth=1.5)
        ax.add_patch(rect)
        ax.text(x + w/2, y + h/2, label, ha='center', va='center', fontsize=8, color='white', fontweight='bold')
        ax.text(x + w/2, y - 0.15, note, ha='center', va='top', fontsize=6, color='#aaaaaa')

    # Arrows between levels
    ax.annotate('', xy=(5, 4.8), xytext=(5, 4.55), arrowprops=dict(arrowstyle='<->', color='#00ff88', lw=1.5))
    ax.annotate('', xy=(5, 3.8), xytext=(5, 3.55), arrowprops=dict(arrowstyle='<->', color='#00ff88', lw=1.5))
    ax.annotate('', xy=(5, 2.8), xytext=(5, 2.55), arrowprops=dict(arrowstyle='<->', color='#00ff88', lw=1.5))

    ax.set_facecolor('#0a0a1a')
    fig.patch.set_facecolor('#0a0a1a')
    ax.set_title('Memory Hierarchy', fontsize=12, fontweight='bold', color='white', pad=10)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'memory_hierarchy.pdf'), dpi=150, bbox_inches='tight',
                facecolor=fig.get_facecolor())
    plt.close()
    print("Generated memory_hierarchy.pdf")

def nn_architecture():
    """Neural network architecture diagram."""
    fig, ax = plt.subplots(figsize=(8, 3.5))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 4)
    ax.axis('off')

    # Input layer
    for i, y_pos in enumerate([2.5, 2.0, 1.5, 1.0]):
        circle = plt.Circle((1.5, y_pos), 0.25, color='#4a90d9', ec='white', lw=1.5, zorder=5)
        ax.add_patch(circle)
        ax.text(1.5, y_pos, f'x{i+1}', ha='center', va='center', fontsize=5, color='white', fontweight='bold')

    # Hidden layer
    for i, y_pos in enumerate([2.25, 1.75, 1.25]):
        circle = plt.Circle((4.0, y_pos), 0.25, color='#50b86c', ec='white', lw=1.5, zorder=5)
        ax.add_patch(circle)
        ax.text(4.0, y_pos, f'h{i+1}', ha='center', va='center', fontsize=5, color='white', fontweight='bold')

    # Output layer
    for i, y_pos in enumerate([2.0, 1.5]):
        circle = plt.Circle((6.5, y_pos), 0.25, color='#e8a838', ec='white', lw=1.5, zorder=5)
        ax.add_patch(circle)
        ax.text(6.5, y_pos, f'y{i+1}', ha='center', va='center', fontsize=5, color='white', fontweight='bold')

    # Output
    output_circle = plt.Circle((8.5, 1.75), 0.3, color='#d9664a', ec='white', lw=2, zorder=5)
    ax.add_patch(output_circle)
    ax.text(8.5, 1.75, 'Trit', ha='center', va='center', fontsize=5, color='white', fontweight='bold')
    ax.text(8.5, 1.4, '0/1/2', ha='center', va='center', fontsize=4, color='#aaaaaa')

    # Connections (just draw a few representative ones)
    for src_y in [2.5, 2.0, 1.5, 1.0]:
        for dst_y in [2.25, 1.75, 1.25]:
            ax.plot([1.75, 3.75], [src_y, dst_y], color='#555555', lw=0.5, alpha=0.5)
    for src_y in [2.25, 1.75, 1.25]:
        for dst_y in [2.0, 1.5]:
            ax.plot([4.25, 6.25], [src_y, dst_y], color='#555555', lw=0.5, alpha=0.5)
    ax.plot([6.75, 8.2], [1.75, 1.75], color='#555555', lw=0.5, alpha=0.5)

    # Labels
    ax.text(1.5, 3.2, 'Input\n(ternary)', ha='center', fontsize=7, color='#4a90d9', fontweight='bold')
    ax.text(4.0, 3.0, 'Hidden\n(ternary)', ha='center', fontsize=7, color='#50b86c', fontweight='bold')
    ax.text(6.5, 2.8, 'Output\n(ternary)', ha='center', fontsize=7, color='#e8a838', fontweight='bold')

    # Step function annotation
    ax.annotate('ternary_step', xy=(8.0, 2.8), fontsize=6, color='#d9664a',
                ha='center', arrowprops=dict(arrowstyle='->', color='#d9664a', lw=1))

    ax.set_facecolor('#0a0a1a')
    fig.patch.set_facecolor('#0a0a1a')
    ax.set_title('Ternary Neural Network: MLP Architecture', fontsize=11, fontweight='bold', color='white')
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'nn_architecture.pdf'), dpi=150, bbox_inches='tight',
                facecolor=fig.get_facecolor())
    plt.close()
    print("Generated nn_architecture.pdf")

def training_flow():
    """SGD vs HillClimber training flow."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))

    for ax, title, color, steps in [
        (ax1, 'SGD Optimizer', '#4a90d9',
         ['Shuffle Dataset', 'Forward pass\n(perceptron)', 'Compute error\n(target - pred)', 'Clamp to {-1,0,+1}',
          'Update each weight\nw += lr * input * error', 'Clamp to {-1,0,+1}', 'Convert back to ternary']),
        (ax2, 'HillClimber', '#e8a838',
         ['Pick 1-3 random\nweights/biases', 'Set to random\n{0,1,2}', 'Evaluate accuracy\non full dataset',
          'Better?\n→ Keep mutation', 'Same?\n→ Keep (explore)', 'Worse?\n→ Revert', 'Restore best\nif stuck'])]:

        for i, (step, y_pos) in enumerate(zip(steps, [3.3, 2.8, 2.3, 1.8, 1.3, 0.8, 0.3])):
            rect = mpatches.FancyBboxPatch((0.3, y_pos-0.15), 4.4, 0.35,
                                            boxstyle="round,pad=0.02",
                                            facecolor=color, alpha=0.7 + i*0.04,
                                            edgecolor='white', linewidth=0.5)
            ax.add_patch(rect)
            ax.text(2.5, y_pos, step, ha='center', va='center', fontsize=6, color='white')

        ax.set_xlim(0, 5)
        ax.set_ylim(0, 4)
        ax.axis('off')
        ax.set_title(title, fontsize=10, fontweight='bold', color=color, pad=5)
        ax.set_facecolor('#0a0a1a')

    fig.patch.set_facecolor('#0a0a1a')
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'training_flow.pdf'), dpi=150, bbox_inches='tight',
                facecolor=fig.get_facecolor())
    plt.close()
    print("Generated training_flow.pdf")

def tal_pipeline():
    """TAL compiler pipeline diagram."""
    fig, ax = plt.subplots(figsize=(10, 3.5))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 4)
    ax.axis('off')

    stages = [
        (0.3, 2.5, 'TAL\nSource', '#4a90d9'),
        (2.3, 2.5, 'Tokenizer\nIdentifiers\nNumbers\nLabels', '#50b86c'),
        (4.3, 2.5, 'Parser\nvar/const/label\nStatements', '#e8a838'),
        (6.3, 2.5, 'Code Generator\nEmit CPU\ninstructions', '#d9664a'),
        (8.3, 2.5, 'Assembly\nOutput\n(27 opcodes)', '#9b59b6'),
    ]

    for x, y, label, color in stages:
        rect = mpatches.FancyBboxPatch((x, y-0.6), 1.8, 1.2, boxstyle="round,pad=0.1",
                                        facecolor=color, alpha=0.85, edgecolor='white', linewidth=2)
        ax.add_patch(rect)
        ax.text(x+0.9, y, label, ha='center', va='center', fontsize=7, color='white', fontweight='bold')

    # Symbol table below
    sym = mpatches.FancyBboxPatch((3.3, 0.3), 3.4, 0.8, boxstyle="round,pad=0.1",
                                   facecolor='#2a2a5e', edgecolor='#8888ff', linewidth=1.5, linestyle='--')
    ax.add_patch(sym)
    ax.text(5, 0.7, 'Symbol Table: variables, constants, labels', ha='center', va='center', fontsize=7, color='#8888ff')

    # Arrows between stages
    for i in range(4):
        x_start = 2.1 + i * 2.0
        ax.annotate('', xy=(x_start + 0.2, 2.5), xytext=(x_start - 0.2, 2.5),
                    arrowprops=dict(arrowstyle='->', color='white', lw=2))

    # Connection from parser/code gen to symbol table
    ax.plot([5.3, 5.3], [1.9, 1.1], color='#8888ff', lw=1, linestyle='--')
    ax.plot([4.7, 4.7], [1.9, 1.1], color='#8888ff', lw=1, linestyle='--')

    ax.set_facecolor('#0a0a1a')
    fig.patch.set_facecolor('#0a0a1a')
    ax.set_title('TAL Compiler Pipeline', fontsize=11, fontweight='bold', color='white', pad=5)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'tal_pipeline.pdf'), dpi=150, bbox_inches='tight',
                facecolor=fig.get_facecolor())
    plt.close()
    print("Generated tal_pipeline.pdf")

def instruction_formats():
    """Instruction format visualization."""
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 5)
    ax.axis('off')

    formats = [
        (0.5, 4.0, 'Format A', 'OP R_dst R_src', 'ADD R0 R1', '010 0 1', '#4a90d9'),
        (0.5, 3.2, 'Format B', 'OP R_op', 'CLR R0', '002 0', '#50b86c'),
        (0.5, 2.4, 'Format C', 'OP R_dst value', 'LOAD R0 10', '000 0 10', '#e8a838'),
        (0.5, 1.6, 'Format D', 'OP addr', 'JMP loop', '100 loop', '#d9664a'),
        (0.5, 0.8, 'Format E', 'OP', 'HALT', '121', '#9b59b6'),
        (5.5, 4.0, 'Format M', 'OP addr R_reg', 'STOREM 33 R0', '201 0 33', '#4a90d9'),
        (5.5, 3.2, 'Format A3', 'OP dst src_a src_b', 'TVECADD 0 1 2', '210 0 1 2', '#50b86c'),
        (5.5, 2.4, 'Format B2', 'OP dst src', 'TACT 0 0', '220 0 0', '#e8a838'),
        (5.5, 1.6, 'Format L', 'OP addr rows cols', 'TLOADW 100 4 4', '221 100 4 4', '#d9664a'),
        (5.5, 0.8, 'Format S2', 'OP tid addr', 'TSTOREW 0 100', '222 0 100', '#9b59b6'),
    ]

    for x, y, fmt, syntax, example, encoding, color in formats:
        rect = mpatches.FancyBboxPatch((x, y-0.2), 4.0, 0.6, boxstyle="round,pad=0.05",
                                        facecolor=color, alpha=0.7, edgecolor='white', linewidth=1)
        ax.add_patch(rect)
        ax.text(x + 2.0, y + 0.1, f'{fmt}: {syntax}', ha='center', va='center',
                fontsize=7, color='white', fontweight='bold')
        ax.text(x + 2.0, y - 0.1, f'{example}  →  {encoding}', ha='center', va='center',
                fontsize=6, color='#cccccc')

    ax.set_facecolor('#0a0a1a')
    fig.patch.set_facecolor('#0a0a1a')
    ax.set_title('Instruction Encoding Formats', fontsize=11, fontweight='bold', color='white', pad=5)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'instruction_formats.pdf'), dpi=150, bbox_inches='tight',
                facecolor=fig.get_facecolor())
    plt.close()
    print("Generated instruction_formats.pdf")

def ripple_carry_adder():
    """Ripple-carry adder circuit diagram."""
    fig, ax = plt.subplots(figsize=(10, 3.5))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 3.5)
    ax.axis('off')

    n_stages = 4
    for i in range(n_stages):
        x = 1.5 + i * 2.0

        # Full adder box
        fa = mpatches.FancyBboxPatch((x-0.6, 1.0), 1.2, 1.2, boxstyle="round,pad=0.1",
                                      facecolor='#2a2a5e', edgecolor='#4a90d9', linewidth=2)
        ax.add_patch(fa)
        ax.text(x, 1.6, f'FA\n{i+1}', ha='center', va='center', fontsize=8, color='white', fontweight='bold')

        # Input trits above
        ax.text(x-0.25, 2.6, f'a{i+1}', ha='center', fontsize=8, color='#e8a838')
        ax.text(x+0.25, 2.6, f'b{i+1}', ha='center', fontsize=8, color='#d9664a')

        # Input arrows
        ax.annotate('', xy=(x-0.25, 2.6), xytext=(x-0.25, 2.2), arrowprops=dict(arrowstyle='->', color='#e8a838', lw=1))
        ax.annotate('', xy=(x+0.25, 2.6), xytext=(x+0.25, 2.2), arrowprops=dict(arrowstyle='->', color='#d9664a', lw=1))

        # Sum output below
        ax.text(x, 0.4, f's{i+1}', ha='center', fontsize=9, color='#50b86c', fontweight='bold')
        ax.annotate('', xy=(x, 1.0), xytext=(x, 0.6), arrowprops=dict(arrowstyle='->', color='#50b86c', lw=1.5))

        # Carry propagation
        if i < n_stages - 1:
            ax.annotate('', xy=(x + 0.6, 1.3), xytext=(x + 1.4, 1.3),
                        arrowprops=dict(arrowstyle='->', color='#9b59b6', lw=2))
            ax.text(x + 1.0, 1.5, f'c{i+2}', ha='center', fontsize=7, color='#9b59b6')

    # Carry chain labels
    ax.text(1.5 + 0.0, 0.8, 'c₁=0', ha='center', fontsize=7, color='#9b59b6')
    ax.text(3.5 - 0.2, 2.9, 'cin at each\nstage', ha='center', fontsize=6, color='#aaaaaa')

    ax.set_facecolor('#0a0a1a')
    fig.patch.set_facecolor('#0a0a1a')
    ax.set_title('Ternary Ripple-Carry Adder — 4-Stage Full-Adder Chain', fontsize=11, fontweight='bold', color='white')
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'ripple_carry_adder.pdf'), dpi=150, bbox_inches='tight',
                facecolor=fig.get_facecolor())
    plt.close()
    print("Generated ripple_carry_adder.pdf")

def decimal_roundtrip():
    """Decimal round-trip arithmetic flow diagram."""
    fig, ax = plt.subplots(figsize=(8, 3.5))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 4)
    ax.axis('off')

    # Ternary inputs
    t1 = mpatches.FancyBboxPatch((0.3, 2.5), 1.8, 0.8, boxstyle="round,pad=0.1",
                                  facecolor='#4a90d9', edgecolor='white', linewidth=1.5)
    ax.add_patch(t1)
    ax.text(1.2, 2.9, 'ternary\n"1021"', ha='center', va='center', fontsize=7, color='white', fontweight='bold')

    t2 = mpatches.FancyBboxPatch((0.3, 1.0), 1.8, 0.8, boxstyle="round,pad=0.1",
                                  facecolor='#4a90d9', edgecolor='white', linewidth=1.5)
    ax.add_patch(t2)
    ax.text(1.2, 1.4, 'ternary\n"12"', ha='center', va='center', fontsize=7, color='white', fontweight='bold')

    # Conversion step
    c1 = mpatches.FancyBboxPatch((3.2, 2.5), 1.8, 0.8, boxstyle="round,pad=0.1",
                                  facecolor='#50b86c', edgecolor='white', linewidth=1.5)
    ax.add_patch(c1)
    ax.text(4.1, 2.9, 't2d\n34', ha='center', va='center', fontsize=7, color='white', fontweight='bold')

    c2 = mpatches.FancyBboxPatch((3.2, 1.0), 1.8, 0.8, boxstyle="round,pad=0.1",
                                  facecolor='#50b86c', edgecolor='white', linewidth=1.5)
    ax.add_patch(c2)
    ax.text(4.1, 1.4, 't2d\n5', ha='center', va='center', fontsize=7, color='white', fontweight='bold')

    # Operation
    op = mpatches.FancyBboxPatch((6.0, 1.4), 1.8, 1.4, boxstyle="round,pad=0.1",
                                  facecolor='#e8a838', edgecolor='white', linewidth=2)
    ax.add_patch(op)
    ax.text(6.9, 2.1, '34 + 5\n= 39', ha='center', va='center', fontsize=8, color='white', fontweight='bold')

    # Result
    res = mpatches.FancyBboxPatch((8.5, 1.4), 1.4, 1.4, boxstyle="round,pad=0.1",
                                   facecolor='#d9664a', edgecolor='white', linewidth=2)
    ax.add_patch(res)
    ax.text(9.2, 2.1, 'd2t\n"1110"', ha='center', va='center', fontsize=7, color='white', fontweight='bold')

    # Arrows
    ax.annotate('', xy=(2.1, 2.9), xytext=(3.2, 2.9), arrowprops=dict(arrowstyle='->', color='white', lw=1.5))
    ax.annotate('', xy=(2.1, 1.4), xytext=(3.2, 1.4), arrowprops=dict(arrowstyle='->', color='white', lw=1.5))
    ax.annotate('', xy=(4.1, 2.5), xytext=(4.1, 2.1), arrowprops=dict(arrowstyle='->', color='white', lw=1.5))
    ax.annotate('', xy=(4.1, 1.8), xytext=(4.1, 2.1), arrowprops=dict(arrowstyle='->', color='white', lw=1.5))
    ax.annotate('', xy=(7.8, 2.1), xytext=(8.5, 2.1), arrowprops=dict(arrowstyle='->', color='white', lw=2))

    # Labels
    ax.text(4.1, 0.5, 'Step 1: ternary → decimal', ha='center', fontsize=7, color='#50b86c')
    ax.text(6.9, 0.5, 'Step 2: decimal op', ha='center', fontsize=7, color='#e8a838')
    ax.text(9.2, 0.5, 'Step 3: decimal → ternary', ha='center', fontsize=7, color='#d9664a')

    ax.set_facecolor('#0a0a1a')
    fig.patch.set_facecolor('#0a0a1a')
    ax.set_title('Decimal Round-Trip Arithmetic Pipeline', fontsize=11, fontweight='bold', color='white')
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'decimal_roundtrip.pdf'), dpi=150, bbox_inches='tight',
                facecolor=fig.get_facecolor())
    plt.close()
    print("Generated decimal_roundtrip.pdf")

def cache_organization():
    """Direct-mapped L1 cache structure diagram."""
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6)
    ax.axis('off')

    # Tag array on left
    tag_box = mpatches.FancyBboxPatch((0.3, 0.3), 2.5, 5.4, boxstyle="round,pad=0.1",
                                       facecolor='#1a1a3e', edgecolor='#4a90d9', linewidth=2)
    ax.add_patch(tag_box)
    ax.text(1.55, 5.6, 'Tag Array', ha='center', va='top', fontsize=9, color='#4a90d9', fontweight='bold')
    for i in range(6):
        y = 4.7 - i * 0.75
        rect = mpatches.FancyBboxPatch((0.6, y-0.25), 1.9, 0.45, boxstyle="round,pad=0.02",
                                        facecolor='#2a2a5e', edgecolor='#555', linewidth=0.5)
        ax.add_patch(rect)
        ax.text(1.55, y, f'Tag {i}', ha='center', va='center', fontsize=6, color='#aaa')

    # Data array on right
    data_box = mpatches.FancyBboxPatch((3.5, 0.3), 6.2, 5.4, boxstyle="round,pad=0.1",
                                        facecolor='#1a1a3e', edgecolor='#50b86c', linewidth=2)
    ax.add_patch(data_box)
    ax.text(6.6, 5.6, 'Data Array (64 cache lines)', ha='center', va='top', fontsize=9, color='#50b86c', fontweight='bold')
    for i in range(4):
        y = 4.7 - i * 0.75
        rect = mpatches.FancyBboxPatch((3.8, y-0.25), 2.8, 0.45, boxstyle="round,pad=0.02",
                                        facecolor='#2a3a2e', edgecolor='#555', linewidth=0.5)
        ax.add_patch(rect)
        ax.text(5.2, y, f'Line {i}: 8 B data', ha='center', va='center', fontsize=6, color='#aaa')
        rect = mpatches.FancyBboxPatch((7.0, y-0.25), 2.5, 0.45, boxstyle="round,pad=0.02",
                                        facecolor='#2a3a2e', edgecolor='#555', linewidth=0.5)
        ax.add_patch(rect)
        ax.text(8.25, y, 'Dirty + Valid', ha='center', va='center', fontsize=6, color='#aaa')

    # CPU -> Cache arrow
    ax.annotate('', xy=(5, 5.8), xytext=(5, 5.7), arrowprops=dict(arrowstyle='->', color='#00ff88', lw=2))
    ax.text(5, 5.9, 'CPU Address → Index → Tag Match', ha='center', fontsize=7, color='#00ff88')

    ax.set_facecolor('#0a0a1a')
    fig.patch.set_facecolor('#0a0a1a')
    ax.set_title('Direct-Mapped L1 Cache — Tag Array + Data Array (64 lines × 8 B)', fontsize=9, fontweight='bold', color='white')
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'cache_organization.pdf'), dpi=150, bbox_inches='tight',
                facecolor=fig.get_facecolor())
    plt.close()
    print("Generated cache_organization.pdf")

def pipeline_hazard():
    """Pipeline data hazard with forwarding diagram."""
    fig, ax = plt.subplots(figsize=(10, 3.5))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 4)
    ax.axis('off')

    stages = ['IF', 'ID', 'EX', 'MEM', 'WB']
    colors = ['#4a90d9', '#50b86c', '#e8a838', '#d9664a', '#9b59b6']

    for i, (stage, color) in enumerate(zip(stages, colors)):
        rect = mpatches.FancyBboxPatch((0.5 + i*1.8, 2.8), 1.5, 0.8, boxstyle="round,pad=0.1",
                                        facecolor=color, alpha=0.8, edgecolor='white', linewidth=1.5)
        ax.add_patch(rect)
        ax.text(1.25 + i*1.8, 3.2, stage, ha='center', va='center', fontsize=9, color='white', fontweight='bold')

    # ADD R0, R1 instruction
    ax.text(1.25, 2.4, 'ADD R0 R1', ha='center', fontsize=7, color='white')
    # MOV R2, R0 instruction (dependent)
    ax.text(3.05, 2.4, 'MOV R2 R0', ha='center', fontsize=7, color='white')

    # Hazard arrow
    ax.annotate('', xy=(2.75, 2.0), xytext=(4.85, 2.0), arrowprops=dict(arrowstyle='->', color='#d9664a', lw=2))
    ax.text(3.8, 1.8, 'RAW Hazard: R0 written in EX, read in ID', ha='center', fontsize=7, color='#d9664a', fontweight='bold')

    # Forwarding path
    ax.annotate('', xy=(3.5, 2.8), xytext=(4.5, 3.6),
                arrowprops=dict(arrowstyle='->', color='#00ff88', lw=2, connectionstyle='arc3,rad=0.3'))
    ax.text(5.0, 3.7, 'Forwarding Path\n(bypass EX→ID)', ha='center', fontsize=6, color='#00ff88')

    # Without forwarding: stall
    stall_rect = mpatches.FancyBboxPatch((5.5, 0.3), 2.5, 1.2, boxstyle="round,pad=0.1",
                                          facecolor='#3a1a1a', edgecolor='#d9664a', linewidth=1.5)
    ax.add_patch(stall_rect)
    ax.text(6.75, 0.9, 'Without forwarding:\n2-cycle stall penalty', ha='center', va='center', fontsize=7, color='#d9664a')

    # Forwarding check
    fwd_rect = mpatches.FancyBboxPatch((0.5, 0.3), 2.5, 1.2, boxstyle="round,pad=0.1",
                                        facecolor='#1a3a1a', edgecolor='#50b86c', linewidth=1.5)
    ax.add_patch(fwd_rect)
    ax.text(1.75, 0.9, 'With forwarding:\n0-cycle penalty', ha='center', va='center', fontsize=7, color='#50b86c')

    ax.set_facecolor('#0a0a1a')
    fig.patch.set_facecolor('#0a0a1a')
    ax.set_title('Pipeline Data Hazard (RAW) with Forwarding Path', fontsize=10, fontweight='bold', color='white')
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'pipeline_hazard.pdf'), dpi=150, bbox_inches='tight',
                facecolor=fig.get_facecolor())
    plt.close()
    print("Generated pipeline_hazard.pdf")

def branch_predictor_fsm():
    """2-bit saturating counter branch predictor state machine."""
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 5)
    ax.axis('off')

    states = [
        (1.5, 3.5, '00\nStrongly\nNot Taken', '#4a90d9'),
        (4.5, 3.5, '01\nWeakly\nNot Taken', '#50b86c'),
        (7.0, 3.5, '10\nWeakly\nTaken', '#e8a838'),
        (9.5, 3.5, '11\nStrongly\nTaken', '#d9664a'),
    ]

    for x, y, label, color in states:
        circle = plt.Circle((x, y), 0.8, color=color, ec='white', lw=2, zorder=5)
        ax.add_patch(circle)
        ax.text(x, y, label, ha='center', va='center', fontsize=6, color='white', fontweight='bold')

    # Transitions for "taken" (T)
    ax.annotate('', xy=(2.3, 3.5), xytext=(3.7, 3.5), arrowprops=dict(arrowstyle='->', color='#50b86c', lw=2))
    ax.text(3.0, 3.3, 'T', ha='center', fontsize=8, color='#50b86c', fontweight='bold')
    ax.annotate('', xy=(5.3, 3.5), xytext=(6.2, 3.5), arrowprops=dict(arrowstyle='->', color='#e8a838', lw=2))
    ax.text(5.75, 3.3, 'T', ha='center', fontsize=8, color='#e8a838', fontweight='bold')
    ax.annotate('', xy=(7.8, 3.5), xytext=(8.7, 3.5), arrowprops=dict(arrowstyle='->', color='#d9664a', lw=2))
    ax.text(8.25, 3.3, 'T', ha='center', fontsize=8, color='#d9664a', fontweight='bold')

    # Transitions for "not taken" (NT)
    ax.annotate('', xy=(9.5, 2.8), xytext=(9.5, 2.1), arrowprops=dict(arrowstyle='->', color='#e8a838', lw=1.5))
    ax.text(9.8, 2.5, 'NT', fontsize=7, color='#e8a838')
    ax.annotate('', xy=(7.0, 2.8), xytext=(7.0, 2.1), arrowprops=dict(arrowstyle='->', color='#50b86c', lw=1.5))
    ax.text(6.5, 2.5, 'NT', fontsize=7, color='#50b86c')
    ax.annotate('', xy=(4.5, 2.8), xytext=(4.5, 2.1), arrowprops=dict(arrowstyle='->', color='#4a90d9', lw=1.5))
    ax.text(5.2, 2.2, 'NT', fontsize=7, color='#4a90d9')

    # Counter saturates
    sat_rect = mpatches.FancyBboxPatch((7.5, 0.3), 2.2, 1.0, boxstyle="round,pad=0.1",
                                        facecolor='#2a1a1a', edgecolor='#d9664a', linewidth=1.5)
    ax.add_patch(sat_rect)
    ax.text(8.6, 0.8, 'Counter saturates\nat 0 and 3', ha='center', va='center', fontsize=6, color='#d9664a')

    # Prediction verdict
    pred_rect = mpatches.FancyBboxPatch((0.3, 0.3), 4.0, 1.0, boxstyle="round,pad=0.1",
                                         facecolor='#1a2a1a', edgecolor='#50b86c', linewidth=1.5)
    ax.add_patch(pred_rect)
    ax.text(2.3, 0.8, 'Prediction: MSB of counter', ha='center', va='center', fontsize=7, color='#50b86c')
    ax.text(2.3, 0.45, '0 → Not Taken, 1 → Taken, 85--95% accuracy', ha='center', va='center', fontsize=6, color='#aaa')

    ax.set_facecolor('#0a0a1a')
    fig.patch.set_facecolor('#0a0a1a')
    ax.set_title('2-Bit Saturating Counter Branch Predictor — State Machine', fontsize=10, fontweight='bold', color='white')
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'branch_predictor_fsm.pdf'), dpi=150, bbox_inches='tight',
                facecolor=fig.get_facecolor())
    plt.close()
    print("Generated branch_predictor_fsm.pdf")

def bus_arbitration():
    """System bus with CPU/DMA/Accelerator arbitration."""
    fig, ax = plt.subplots(figsize=(9, 4))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 4)
    ax.axis('off')

    # Bus
    bus = mpatches.FancyBboxPatch((0.3, 1.5), 9.4, 0.8, boxstyle="round,pad=0.1",
                                   facecolor='#1a1a3e', edgecolor='#00ffcc', linewidth=3)
    ax.add_patch(bus)
    ax.text(5, 1.9, 'System Bus (shared address/data/control lines)', ha='center', va='center', fontsize=9, color='#00ffcc')

    # Bus master: CPU
    cpu_box = mpatches.FancyBboxPatch((0.5, 2.8), 2.5, 0.9, boxstyle="round,pad=0.1",
                                       facecolor='#4a90d9', alpha=0.85, edgecolor='white', linewidth=2)
    ax.add_patch(cpu_box)
    ax.text(1.75, 3.25, 'CPU (default master)', ha='center', va='center', fontsize=8, color='white', fontweight='bold')

    # Bus master: DMA
    dma_box = mpatches.FancyBboxPatch((3.8, 2.8), 2.5, 0.9, boxstyle="round,pad=0.1",
                                       facecolor='#e8a838', alpha=0.85, edgecolor='white', linewidth=2)
    ax.add_patch(dma_box)
    ax.text(5.05, 3.25, 'DMA Controller', ha='center', va='center', fontsize=8, color='white', fontweight='bold')

    # Bus master: Accelerator
    acc_box = mpatches.FancyBboxPatch((7.0, 2.8), 2.5, 0.9, boxstyle="round,pad=0.1",
                                       facecolor='#9b59b6', alpha=0.85, edgecolor='white', linewidth=2)
    ax.add_patch(acc_box)
    ax.text(8.25, 3.25, 'Tensor Accelerator', ha='center', va='center', fontsize=8, color='white', fontweight='bold')

    # Bus slaves
    mem_box = mpatches.FancyBboxPatch((0.5, 0.2), 3.0, 0.8, boxstyle="round,pad=0.1",
                                       facecolor='#50b86c', alpha=0.85, edgecolor='white', linewidth=1.5)
    ax.add_patch(mem_box)
    ax.text(2.0, 0.6, 'Memory (slave)', ha='center', va='center', fontsize=7, color='white')

    vram_box = mpatches.FancyBboxPatch((4.3, 0.2), 2.5, 0.8, boxstyle="round,pad=0.1",
                                        facecolor='#d9664a', alpha=0.85, edgecolor='white', linewidth=1.5)
    ax.add_patch(vram_box)
    ax.text(5.55, 0.6, 'VRAM (slave)', ha='center', va='center', fontsize=7, color='white')

    io_box = mpatches.FancyBboxPatch((7.5, 0.2), 2.0, 0.8, boxstyle="round,pad=0.1",
                                      facecolor='#e8a838', alpha=0.85, edgecolor='white', linewidth=1.5)
    ax.add_patch(io_box)
    ax.text(8.5, 0.6, 'I/O (slave)', ha='center', va='center', fontsize=7, color='white')

    # Arbitration label
    arb = mpatches.FancyBboxPatch((3.0, 3.7), 4.0, 0.3, boxstyle="round,pad=0.02",
                                   facecolor='#2a2a1e', edgecolor='#e8a838', linewidth=1)
    ax.add_patch(arb)
    ax.text(5, 3.85, 'Arbitration: fixed priority CPU > DMA > Accelerator', ha='center', va='center', fontsize=6, color='#e8a838')

    ax.set_facecolor('#0a0a1a')
    fig.patch.set_facecolor('#0a0a1a')
    ax.set_title('System Bus Architecture — Masters and Slaves', fontsize=11, fontweight='bold', color='white')
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'bus_arbitration.pdf'), dpi=150, bbox_inches='tight',
                facecolor=fig.get_facecolor())
    plt.close()
    print("Generated bus_arbitration.pdf")

def palette_colors():
    """9-color palette visualization."""
    fig, ax = plt.subplots(figsize=(8, 3))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 3)
    ax.axis('off')

    palette = [
        ('#000000', 'Black', 0), ('#ffffff', 'White', 1), ('#ff0000', 'Red', 2),
        ('#00ff00', 'Green', 3), ('#0000ff', 'Blue', 4), ('#ffff00', 'Yellow', 5),
        ('#00ffff', 'Cyan', 6), ('#ff00ff', 'Magenta', 7), ('#ff8800', 'Orange', 8),
    ]

    for i, (rgb, name, idx) in enumerate(palette):
        x = 0.6 + i * 1.0
        rect = mpatches.FancyBboxPatch((x, 0.8), 0.8, 1.6, boxstyle="round,pad=0.05",
                                        facecolor=rgb, edgecolor='white', linewidth=1.5)
        ax.add_patch(rect)
        # Text color contrast
        text_color = 'white' if idx in [0, 2, 4] else 'black'
        ax.text(x+0.4, 1.6, str(idx), ha='center', va='center', fontsize=11, color=text_color, fontweight='bold')
        ax.text(x+0.4, 0.5, name, ha='center', va='center', fontsize=5, color='white')
        ax.text(x+0.4, 0.2, f'idx {idx}', ha='center', va='center', fontsize=4, color='#666')

    ax.set_facecolor('#0a0a1a')
    fig.patch.set_facecolor('#0a0a1a')
    ax.set_title('9-Color Palette for SDK Framebuffer', fontsize=11, fontweight='bold', color='white')
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'palette_colors.pdf'), dpi=150, bbox_inches='tight',
                facecolor=fig.get_facecolor())
    plt.close()
    print("Generated palette_colors.pdf")

def test_coverage():
    """Test suite coverage pie chart."""
    fig, ax = plt.subplots(figsize=(7, 4))

    categories = [
        ('Hardware', 76, '#4a90d9'),
        ('Neural Networks', 128, '#50b86c'),
        ('SDK / Display', 90, '#e8a838'),
        ('CPU / Accelerator', 62, '#d9664a'),
        ('ALU / Arithmetic', 22, '#9b59b6'),
        ('Assembler / TAL / Machine', 17, '#00ff88'),
        ('OS / Kernel', 38, '#ff66aa'),
        ('GPU / SIMD / Packed', 50, '#88ccff'),
        ('Conversion / Logic', 20, '#ffaa66'),
        ('Cache / Bus / DMA / IRQ', 48, '#aa88ff'),
        ('Profiler / Viz / VRAM', 38, '#66ffaa'),
        ('Native C Backend', 11, '#ff6666'),
    ]

    values = [c[1] for c in categories]
    labels = [f'{c[0]}\n({c[1]})' for c in categories]
    colors = [c[2] for c in categories]

    wedges, texts, autotexts = ax.pie(values, labels=None, autopct='', startangle=140,
                                       colors=colors, wedgeprops={'edgecolor': 'white', 'linewidth': 1})

    ax.legend(wedges, labels, title='Test Categories', loc='center left',
              bbox_to_anchor=(1, 0, 0.5, 1), fontsize=6)
    ax.set_title('Test Coverage by Category (594 total)', fontsize=11, fontweight='bold', color='white', pad=15)
    ax.set_facecolor('#0a0a1a')
    fig.patch.set_facecolor('#0a0a1a')
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'test_coverage.pdf'), dpi=150, bbox_inches='tight',
                facecolor=fig.get_facecolor())
    plt.close()
    print("Generated test_coverage.pdf")

def webviz_architecture():
    """Web visualizer architecture diagram."""
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 4.5)
    ax.axis('off')

    # Backend box
    backend = mpatches.FancyBboxPatch((0.3, 2.0), 3.5, 2.2, boxstyle="round,pad=0.1",
                                       facecolor='#1a1a3e', edgecolor='#4a90d9', linewidth=2.5)
    ax.add_patch(backend)
    ax.text(2.05, 3.8, 'FastAPI Backend (port 8000)', ha='center', fontsize=8, color='#4a90d9', fontweight='bold')

    backend_components = [
        (1.0, 3.2, 'REST Endpoints\n/state /registers\n/memory /disasm'),
        (3.0, 3.2, 'WebSocket\n/ws'),
        (1.0, 2.4, 'SnapshotEngine\n10K-cell CPU\nRealistic timing'),
        (3.0, 2.4, 'CPU State\nCapture\n(JSON)'),
    ]
    for x, y, label in backend_components:
        rect = mpatches.FancyBboxPatch((x-0.6, y-0.25), 1.3, 0.5, boxstyle="round,pad=0.02",
                                        facecolor='#2a2a5e', edgecolor='#8888ff', linewidth=0.5)
        ax.add_patch(rect)
        ax.text(x, y, label, ha='center', va='center', fontsize=5, color='white')

    # Arrow
    ax.annotate('', xy=(3.8, 3.5), xytext=(4.5, 3.5), arrowprops=dict(arrowstyle='->', color='#00ff88', lw=3))
    ax.text(4.15, 3.8, 'WebSocket\nJSON', ha='center', fontsize=6, color='#00ff88')

    # Frontend box
    frontend = mpatches.FancyBboxPatch((4.8, 2.0), 3.5, 2.2, boxstyle="round,pad=0.1",
                                        facecolor='#1a2a1e', edgecolor='#50b86c', linewidth=2.5)
    ax.add_patch(frontend)
    ax.text(6.55, 3.8, 'React + TypeScript Frontend', ha='center', fontsize=8, color='#50b86c', fontweight='bold')

    frontend_pages = [
        (5.5, 3.2, 'Page 1: Dashboard\nCPU Registers\nPipeline State'),
        (7.5, 3.2, 'Page 2: Debugger\nMemory / Disasm\nTimeline'),
        (5.5, 2.4, '7 Viz Panels:\nRegisters, Pipeline\nCache, Memory, etc.'),
        (7.5, 2.4, 'Vite Dev Server\nHot Reload\nTypeScript'),
    ]
    for x, y, label in frontend_pages:
        rect = mpatches.FancyBboxPatch((x-0.65, y-0.25), 1.4, 0.5, boxstyle="round,pad=0.02",
                                        facecolor='#2a3a2e', edgecolor='#88ff88', linewidth=0.5)
        ax.add_patch(rect)
        ax.text(x, y, label, ha='center', va='center', fontsize=5, color='white')

    # Browser
    browser = mpatches.FancyBboxPatch((9.0, 2.3), 0.9, 1.6, boxstyle="round,pad=0.1",
                                       facecolor='#3a1a1a', edgecolor='#e8a838', linewidth=2)
    ax.add_patch(browser)
    ax.text(9.45, 3.1, 'Browser', ha='center', va='center', fontsize=6, color='#e8a838', fontweight='bold')
    ax.annotate('', xy=(8.3, 3.1), xytext=(9.0, 3.1), arrowprops=dict(arrowstyle='->', color='#e8a838', lw=2))

    # CPU simulation below
    cpu_sim = mpatches.FancyBboxPatch((0.3, 0.2), 8.0, 1.0, boxstyle="round,pad=0.1",
                                       facecolor='#2a2a1e', edgecolor='#d9664a', linewidth=2)
    ax.add_patch(cpu_sim)
    ax.text(4.3, 0.7, 'Python CPU Simulation (trinary package) — 27 opcodes, 594 tests',
            ha='center', va='center', fontsize=8, color='#d9664a')

    # Connection from CPU sim to backend
    ax.plot([2.05, 2.05], [1.2, 2.0], color='#d9664a', lw=1.5, linestyle='--')

    ax.set_facecolor('#0a0a1a')
    fig.patch.set_facecolor('#0a0a1a')
    ax.set_title('Web Visualizer Architecture — FastAPI + React', fontsize=11, fontweight='bold', color='white')
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'webviz_architecture.pdf'), dpi=150, bbox_inches='tight',
                facecolor=fig.get_facecolor())
    plt.close()
    print("Generated webviz_architecture.pdf")

def simulator_gui():
    """PyQt6 simulator GUI layout."""
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 5.5)
    ax.axis('off')

    # Main window
    main = mpatches.FancyBboxPatch((0.2, 0.2), 9.6, 5.1, boxstyle="round,pad=0.1",
                                    facecolor='#1a1a2e', edgecolor='#4a90d9', linewidth=2)
    ax.add_patch(main)
    ax.text(5, 5.3, 'PyQt6 Trinary Simulator Main Window', ha='center', fontsize=9, color='#4a90d9', fontweight='bold')

    # Display widget
    disp = mpatches.FancyBboxPatch((0.5, 3.0), 4.5, 2.0, boxstyle="round,pad=0.1",
                                    facecolor='#0a0a1a', edgecolor='#50b86c', linewidth=2)
    ax.add_patch(disp)
    ax.text(2.75, 4.0, 'Display Widget\n(64×64 framebuffer)\n8× scale, scanlines',
            ha='center', va='center', fontsize=7, color='#50b86c')

    # Editor
    editor = mpatches.FancyBboxPatch((5.5, 3.0), 4.0, 2.0, boxstyle="round,pad=0.1",
                                      facecolor='#1a1a0e', edgecolor='#e8a838', linewidth=2)
    ax.add_patch(editor)
    ax.text(7.5, 4.0, 'Assembly Editor\nSyntax highlighting\nLine numbers',
            ha='center', va='center', fontsize=7, color='#e8a838')

    # Controls
    ctrl = mpatches.FancyBboxPatch((0.5, 1.0), 3.0, 1.5, boxstyle="round,pad=0.1",
                                    facecolor='#1a2a1e', edgecolor='#00ff88', linewidth=2)
    ax.add_patch(ctrl)
    ax.text(2.0, 1.75, 'Controls:\nRun / Step / Reset\nSpeed Slider',
            ha='center', va='center', fontsize=7, color='#00ff88')

    # Output
    output = mpatches.FancyBboxPatch((4.0, 1.0), 3.0, 1.5, boxstyle="round,pad=0.1",
                                      facecolor='#2a1a1e', edgecolor='#d9664a', linewidth=2)
    ax.add_patch(output)
    ax.text(5.5, 1.75, 'Output Log:\nExecution trace\nError messages',
            ha='center', va='center', fontsize=7, color='#d9664a')

    # Status bar
    status = mpatches.FancyBboxPatch((7.5, 1.0), 2.0, 1.5, boxstyle="round,pad=0.1",
                                      facecolor='#1a1a3e', edgecolor='#9b59b6', linewidth=2)
    ax.add_patch(status)
    ax.text(8.5, 1.75, 'Status:\nCycles\nIPC / CPI',
            ha='center', va='center', fontsize=7, color='#9b59b6')

    # Assembly listing at bottom
    listing = mpatches.FancyBboxPatch((0.5, 0.3), 9.0, 0.5, boxstyle="round,pad=0.02",
                                       facecolor='#0a0a1a', edgecolor='#555', linewidth=1)
    ax.add_patch(listing)
    ax.text(5, 0.55, 'Memory Viewer | Register File | Disassembly | Breakpoints',
            ha='center', va='center', fontsize=6, color='#888')

    ax.set_facecolor('#0a0a0a')
    fig.patch.set_facecolor('#0a0a0a')
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'simulator_gui.pdf'), dpi=150, bbox_inches='tight',
                facecolor=fig.get_facecolor())
    plt.close()
    print("Generated simulator_gui.pdf")

if __name__ == '__main__':
    pipeline_diagram()
    memory_map_diagram()
    system_stack_diagram()
    gpu_hierarchy_diagram()
    opcode_heatmap()
    benchmark_comparison()
    digit_efficiency()
    test_growth()
    cpu_architecture()
    interrupt_flow()
    assembler_flow()
    memory_hierarchy()
    nn_architecture()
    training_flow()
    tal_pipeline()
    instruction_formats()
    ripple_carry_adder()
    decimal_roundtrip()
    cache_organization()
    pipeline_hazard()
    branch_predictor_fsm()
    bus_arbitration()
    palette_colors()
    test_coverage()
    webviz_architecture()
    simulator_gui()
    print("\nAll diagrams generated successfully.")
