import math
import random
import numpy as np
import re


class Board_3x3:
    def __init__(self, grid=np.zeros((3, 3))):
        self.grid = grid

        self.player = 1
        self.is_leaf = False
        self.term = None

        self.ply = 0

    def three(self):
        yield from set(map(tuple, (self.grid[0], self.grid[1], self.grid[2],
                    self.grid[:, 0], self.grid[:, 1], self.grid[:, 2],
                    self.grid.diagonal(), np.diag(np.fliplr(self.grid)))))

    def get_lines(self, move):
        x, y = move
        lines = [self.grid[x], self.grid[:, y]]
        if x == y:
            lines.append(self.grid.diagonal())
        if x + y == 2:
            lines.append((self.grid[0, 2], self.grid[1, 1], self.grid[2, 0]))
        return lines

    def was_winning_move(self, move):
        for line in self.get_lines(move):
            s = sum(line)
            if abs(s) == 3:
                return s//3
        return 0

    def is_won(self) -> int:
        for line in self.three():
            s = sum(line)
            if abs(s) == 3:
                return s//3
        return 0

    def is_draw(self):
        return self.ply == 9

    def make_move(self, move):
        new_board = Board_3x3()

        new_board.grid = self.grid.copy()
        new_board.grid[move] = self.player
        new_board.player = -1 * self.player
        new_board.ply = self.ply + 1
        new_board.is_leaf = (term := new_board.was_winning_move(move)) or new_board.is_draw()
        if new_board.is_leaf:
            new_board.term = term

        return new_board

    def generate_states(self):
        states = []
        if self.is_leaf: return states
        for x, line in enumerate(self.grid):
            for y, sq in enumerate(line):
                if sq == 0:
                    states.append(self.make_move((x, y)))
        return states

    def legal_moves(self):
        return [*zip(*np.where(self.grid == 0))]

    def __str__(self):
        board = ""
        for line in self.grid:
            board += "| "
            for sq in line:
                board += ("O" if sq == 1 else "X" if sq else ".") + " | "
            board += "\n"
        return board


class Node:
    def __init__(self, board, parent):
        self.board = board
        self.parent = parent

        self.value_sum = 0
        self.visit_count = 0
        self.score = 0
        self.children = {}

        self.is_fully_expanded = False

    def expanded(self):
        return not not self.children

    def value(self):
        if self.visit_count == 0:
            return 0
        return self.value_sum / self.visit_count


class Morp:
    def run(self, grid):
        self.root = Node(grid, None)

        for iteration in range(1000):
            node = self.select(self.root)
            score = self.rollout(node.board)
            self.backpropagate(node, score)

        return self.get_best_move(self.root, 0)

    def select(self, node):
        while not node.board.is_leaf:
            if node.is_fully_expanded:
                node = self.get_best_move(node, 2)
            else:
                return self.expand(node)
        return node

    def expand(self, node):
        states = node.board.generate_states()
        for state in states:
            if str(state) not in node.children:
                new_node = Node(state, node)
                node.children[str(state)] = new_node
                if len(states) == len(node.children):
                    node.is_fully_expanded = True

                return new_node

        assert 1 == 0, "illegal move"

    @staticmethod
    def rollout(board):
        while not board.is_leaf:
            board = random.choice(board.generate_states())
        return board.term

    def backpropagate(self, node, score):
        while node is not None:
            node.visit_count += 1
            node.score += score
            node = node.parent

    def get_best_move(self, node, exploration_constant):
        best_score = float('-inf')
        best_moves = []

        for child_node in node.children.values():

            move_score = node.board.player * child_node.score / child_node.visit_count + exploration_constant * math.sqrt(
                math.log(node.visit_count / child_node.visit_count))

            if move_score > best_score:
                best_score = move_score
                best_moves = [child_node]

            elif move_score == best_score:
                best_moves.append(child_node)

        return random.choice(best_moves)


def main():
    b = Board_3x3()
    m = Morp()
    turn = 1

    while not b.is_leaf:

        legal_moves = b.legal_moves()
        move = (-1, -1)

        if turn:
            print(b)
            while move not in legal_moves:
                print("legal moves: ", [f"{x} {y}" for x, y in legal_moves])
                move = input("your move:")
                if re.match(r"[0-8]\s[0-8]", move):
                    move = tuple(map(int, move.split()))
                else:
                    print(repr(move), "is an illegal move")
                    continue
            b = b.make_move(move)
        else:
            b = m.run(b).board

        turn ^= 1

    print(b)
    print("You win!" if b.term > 0 else "You lose" if b.term < 0 else "The game is a draw")
    input("press enter to play again")
    main()


if __name__ == '__main__':
    main()
