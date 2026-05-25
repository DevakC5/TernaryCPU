"""
Test the TAL-compiled snake game.
"""
from trinary.tal import compile_tal, compile_and_assemble
from trinary.conversion import ternary_to_decimal as t2d, decimal_to_ternary as d2t
from trinary.cpu import CPU
from trinary.memory import Memory
from trinary.assembler import Assembler

SNAKE_TAL = r"""
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

label init:
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

label game_loop:
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

label @key_up:
    if_eq direction, DOWN, @done_keys
    store next_dir, UP
    jmp @done_keys

label @key_down:
    if_eq direction, UP, @done_keys
    store next_dir, DOWN
    jmp @done_keys

label @key_left:
    if_eq direction, RIGHT, @done_keys
    store next_dir, LEFT
    jmp @done_keys

label @key_right:
    if_eq direction, LEFT, @done_keys
    store next_dir, RIGHT

label @done_keys:
    inc tick_count
    if_ne tick_count, TICK_DELAY, @skip_move

label do_move:
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

label @move_up:
    if_eq head_y, 0, wall_collision
    dec new_head_y
    jmp @check_wall_self

label @move_down:
    if_eq head_y, MAX_GRID, wall_collision
    inc new_head_y
    jmp @check_wall_self

label @move_left:
    if_eq head_x, 0, wall_collision
    dec new_head_x
    jmp @check_wall_self

label @move_right:
    if_eq head_x, MAX_GRID, wall_collision
    inc new_head_x

label @check_wall_self:

label @check_self:
    copy loop_i, tail_idx

label @self_loop:
    body_x loop_i, temp_x
    if_ne temp_x, new_head_x, @self_next
    body_y loop_i, temp_y
    if_eq temp_y, new_head_y, self_hit
label @self_next:
    if_eq loop_i, head_idx, @self_done
    inc loop_i
    if_eq loop_i, MAX_IDX, @self_wrap
    jmp @self_loop
label @self_wrap:
    store loop_i, 0
    jmp @self_loop

label @self_done:
    if_ne new_head_x, food_x, @no_eat
    if_ne new_head_y, food_y, @no_eat
    jmp @eat_food
label @no_eat:
    store grow_flag, 0
    jmp @update_body

label @eat_food:
    store grow_flag, 1
    inc score

label @find_food:
    inc food_x
    if_eq food_x, MAX_IDX, @ff_wrap_x
    jmp @ff_check
label @ff_wrap_x:
    store food_x, 0
    inc food_y
    if_eq food_y, MAX_IDX, @ff_wrap_y
    jmp @ff_check
label @ff_wrap_y:
    store food_y, 0
label @ff_check:
    copy loop_i, tail_idx
label @ff_occ_loop:
    body_x loop_i, temp_x
    if_ne temp_x, food_x, @ff_occ_next
    body_y loop_i, temp_y
    if_eq temp_y, food_y, @find_food
label @ff_occ_next:
    if_eq loop_i, head_idx, @ff_done
    inc loop_i
    if_eq loop_i, MAX_IDX, @ff_occ_wrap
    jmp @ff_occ_loop
label @ff_occ_wrap:
    store loop_i, 0
    jmp @ff_occ_loop
label @ff_done:

label @update_body:
    copy prev_tail_x, head_x
    copy prev_tail_y, head_y
    copy head_x, new_head_x
    copy head_y, new_head_y

    inc head_idx
    if_eq head_idx, MAX_IDX, @ub_head_wrap
    jmp @ub_head_cont
label @ub_head_wrap:
    store head_idx, 0
label @ub_head_cont:
    set_body_x head_idx, new_head_x
    set_body_y head_idx, new_head_y

    if_eq grow_flag, 1, @ub_grow
    inc tail_idx
    if_eq tail_idx, MAX_IDX, @ub_tail_wrap
    jmp @ub_tail_cont
label @ub_tail_wrap:
    store tail_idx, 0
label @ub_tail_cont:
    store grow_flag, 0
    jmp @move_done

label @ub_grow:
    inc snake_len
    store grow_flag, 0

label @move_done:
    store tick_count, 0

label @skip_move:
    if_eq game_state, 1, @skip_render
    draw new_head_x, new_head_y, COL_HEAD
    draw prev_tail_x, prev_tail_y, COL_BODY
    if_eq grow_flag, 1, @skip_tail
    body_x tail_idx, temp_x
    body_y tail_idx, temp_y
    clear temp_x, temp_y
label @skip_tail:
    draw food_x, food_y, COL_FOOD
label @skip_render:
    write FRAME_DONE, 1
    jmp game_loop

label wall_collision:
    store game_state, 1
    jmp @done_collision

label self_hit:
    store game_state, 1

label @done_collision:
    store tick_count, 0
    jmp @skip_move

label game_over_label:
    write FRAME_DONE, 1
    jmp game_loop
"""


def main():
    print("Compiling TAL snake game...")
    asm_out = compile_tal(SNAKE_TAL)

    asm = Assembler()
    try:
        program, labels = asm.assemble(asm_out)
        print(f"OK: {len(program)} instructions, {len(labels)} labels")
    except Exception as e:
        print(f"ASSEMBLY ERROR:\n{e}")
        print("\n--- TAL OUTPUT (last 30 lines) ---")
        lines = asm_out.split('\n')
        for i, l in enumerate(lines[-30:]):
            print(f"  {i}: {l}")
        return

    # Run init
    mem = Memory(10000)
    cpu = CPU(memory=mem)
    cpu.load_program(program)
    cpu.pc = labels.get("init", 0)

    mem.store(9999, "0")
    steps = 0
    while steps < 2000:
        cpu.step()
        steps += 1
        if cpu.halted:
            print(f"HALTED at step {steps}")
            break
        if mem.load(9999) != "0":
            print(f"Frame done at step {steps}")
            break

    # Check initial state
    print(f"\nAfter init:")
    print(f"  head: ({t2d(mem.load(6))},{t2d(mem.load(7))})")
    print(f"  food: ({t2d(mem.load(3))},{t2d(mem.load(4))})")
    print(f"  dir={t2d(mem.load(1))}, state={t2d(mem.load(0))}")
    print(f"  head_idx={t2d(mem.load(8))}, tail_idx={t2d(mem.load(9))}")
    print(f"  snake_len={t2d(mem.load(10))}")

    # Check VRAM pixels
    def px(x, y):
        return t2d(mem.load(1000 + y * 64 + x))

    print(f"  Pixel(32,32)={px(32,32)} (expect 4=head)")
    print(f"  Pixel(31,32)={px(31,32)} (expect 2=body)")
    print(f"  Pixel(30,32)={px(30,32)} (expect 2=body)")
    print(f"  Pixel(20,20)={px(20,20)} (expect 3=food)")

    # Run enough frames to trigger at least one move
    for fr in range(12):
        mem.store(9999, "0")
        s2 = 0
        while s2 < 2000:
            cpu.step()
            s2 += 1
            if cpu.halted:
                break
            if mem.load(9999) != "0":
                break
        if fr == 0 or fr == 10:
            print(f"\nFrame {fr+2}: head=({t2d(mem.load(6))},{t2d(mem.load(7))}), "
                  f"tick={t2d(mem.load(11))}, dir={t2d(mem.load(1))}, "
                  f"nh=({t2d(mem.load(15))},{t2d(mem.load(16))}), state={t2d(mem.load(0))}")

    print(f"\nAfter 13 frames total:")
    print(f"  head: ({t2d(mem.load(6))},{t2d(mem.load(7))})")
    print(f"  tick: {t2d(mem.load(11))}")
    print(f"  Pixel(33,32)={px(33,32)} (expect 2=body segment, was old head)")
    print(f"  Pixel(30,32)={px(30,32)} (expect 0=cleared tail)")
    print(f"  Pixel(34,32)={px(34,32)} (expect 4=current head)")
    print(f"  Score: {t2d(mem.load(5))}")


if __name__ == "__main__":
    main()
