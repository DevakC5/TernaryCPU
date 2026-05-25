from trinary.os.constants import VERSION, NAME, COLOR_INFO, COLOR_ERROR, COLOR_TEXT
from trinary.conversion import decimal_to_ternary as d2t


COMMANDS = {}
DESCRIPTIONS = {}


def register(name, desc, fn):
    COMMANDS[name.upper()] = fn
    DESCRIPTIONS[name.upper()] = desc


def cmd_help(args, syscalls, kernel):
    syscalls.println("COMMANDS:", COLOR_INFO)
    for name in sorted(COMMANDS):
        desc = DESCRIPTIONS.get(name, "")
        syscalls.println(f"  {name:12} {desc}", COLOR_TEXT)
    syscalls.println("")
    syscalls.println("Type a command and press Enter.", COLOR_TEXT)


def cmd_cls(args, syscalls, kernel):
    syscalls.clear_screen()


def cmd_mem(args, syscalls, kernel):
    mem = kernel.cpu.memory
    start = 0
    end = min(16, mem.size)
    if args:
        try:
            start = int(args[0])
            end = min(start + 16, mem.size)
        except ValueError:
            pass
    syscalls.println(f"MEMORY DUMP {start}-{end-1}:", COLOR_INFO)
    for addr in range(start, end):
        val = mem.load(addr)
        syscalls.println(f"  [{addr:3}] = {val}", COLOR_TEXT)


def cmd_regs(args, syscalls, kernel):
    regs = kernel.cpu.registers.dump()
    syscalls.println("REGISTERS:", COLOR_INFO)
    for name, val in regs.items():
        syscalls.println(f"  {name}: {val}", COLOR_TEXT)


def cmd_clear(args, syscalls, kernel):
    kernel.cpu.memory.clear_all()
    DisplayMemoryMap().clear(kernel.cpu.memory)
    from trinary.display.text_display import DisplayMemoryMap
    syscalls.println("Memory cleared.", COLOR_INFO)


def cmd_about(args, syscalls, kernel):
    syscalls.println(f"{NAME} v{VERSION}", COLOR_INFO)
    syscalls.println("Ternary (base-3) fantasy console OS", COLOR_TEXT)
    syscalls.println("64x64 framebuffer | 26 CPU opcodes", COLOR_TEXT)
    syscalls.println("256-word RAM | Assembler | PyQt6 UI", COLOR_TEXT)


def cmd_demo(args, syscalls, kernel):
    demos = {
        "PIXEL": "Pixel test",
        "COLORS": "Color bars",
        "BOUNCE": "Bouncing box",
        "NOISE": "Random noise",
    }
    if not args:
        syscalls.println("Available demos:", COLOR_INFO)
        for name, desc in demos.items():
            syscalls.println(f"  DEMO {name:8} {desc}", COLOR_TEXT)
        return
    name = args[0].upper()
    if name == "PIXEL":
        from trinary.demo_graphics import demo_pixel_test
        syscalls.clear_screen()
        demo_pixel_test(kernel.fb)
    elif name == "COLORS":
        from trinary.demo_graphics import demo_color_bars
        syscalls.clear_screen()
        demo_color_bars(kernel.fb)
    elif name == "BOUNCE":
        from trinary.demo_graphics import demo_bouncing_box
        syscalls.clear_screen()
        demo_bouncing_box(kernel.fb)
    elif name == "NOISE":
        from trinary.demo_graphics import demo_noise
        syscalls.clear_screen()
        demo_noise(kernel.fb)
    else:
        syscalls.println(f"Unknown demo: {name}", COLOR_ERROR)


def cmd_run(args, syscalls, kernel):
    if not args:
        syscalls.println("Usage: RUN <program>", COLOR_ERROR)
        syscalls.println("Available: COUNTDOWN FIBONACCI", COLOR_TEXT)
        return
    prog_name = args[0].upper()
    from trinary.ui.demos import DEMOS
    from trinary.assembler import Assembler
    source = DEMOS.get(prog_name)
    if source is None:
        syscalls.println(f"Unknown program: {prog_name}", COLOR_ERROR)
        return
    asm = Assembler()
    program, labels = asm.assemble(source)
    kernel.cpu.load_program(program)
    syscalls.println(f"Loaded '{prog_name}' ({len(program)} instr)", COLOR_INFO)
    kernel.cpu.run(verbose=False)
    syscalls.println("Program finished.", COLOR_INFO)


def cmd_halt(args, syscalls, kernel):
    syscalls.println("Halting CPU...", COLOR_INFO)
    kernel.cpu.halted = True
    kernel.running = False


def cmd_cpu(args, syscalls, kernel):
    syscalls.println("CPU INFO:", COLOR_INFO)
    syscalls.println(f"  PC: {kernel.cpu.pc}", COLOR_TEXT)
    syscalls.println(f"  Cycles: {kernel.cpu.cycles}", COLOR_TEXT)
    syscalls.println(f"  Halted: {kernel.cpu.halted}", COLOR_TEXT)
    syscalls.println(f"  SP: {kernel.cpu.sp}", COLOR_TEXT)
    syscalls.println(f"  IFlag: {kernel.cpu.iflag}", COLOR_TEXT)


register("HELP", "Show this help", cmd_help)
register("CLS", "Clear screen", cmd_cls)
register("MEM", "Dump memory [addr]", cmd_mem)
register("REGS", "Show registers", cmd_regs)
register("CLEAR", "Reset memory", cmd_clear)
register("ABOUT", "System info", cmd_about)
register("DEMO", "Run graphics demo", cmd_demo)
register("RUN", "Load and run program", cmd_run)
register("HALT", "Stop CPU", cmd_halt)
register("CPU", "CPU status", cmd_cpu)
