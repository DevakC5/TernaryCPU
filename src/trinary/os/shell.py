from trinary.os.commands import COMMANDS
from trinary.os.constants import COLOR_ERROR, COLOR_TEXT


class Shell:
    def __init__(self, terminal, syscalls, kernel):
        self.terminal = terminal
        self.syscalls = syscalls
        self.kernel = kernel

    def execute(self, line):
        if not line:
            return
        parts = line.split()
        cmd_name = parts[0].upper()
        args = parts[1:]
        handler = COMMANDS.get(cmd_name)
        if handler is None:
            self.syscalls.println(f"Unknown command: {cmd_name}", COLOR_ERROR)
            self.syscalls.println("Type HELP for available commands.", COLOR_TEXT)
        else:
            handler(args, self.syscalls, self.kernel)
