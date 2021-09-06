import numpy as np
import random
import math
import re


LINES = np.array((0b000_000_111, 0b000_111_000, 0b111_000_000,
                  0b001_001_001, 0b010_010_010, 0b100_100_100,
                  0b100_010_001, 0b001_010_100), dtype=np.uint16)

LINES_FROM_SQ = {0: (LINES[0], LINES[3], LINES[6]),
                 1: (LINES[0], LINES[4]),
                 2: (LINES[0], LINES[5], LINES[7]),
                 3: (LINES[1], LINES[3]),
                 4: (LINES[1], LINES[4], LINES[6], LINES[7]),
                 5: (LINES[1], LINES[5]),
                 6: (LINES[2], LINES[3], LINES[7]),
                 7: (LINES[2], LINES[4]),
                 8: (LINES[2], LINES[5], LINES[6])}

EMPTY = 0
UNIVERSE = 0b111_111_111


# @njit(nb.b1(nb.uint64, nb.uint8), cache=True)
def get_bit(bb, sq):
    return bb & (1 << sq)


# @njit(nb.uint64(nb.uint64, nb.uint8), cache=True)
def set_bit(bb, sq):
    return bb | (1 << sq)


def print_bb(bb):
    bb_str = ""
    for sq in range(9):
        bb_str += "1 " if get_bit(bb, sq) else ". "
        if sq in (2, 5, 8):
            bb_str += "\n"
    print(bb_str)


class Bitboard_3x3:
    """
    Bitboard representation of 3*3 Tic-Tac-Toe.
    """
    def __init__(self, grid=np.zeros(3, dtype=np.uint16)):
        self.grid = grid    # both, X, O
        self.player = 1
        self.is_leaf = False
        self.term = None
        self.last_move = None

    def is_won(self):
        for line in LINES_FROM_SQ[self.last_move]:
            if self.grid[- self.player] & line == line:
                return - self.player
        return 0

    def is_draw(self):
        return self.grid[0] == UNIVERSE

    def make_move(self, move):
        new = Bitboard_3x3(self.grid.copy())

        mask = set_bit(EMPTY, (move := move[0] * 3 + move[1]))
        new.grid[self.player] |= mask
        new.grid[0] |= mask
        new.player = - self.player
        new.last_move = move

        new.is_leaf = ((term := new.is_won()) or new.is_draw())
        new.term = term if new.is_leaf else None
        return new

    def generate_states(self):
        yield from (self.make_move((sq // 3, sq % 3)) for sq in range(9) if not get_bit(self.grid[0], sq))

    def legal_moves(self):
        return [(sq // 3, sq % 3) for sq in range(9) if not get_bit(self.grid[0], sq)]

    def make_random_move(self):
        return self.make_move(random.choice(self.legal_moves()))

    def __str__(self):
        B = "\n"
        for row in range(3):
            for col in range(3):
                B += "|"
                sq = row * 3 + col
                B += " X " if get_bit(self.grid[1], sq) else \
                    " O " if get_bit(self.grid[2], sq) else " . "
            B += "|\n"
        return B
