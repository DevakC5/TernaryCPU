"""
CPU-based Snake Game — game logic runs on the ternary CPU via assembly.
"""

from trinary.cpu import CPU
from trinary.memory import Memory
from trinary.assembler import Assembler
from trinary.conversion import decimal_to_ternary as d2t, ternary_to_decimal as t2d


# Memory map:
#   0: game_state (0=play, 1=game_over)
#   1: direction (0=up, 1=down, 2=left, 3=right)
#   2: next_dir
#   3: food_x  4: food_y
#   5: score
#   6: head_x  7: head_y
#   8: head_idx  9: tail_idx
#  10: snake_len
#  11: tick_count
#  12: grow_flag
#  13: prev_tail_x  14: prev_tail_y
#  15: new_head_x  16: new_head_y
# 20-83: body_x[0..63]   84-147: body_y[0..63]
#
# Keyboard: 9000   Frame-done: 9999   VRAM: 1000-5095
# Colors: 0=black, 2=white(snake), 3=red(food), 4=green(head)

CPU_SNAKE_SOURCE = r"""
init:
    LOAD R0 0
    STOREM 0 R0
    LOAD R0 10
    STOREM 1 R0
    STOREM 2 R0
    LOAD R0 1012
    STOREM 6 R0
    STOREM 7 R0
    LOAD R0 0
    STOREM 8 R0
    STOREM 9 R0
    LOAD R0 10
    STOREM 10 R0
    STOREM 15 R0
    STOREM 16 R0
    LOAD R0 1012
    STOREM 20 R0
    STOREM 84 R0
    LOAD R0 1011
    STOREM 21 R0
    LOAD R0 1012
    STOREM 85 R0
    LOAD R0 1010
    STOREM 22 R0
    LOAD R0 1012
    STOREM 86 R0
    LOAD R0 202
    STOREM 3 R0
    STOREM 4 R0
    LOAD R0 0
    STOREM 5 R0
    STOREM 11 R0
    STOREM 12 R0

    LOAD R0 11020002
    LOAD R1 11
    STOREM R0 R1
    LOAD R0 11020001
    LOAD R1 2
    STOREM R0 R1
    LOAD R0 11020000
    LOAD R1 2
    STOREM R0 R1
    LOAD R0 10011012
    LOAD R1 10
    STOREM R0 R1

    JMP game_loop

game_loop:
    LOADM 0 R1
    LOAD R2 1
    CMP R1 R2
    JZ game_over

    LOADM 9000 R0
    LOAD R1 0
    CMP R0 R1
    JZ done_keys
    STOREM 9000 R1

    LOAD R1 11102
    CMP R0 R1
    JZ key_up
    LOAD R1 10020
    CMP R0 R1
    JZ key_up
    LOAD R1 11021
    CMP R0 R1
    JZ key_down
    LOAD R1 10002
    CMP R0 R1
    JZ key_down
    LOAD R1 10121
    CMP R0 R1
    JZ key_left
    LOAD R1 2102
    CMP R0 R1
    JZ key_left
    LOAD R1 10201
    CMP R0 R1
    JZ key_right
    LOAD R1 2112
    CMP R0 R1
    JZ key_right
    LOAD R1 11100
    CMP R0 R1
    JZ key_restart
    JMP done_keys

key_up:
    LOAD R1 0
    JMP try_set_dir
key_down:
    LOAD R1 1
    JMP try_set_dir
key_left:
    LOAD R1 2
    JMP try_set_dir
key_right:
    LOAD R1 3

try_set_dir:
    LOADM 1 R2
    LOAD R3 0
    CMP R1 R3
    JZ check_up
    LOAD R3 1
    CMP R1 R3
    JZ check_down
    LOAD R3 2
    CMP R1 R3
    JZ check_left
    JMP check_right

check_up:
    LOADM 1 R2
    LOAD R3 1
    CMP R2 R3
    JZ done_keys
    STOREM 2 R1
    JMP done_keys

check_down:
    LOADM 1 R2
    LOAD R3 0
    CMP R2 R3
    JZ done_keys
    STOREM 2 R1
    JMP done_keys

check_left:
    LOADM 1 R2
    LOAD R3 3
    CMP R2 R3
    JZ done_keys
    STOREM 2 R1
    JMP done_keys

check_right:
    LOADM 1 R2
    LOAD R3 2
    CMP R2 R3
    JZ done_keys
    STOREM 2 R1
    JMP done_keys

key_restart:
    JMP init

done_keys:
    LOADM 11 R0
    LOAD R1 1
    ADD R0 R1
    STOREM 11 R0
    LOAD R1 20
    CMP R0 R1
    JZ do_move
    JMP skip_move

do_move:
    LOADM 2 R0
    STOREM 1 R0

    LOADM 1 R0
    LOAD R1 0
    CMP R0 R1
    JZ move_up
    LOAD R1 1
    CMP R0 R1
    JZ move_down
    LOAD R1 2
    CMP R0 R1
    JZ move_left
    LOAD R1 3
    CMP R0 R1
    JZ move_right

move_up:
    LOADM 7 R0
    LOAD R1 0
    CMP R0 R1
    JZ wall_collision
    LOAD R1 1
    SUB R0 R1
    STOREM 16 R0
    LOADM 6 R0
    STOREM 15 R0
    JMP check_self

move_down:
    LOADM 7 R0
    LOAD R1 2100
    CMP R0 R1
    JZ wall_collision
    LOAD R1 1
    ADD R0 R1
    STOREM 16 R0
    LOADM 6 R0
    STOREM 15 R0
    JMP check_self

move_left:
    LOADM 6 R0
    LOAD R1 0
    CMP R0 R1
    JZ wall_collision
    LOAD R1 1
    SUB R0 R1
    STOREM 15 R0
    LOADM 7 R0
    STOREM 16 R0
    JMP check_self

move_right:
    LOADM 6 R0
    LOAD R1 2100
    CMP R0 R1
    JZ wall_collision
    LOAD R1 1
    ADD R0 R1
    STOREM 15 R0
    LOADM 7 R0
    STOREM 16 R0

check_self:
    LOADM 9 R0
    LOADM 8 R3
self_loop:
    PUSH R3
    LOAD R2 202
    ADD R0 R2
    LOADM R0 R2
    LOADM 15 R1
    CMP R2 R1
    JNZ self_next
    LOAD R2 2200
    ADD R0 R2
    LOADM R0 R2
    LOADM 16 R1
    CMP R2 R1
    JNZ self_next
    LOAD R0 1
    STOREM 0 R0
    POP R3
    JMP move_done
self_next:
    POP R3
    CMP R0 R3
    JZ self_done
    LOAD R2 1
    ADD R0 R2
    LOAD R2 2101
    CMP R0 R2
    JZ self_wrap
    JMP self_loop
self_wrap:
    LOAD R0 0
    JMP self_loop

self_done:
    LOADM 15 R0
    LOADM 3 R1
    CMP R0 R1
    JZ eat_food
    LOADM 16 R0
    LOADM 4 R1
    CMP R0 R1
    JZ eat_food
    LOAD R0 0
    STOREM 12 R0
    JMP update_body

eat_food:
    LOAD R0 1
    STOREM 12 R0
    LOADM 5 R0
    LOAD R1 1
    ADD R0 R1
    STOREM 5 R0

find_food_loop:
    LOADM 3 R0
    LOAD R1 1
    ADD R0 R1
    LOAD R1 2101
    CMP R0 R1
    JZ ff_wrap_x
    JMP ff_check_occupied
ff_wrap_x:
    LOAD R0 0
    LOADM 4 R1
    LOAD R2 1
    ADD R1 R2
    LOAD R2 2101
    CMP R1 R2
    JZ ff_wrap_y
    STOREM 4 R1
    JMP ff_check_occupied
ff_wrap_y:
    LOAD R1 0
    STOREM 4 R1

ff_check_occupied:
    STOREM 3 R0
    PUSH R0
    LOADM 9 R2
    LOADM 8 R3
ff_occ_loop:
    PUSH R3
    LOAD R1 202
    ADD R2 R1
    LOADM R1 R1
    LOADM 3 R0
    CMP R1 R0
    JNZ ff_occ_next
    LOAD R1 2200
    ADD R2 R1
    LOADM R1 R1
    LOADM 4 R0
    CMP R1 R0
    JNZ ff_occ_next
    POP R3
    POP R0
    JMP find_food_loop
ff_occ_next:
    POP R3
    CMP R2 R3
    JZ ff_occ_done
    LOAD R1 1
    ADD R2 R1
    LOAD R1 2101
    CMP R2 R1
    JZ ff_occ_wrap
    JMP ff_occ_loop
ff_occ_wrap:
    LOAD R2 0
    JMP ff_occ_loop
ff_occ_done:
    POP R0

update_body:
    LOADM 9 R0
    STOREM 13 R0
    LOADM 7 R0
    STOREM 14 R0

    LOADM 8 R0
    LOAD R1 1
    ADD R0 R1
    LOAD R1 2101
    CMP R0 R1
    JZ ub_head_wrap
    JMP ub_head_cont
ub_head_wrap:
    LOAD R0 0
ub_head_cont:
    STOREM 8 R0
    LOAD R1 202
    ADD R0 R1
    LOADM 15 R1
    STOREM R0 R1
    LOAD R0 2200
    ADD R0 R1
    LOADM 16 R1
    STOREM R0 R1

    LOADM 12 R0
    LOAD R1 1
    CMP R0 R1
    JZ ub_grow

    LOADM 9 R0
    LOAD R1 1
    ADD R0 R1
    LOAD R1 2101
    CMP R0 R1
    JZ ub_tail_wrap
    JMP ub_tail_cont
ub_tail_wrap:
    LOAD R0 0
ub_tail_cont:
    STOREM 9 R0
    LOAD R0 0
    STOREM 12 R0
    JMP move_done

ub_grow:
    LOADM 10 R0
    LOAD R1 1
    ADD R0 R1
    STOREM 10 R0
    LOAD R0 0
    STOREM 12 R0

move_done:
    LOAD R0 0
    STOREM 11 R0

skip_move:
    LOADM 0 R0
    LOAD R1 1
    CMP R0 R1
    JZ render_over

    LOADM 15 R0
    LOADM 16 R1
    LOAD R2 11
    PUSH R0
    PUSH R1
    PUSH R2
    LOAD R3 1101001
    LOAD R0 2101
    MUL R1 R0
    ADD R3 R1
    POP R2
    POP R1
    POP R0
    ADD R3 R0
    STOREM R3 R2

    LOADM 12 R0
    LOAD R1 1
    CMP R0 R1
    JZ skip_tail_clear

    LOADM 13 R0
    LOADM 14 R1
    LOAD R2 0
    PUSH R0
    PUSH R1
    PUSH R2
    LOAD R3 1101001
    LOAD R0 2101
    MUL R1 R0
    ADD R3 R1
    POP R2
    POP R1
    POP R0
    ADD R3 R0
    STOREM R3 R2

skip_tail_clear:
    LOADM 3 R0
    LOADM 4 R1
    LOAD R2 10
    PUSH R0
    PUSH R1
    PUSH R2
    LOAD R3 1101001
    LOAD R0 2101
    MUL R1 R0
    ADD R3 R1
    POP R2
    POP R1
    POP R0
    ADD R3 R0
    STOREM R3 R2

    LOAD R0 1
    STOREM 9999 R0
    JMP game_loop

render_over:
    LOAD R0 1
    STOREM 9999 R0
    JMP game_loop

wall_collision:
    LOAD R0 1
    STOREM 0 R0
    JMP move_done

game_over:
    LOAD R0 1
    STOREM 9999 R0
    JMP game_loop
"""


TAL_SNAKE_SOURCE = r"""
var game_state @0
var direction @1
var next_dir @2
var food_x @3
var food_y @4
var score @5
var head_x @6
var head_y @7
var head_idx @8
var tail_idx @9
var snake_len @10
var tick_count @11
var grow_flag @12
var prev_tail_x @13
var prev_tail_y @14
var new_head_x @15
var new_head_y @16
var loop_i @17
var temp_x @18
var temp_y @19

const RIGHT = 3
const LEFT = 2
const UP = 0
const DOWN = 1
const TICK_DELAY = 6
const COL_HEAD = 4
const COL_BODY = 2
const COL_FOOD = 3
const KEY_W = 119
const KEY_A = 97
const KEY_S = 115
const KEY_D = 100
const KEY_Z = 122
const KEY_W_CAPS = 87
const KEY_A_CAPS = 65
const KEY_S_CAPS = 83
const KEY_D_CAPS = 68
const KEY_Z_CAPS = 90
const MAX_IDX = 64
const MAX_GRID = 63
const KEY_ADDR = 9000
const FRAME_DONE = 9999

init:
    store game_state, 0
    store direction, RIGHT
    store next_dir, RIGHT
    store head_x, 32
    store head_y, 32
    store head_idx, 2
    store tail_idx, 0
    store snake_len, 3
    store score, 0
    store tick_count, 0
    store grow_flag, 0
    store new_head_x, 32
    store new_head_y, 32
    store @20, 30
    store @84, 32
    store @21, 31
    store @85, 32
    store @22, 32
    store @86, 32
    store food_x, 20
    store food_y, 20
    draw head_x, head_y, COL_HEAD
    store temp_x, 31
    store temp_y, 32
    draw temp_x, temp_y, COL_BODY
    store temp_x, 30
    draw temp_x, temp_y, COL_BODY
    draw food_x, food_y, COL_FOOD
    write FRAME_DONE, 1
    jmp game_loop

game_loop:
    if_eq game_state, 1, game_over_label
    load temp_x, KEY_ADDR
    if_eq temp_x, 0, @done_keys
    write KEY_ADDR, 0
    if_eq temp_x, KEY_W, @key_up
    if_eq temp_x, KEY_W_CAPS, @key_up
    if_eq temp_x, KEY_S, @key_down
    if_eq temp_x, KEY_S_CAPS, @key_down
    if_eq temp_x, KEY_A, @key_left
    if_eq temp_x, KEY_A_CAPS, @key_left
    if_eq temp_x, KEY_D, @key_right
    if_eq temp_x, KEY_D_CAPS, @key_right
    if_eq temp_x, KEY_Z, init
    if_eq temp_x, KEY_Z_CAPS, init
    jmp @done_keys

@key_up:
    if_eq direction, DOWN, @done_keys
    store next_dir, UP
    jmp @done_keys

@key_down:
    if_eq direction, UP, @done_keys
    store next_dir, DOWN
    jmp @done_keys

@key_left:
    if_eq direction, RIGHT, @done_keys
    store next_dir, LEFT
    jmp @done_keys

@key_right:
    if_eq direction, LEFT, @done_keys
    store next_dir, RIGHT

@done_keys:
    inc tick_count
    if_ne tick_count, TICK_DELAY, @skip_move

do_move:
    copy direction, next_dir
    copy prev_tail_x, new_head_x
    copy prev_tail_y, new_head_y
    copy new_head_x, head_x
    copy new_head_y, head_y

    if_eq direction, UP, @move_up
    if_eq direction, DOWN, @move_down
    if_eq direction, LEFT, @move_left
    if_eq direction, RIGHT, @move_right
    jmp @check_self

@move_up:
    if_eq head_y, 0, wall_collision
    dec new_head_y
    jmp @check_wall_self

@move_down:
    if_eq head_y, MAX_GRID, wall_collision
    inc new_head_y
    jmp @check_wall_self

@move_left:
    if_eq head_x, 0, wall_collision
    dec new_head_x
    jmp @check_wall_self

@move_right:
    if_eq head_x, MAX_GRID, wall_collision
    inc new_head_x

@check_wall_self:

@check_self:
    copy loop_i, tail_idx

@self_loop:
    body_x loop_i, temp_x
    if_ne temp_x, new_head_x, @self_next
    body_y loop_i, temp_y
    if_eq temp_y, new_head_y, self_hit
@self_next:
    if_eq loop_i, head_idx, @self_done
    inc loop_i
    if_eq loop_i, MAX_IDX, @self_wrap
    jmp @self_loop
@self_wrap:
    store loop_i, 0
    jmp @self_loop

@self_done:
    if_ne new_head_x, food_x, @no_eat
    if_ne new_head_y, food_y, @no_eat
    jmp @eat_food
@no_eat:
    store grow_flag, 0
    jmp @update_body

@eat_food:
    store grow_flag, 1
    inc score

@find_food:
    inc food_x
    if_eq food_x, MAX_IDX, @ff_wrap_x
    jmp @ff_check
@ff_wrap_x:
    store food_x, 0
    inc food_y
    if_eq food_y, MAX_IDX, @ff_wrap_y
    jmp @ff_check
@ff_wrap_y:
    store food_y, 0
@ff_check:
    copy loop_i, tail_idx
@ff_occ_loop:
    body_x loop_i, temp_x
    if_ne temp_x, food_x, @ff_occ_next
    body_y loop_i, temp_y
    if_eq temp_y, food_y, @find_food
@ff_occ_next:
    if_eq loop_i, head_idx, @ff_done
    inc loop_i
    if_eq loop_i, MAX_IDX, @ff_occ_wrap
    jmp @ff_occ_loop
@ff_occ_wrap:
    store loop_i, 0
    jmp @ff_occ_loop
@ff_done:

@update_body:
    copy prev_tail_x, head_x
    copy prev_tail_y, head_y
    copy head_x, new_head_x
    copy head_y, new_head_y

    inc head_idx
    if_eq head_idx, MAX_IDX, @ub_head_wrap
    jmp @ub_head_cont
@ub_head_wrap:
    store head_idx, 0
@ub_head_cont:
    set_body_x head_idx, new_head_x
    set_body_y head_idx, new_head_y

    if_eq grow_flag, 1, @ub_grow
    inc tail_idx
    if_eq tail_idx, MAX_IDX, @ub_tail_wrap
    jmp @ub_tail_cont
@ub_tail_wrap:
    store tail_idx, 0
@ub_tail_cont:
    store grow_flag, 0
    jmp @move_done

@ub_grow:
    inc snake_len
    store grow_flag, 0

@move_done:
    store tick_count, 0

@skip_move:
    if_eq game_state, 1, @skip_render
    draw new_head_x, new_head_y, COL_HEAD
    draw prev_tail_x, prev_tail_y, COL_BODY
    if_eq grow_flag, 1, @skip_tail
    body_x tail_idx, temp_x
    body_y tail_idx, temp_y
    clear temp_x, temp_y
@skip_tail:
    draw food_x, food_y, COL_FOOD
@skip_render:
    write FRAME_DONE, 1
    jmp game_loop

wall_collision:
    store game_state, 1
    jmp @done_collision

self_hit:
    store game_state, 1

@done_collision:
    store tick_count, 0
    jmp @skip_move

game_over_label:
    write FRAME_DONE, 1
    jmp game_loop
"""


class TALSnake:
    def __init__(self, display=None, tick_delay=6):
        from trinary.tal import compile_and_assemble
        self.memory = Memory(10000)
        self.cpu = CPU(memory=self.memory)
        program, self.labels = compile_and_assemble(TAL_SNAKE_SOURCE)
        self.cpu.load_program(program)
        self.fb = display or CPUSnakeDisplay(memory=self.memory)
        self.state = {}
        self._frame_done_addr = 9999
        self._game_state_addr = 0
        self._first_frame = True
        self.reset()

    def reset(self):
        self.cpu = CPU(memory=self.memory)
        self.memory.clear_all()
        from trinary.tal import compile_and_assemble
        program, self.labels = compile_and_assemble(TAL_SNAKE_SOURCE)
        self.cpu.load_program(program)
        self.cpu.pc = self.labels.get("init", 0)
        self.cpu.halted = False
        self._first_frame = True

    def _step_until_frame_done(self, max_steps=5000):
        self.memory.store(self._frame_done_addr, "0")
        steps = 0
        while steps < max_steps:
            self.cpu.step()
            steps += 1
            if self.cpu.halted:
                break
            if self.memory.load(self._frame_done_addr) != "0":
                break
        return steps

    def init(self):
        self.reset()

    def update(self):
        if self._first_frame:
            self._first_frame = False
            self.memory.store(self._frame_done_addr, "0")
            self._step_until_frame_done()
        self._step_until_frame_done()

    def render(self):
        gs = self.memory.load(self._game_state_addr)
        self.state["game_over"] = t2d(gs) == 1
        self.state["score"] = t2d(self.memory.load(5))
        self.fb.sync(self.memory)

    def shutdown(self):
        pass


class CPUSnakeDisplay:
    def __init__(self, memory=None, width=64, height=64):
        self.width = width
        self.height = height
        self._pixels = [[0] * width for _ in range(height)]
        if memory is not None:
            self.sync(memory)

    def clear(self, color=0):
        for y in range(self.height):
            row = self._pixels[y]
            for x in range(self.width):
                row[x] = color

    def sync(self, memory):
        for y in range(self.height):
            row = self._pixels[y]
            base = 1000 + y * 64
            for x in range(self.width):
                raw = memory.load(base + x)
                val = t2d(raw)
                row[x] = val if 0 <= val <= 8 else 0

    def get_buffer(self):
        return self._pixels


class CPUSnake:
    def __init__(self, display=None):
        self.memory = Memory(10000)
        self.cpu = CPU(memory=self.memory)
        self.asm = Assembler()
        self.program, self.labels = self.asm.assemble(CPU_SNAKE_SOURCE)
        self.fb = display or CPUSnakeDisplay(memory=self.memory)
        self.state = {}
        self._frame_done_addr = 9999
        self._game_state_addr = 0
        self._first_frame = True
        self.reset()

    def reset(self):
        self.cpu = CPU(memory=self.memory)
        self.memory.clear_all()
        self.cpu.load_program(self.program)
        self.cpu.pc = self.labels.get("init", 0)
        self.cpu.halted = False
        self._first_frame = True

    def init(self):
        self.reset()

    def _step_until_frame_done(self, max_steps=5000):
        self.memory.store(self._frame_done_addr, "0")
        steps = 0
        while steps < max_steps:
            self.cpu.step()
            steps += 1
            if self.cpu.halted:
                break
            if self.memory.load(self._frame_done_addr) != "0":
                break
        return steps

    def update(self):
        if self._first_frame:
            self._first_frame = False
            self.memory.store(self._frame_done_addr, "0")
            self._step_until_frame_done()

        self._step_until_frame_done()

    def render(self):
        gs = self.memory.load(self._game_state_addr)
        self.state["game_over"] = t2d(gs) == 1
        self.state["score"] = t2d(self.memory.load(5))
        self.fb.sync(self.memory)

    def shutdown(self):
        pass


def create_engine(fb=None):
    return CPUSnake(display=fb)
