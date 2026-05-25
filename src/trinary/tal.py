"""
TAL — Ternary Assembly Language compiler.

Compiles a compact structured language into ternary CPU assembly.
The existing Assembler then converts labels → addresses.
"""

from trinary.conversion import decimal_to_ternary as d2t, ternary_to_decimal as t2d


class TALCompiler:
    def __init__(self):
        self.symbols = {}
        self.lines = []
        self._label_id = 0

    def _new_label(self, prefix="__l"):
        self._label_id += 1
        return f"{prefix}{self._label_id}"

    def compile(self, source):
        self.lines = []
        self.symbols = {}
        self._label_id = 0
        for raw_line in source.split('\n'):
            line = self._clean_line(raw_line)
            if not line:
                continue
            if line.startswith('var '):
                self._handle_var(line)
            elif line.startswith('const '):
                self._handle_const(line)
            elif line.endswith(':'):
                if line.startswith('label '):
                    self.lines.append(line[6:])  # strip "label " prefix
                else:
                    self.lines.append(line)
            else:
                self._handle_instr(line)
        return '\n'.join(self.lines)

    def _clean_line(self, line):
        for m in ('//', '#', ';'):
            if m in line:
                line = line[:line.index(m)]
        return line.strip()

    def _handle_var(self, line):
        parts = line.split()
        name = parts[1]
        spec = parts[2]
        base = int(spec.lstrip('@'))
        self.symbols[name] = ('var', base)

    def _handle_const(self, line):
        parts = line.split()
        name = parts[1]
        raw = parts[3]
        self.symbols[name] = ('const', self._as_int(raw))

    def _as_int(self, s):
        if s in self.symbols:
            return self.symbols[s][1]
        return int(s)

    def _resolve_ternary(self, expr):
        if expr in self.symbols:
            _, val = self.symbols[expr]
            if isinstance(val, int):
                return d2t(val)
            return str(val)
        try:
            return d2t(int(expr))
        except ValueError:
            return expr

    def _mem_addr(self, name):
        return self.symbols[name][1]

    def _is_var(self, name):
        return name in self.symbols and self.symbols[name][0] == 'var'

    def _parse_args(self, rest, count=None):
        parts = [p.strip() for p in rest.split(',')]
        if count is not None and len(parts) != count:
            raise ValueError(f"Expected {count} args got {len(parts)}: {rest}")
        return parts

    # -- instruction generators --

    def _gen_load_imm(self, reg, value_expr):
        self.lines.append(f"    LOAD {reg} {self._resolve_ternary(value_expr)}")

    def _gen_load_mem(self, reg, addr_expr):
        clean = self._clean_addr(addr_expr)
        if self._is_var(addr_expr):
            self.lines.append(f"    LOADM {self._mem_addr(addr_expr)} {reg}")
        else:
            self.lines.append(f"    LOADM {clean} {reg}")

    def _clean_addr(self, expr):
        if isinstance(expr, int):
            return str(expr)
        clean = expr.lstrip('@')
        if clean in self.symbols:
            _, val = self.symbols[clean]
            return str(val)
        return clean

    def _as_addr(self, expr):
        return self._clean_addr(expr)

    def _gen_store_mem(self, addr_expr, reg="R0"):
        clean = self._clean_addr(addr_expr)
        if self._is_var(addr_expr):
            self.lines.append(f"    STOREM {self._mem_addr(addr_expr)} {reg}")
        else:
            self.lines.append(f"    STOREM {clean} {reg}")

    def _gen_mov_var_to_var(self, dst_name, src_name):
        self._gen_load_mem("R0", src_name)
        self._gen_store_mem(dst_name, "R0")

    def _gen_store_imm(self, addr_expr, value_expr):
        self._gen_load_imm("R0", value_expr)
        self._gen_store_mem(addr_expr, "R0")

    def _gen_load_io(self, reg, port_expr):
        self.lines.append(f"    LOADM {self._clean_addr(port_expr)} {reg}")

    def _gen_store_io(self, port_expr, reg="R0"):
        self.lines.append(f"    STOREM {self._clean_addr(port_expr)} {reg}")

    def _gen_draw_pixel(self, x_expr, y_expr, color_expr):
        self._gen_load_mem("R1", y_expr)
        self._gen_load_mem("R0", x_expr)
        self._gen_load_imm("R2", color_expr)
        self.lines.append("    PUSH R0")
        self.lines.append("    PUSH R1")
        self.lines.append("    PUSH R2")
        self.lines.append("    LOAD R3 1101001")
        self.lines.append("    LOAD R0 2101")
        self.lines.append("    MUL R1 R0")
        self.lines.append("    ADD R3 R1")
        self.lines.append("    POP R2")
        self.lines.append("    POP R1")
        self.lines.append("    POP R0")
        self.lines.append("    ADD R3 R0")
        self.lines.append("    STOREM R3 R2")

    def _gen_array_store(self, base_addr, idx_expr, src_var):
        base_tern = d2t(base_addr)
        self._gen_load_mem("R0", idx_expr)
        self.lines.append(f"    LOAD R1 {base_tern}")
        self.lines.append("    ADD R0 R1")
        self.lines.append("    PUSH R0")
        self._gen_load_mem("R0", src_var)
        self.lines.append("    POP R1")
        self.lines.append("    STOREM R1 R0")

    # -- instruction handlers --

    def _handle_instr(self, line):
        idx = line.find(' ')
        if idx == -1:
            self.lines.append(f"    {line}")
            return
        op, rest = line[:idx], line[idx:].strip()
        fn = getattr(self, f'_op_{op}', None)
        if fn:
            fn(rest)
        else:
            self.lines.append(f"    {line}")

    def _op_store(self, rest):
        args = self._parse_args(rest, 2)
        dst, src = args
        clean_dst = self._clean_addr(dst)
        if clean_dst != dst:
            addr = int(clean_dst)
            if self._is_var(src):
                self._gen_load_mem("R0", src)
                self.lines.append(f"    STOREM {addr} R0")
            else:
                self._gen_store_imm(addr, src)
        elif self._is_var(src):
            self._gen_mov_var_to_var(dst, src)
        else:
            self._gen_store_imm(dst, src)

    def _op_copy(self, rest):
        self._op_store(rest)

    def _op_add(self, rest):
        args = self._parse_args(rest, 2)
        var, val = args
        addr = self._mem_addr(var)
        self._gen_load_mem("R0", var)
        self._gen_load_imm("R1", val)
        self.lines.append("    ADD R0 R1")
        self._gen_store_mem(var, "R0")

    def _op_sub(self, rest):
        args = self._parse_args(rest, 2)
        var, val = args
        addr = self._mem_addr(var)
        self._gen_load_mem("R0", var)
        self._gen_load_imm("R1", val)
        self.lines.append("    SUB R0 R1")
        self._gen_store_mem(var, "R0")

    def _op_inc(self, rest):
        self._op_add(f"{rest}, 1")

    def _op_dec(self, rest):
        self._op_sub(f"{rest}, 1")

    def _op_load(self, rest):
        args = self._parse_args(rest, 2)
        var, port = args
        self._gen_load_io("R0", port)
        self._gen_store_mem(var, "R0")

    def _op_save(self, rest):
        args = self._parse_args(rest, 2)
        port, var = args
        self._gen_load_mem("R0", var)
        self._gen_store_io(port, "R0")

    def _op_write(self, rest):
        args = self._parse_args(rest, 2)
        port, val = args
        if self._is_var(val):
            self._gen_load_mem("R0", val)
        else:
            self._gen_load_imm("R0", val)
        self._gen_store_io(port, "R0")

    def _op_if_eq(self, rest):
        args = self._parse_args(rest, 3)
        var, target, label = args
        self._gen_load_mem("R1", var)
        if self._is_var(target):
            self._gen_load_mem("R2", target)
        else:
            self._gen_load_imm("R2", target)
        self.lines.append("    CMP R1 R2")
        self.lines.append(f"    JZ {label}")

    def _op_if_ne(self, rest):
        args = self._parse_args(rest, 3)
        var, target, label = args
        self._gen_load_mem("R1", var)
        if self._is_var(target):
            self._gen_load_mem("R2", target)
        else:
            self._gen_load_imm("R2", target)
        self.lines.append("    CMP R1 R2")
        self.lines.append(f"    JNZ {label}")

    def _op_jmp(self, rest):
        self.lines.append(f"    JMP {rest}")

    def _op_goto(self, rest):
        self.lines.append(f"    JMP {rest}")

    def _op_draw(self, rest):
        args = self._parse_args(rest, 3)
        self._gen_draw_pixel(args[0], args[1], args[2])

    def _op_clear(self, rest):
        args = self._parse_args(rest, 2)
        self._gen_draw_pixel(args[0], args[1], "0")

    def _op_wrap_inc(self, rest):
        """wrap_inc var, limit, wrap_label  → inc var; if var==limit: goto wrap_label"""
        args = self._parse_args(rest, 3)
        var, limit, wrap_label = args
        self._op_inc(var)
        self._gen_load_mem("R1", var)
        self._gen_load_imm("R2", limit)
        self.lines.append("    CMP R1 R2")
        self.lines.append(f"    JZ {wrap_label}")

    def _op_div(self, rest): pass

    def _op_mul(self, rest): pass

    # -- array access: body_x / body_y
    # body_x ARRAY_BASE idx_var dest_var
    # set_body_x ARRAY_BASE idx_var src_var
    # (same for body_y)

    def _op_body_x(self, rest):
        args = self._parse_args(rest, 2)
        self._gen_array_read(20, args[0], args[1])

    def _op_body_y(self, rest):
        args = self._parse_args(rest, 2)
        self._gen_array_read(84, args[0], args[1])

    def _op_set_body_x(self, rest):
        args = self._parse_args(rest, 2)
        self._gen_array_write(20, args[0], args[1])

    def _op_set_body_y(self, rest):
        args = self._parse_args(rest, 2)
        self._gen_array_write(84, args[0], args[1])

    def _gen_array_read(self, base_addr, idx_expr, dest_var):
        base_tern = d2t(base_addr)
        self._gen_load_mem("R0", idx_expr)
        self.lines.append(f"    LOAD R1 {base_tern}")
        self.lines.append("    ADD R0 R1")
        self.lines.append("    LOADM R0 R0")
        self._gen_store_mem(dest_var, "R0")

    def _gen_array_write(self, base_addr, idx_expr, src_var):
        base_tern = d2t(base_addr)
        self._gen_load_mem("R0", idx_expr)
        self.lines.append(f"    LOAD R1 {base_tern}")
        self.lines.append("    ADD R0 R1")
        self.lines.append("    PUSH R0")
        self._gen_load_mem("R0", src_var)
        self.lines.append("    POP R1")
        self.lines.append("    STOREM R1 R0")


def compile_tal(source):
    return TALCompiler().compile(source)


def compile_and_assemble(source):
    from trinary.assembler import Assembler
    asm = Assembler()
    tal_asm = compile_tal(source)
    return asm.assemble(tal_asm)
