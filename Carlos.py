import math
import numpy as np
import random
import time


def get_sub_lines(sub_grid, move):
    x, y = move
    lines = {tuple(sub_grid[x]), tuple(sub_grid[:, y])}
    if x == y:
        lines.add((sub_grid[0, 0], sub_grid[1, 1], sub_grid[2, 2]))
    if x + y == 2:
        lines.add((sub_grid[0, 2], sub_grid[1, 1], sub_grid[2, 0]))
    return lines


def sub_is_won(sub_grid, move):
    for line in get_sub_lines(sub_grid, move):
        s = sum(line)
        if abs(s) == 3:
            return s // 3
    return 0


def sub_is_draw(sub_grid):
    return 0 not in sub_grid


class Board_9x9:
    def __init__(self, grid=np.zeros((3, 3, 3, 3)), blurred_grid=np.zeros((3, 3))):
        self.blurred_grid = blurred_grid
        self.grid = grid
        self.drawn = []

        self.player = 1
        self.next_grid = (-1, -1)
        self.last_move = (-1, -1)
        self.is_leaf = False
        self.term = None

    def blurred_draw(self):
        return all(sq in self.drawn for sq in zip(*np.where(self.blurred_grid == 0)))

    def make_move(self, move):
        new_board = Board_9x9()

        new_board.grid = self.grid.copy()
        new_board.blurred_grid = self.blurred_grid.copy()
        new_board.player = -1 * self.player
        new_board.drawn = self.drawn.copy()
        new_board.last_move = move

        x, sub_x = divmod(move[0], 3)
        y, sub_y = divmod(move[1], 3)

        # make the move
        new_board.grid[x, y, sub_x, sub_y] = self.player

        new_board.next_grid = (sub_x, sub_y)

        sub_grid = new_board.grid[x, y]
        sub_move = (sub_x, sub_y)

        # was a sub_grid winning move
        if sub_is_won(sub_grid, sub_move):
            new_board.blurred_grid[x, y] = self.player
            new_board.is_leaf = (term := sub_is_won(new_board.blurred_grid, (x, y))) or new_board.blurred_draw()
            if new_board.is_leaf:
                new_board.term = term

        # was a sub_grid drawing move
        elif sub_is_draw(sub_grid):
            new_board.drawn.append((x, y))
            # walrus ?
            new_board.is_leaf = new_board.blurred_draw()
            if new_board.is_leaf:
                new_board.term = 0

        return new_board

    def generate_states(self):

        # sub_grid is unfinished
        if self.next_grid != (-1, -1) and self.blurred_grid[self.next_grid] == 0 and self.next_grid not in self.drawn:
            sub_grid = self.grid[self.next_grid]
            x, y = self.next_grid
            # for each empty sq
            for sub_x, sub_y in zip(*np.where(sub_grid == 0)):
                yield self.make_move((x * 3 + sub_x, y * 3 + sub_y))

        else:
            for x, y in zip(*np.where(self.blurred_grid == 0)):
                if (x, y) not in self.drawn:
                    for sub_x, sub_y in zip(*np.where(self.grid[x, y] == 0)):
                        yield self.make_move((x * 3 + sub_x, y * 3 + sub_y))

    def legal_moves(self):
        """
        helper function to choose random moves efficiently
        :return: a list of legal moves [(x, y),]
        """
        legal_moves = []

        # sub_grid is unfinished
        if self.next_grid != (-1, -1) and self.blurred_grid[self.next_grid] == 0 and self.next_grid not in self.drawn:
            sub_grid = self.grid[self.next_grid]
            x, y = self.next_grid
            # for each empty sq
            for sub_x, sub_y in zip(*np.where(sub_grid == 0)):
                legal_moves.append((x * 3 + sub_x, y * 3 + sub_y))

        else:
            for x, y in zip(*np.where(self.blurred_grid == 0)):
                if (x, y) not in self.drawn:
                    for sub_x, sub_y in zip(*np.where(self.grid[x, y] == 0)):
                        legal_moves.append((x * 3 + sub_x, y * 3 + sub_y))

        return legal_moves

    def make_random_move(self):
        """
        play one random legal move
        :return: a board object
        """
        return self.make_move(random.choice(self.legal_moves()))

    def __str__(self):
        board = ""

        rows = iter(range(9))

        for i in range(3):
            if not i:
                board += "    0 1 2   3 4 5   6 7 8\n"
            else:
                board += "   " + "-" * 23 + "\n"
            for j in range(3):
                board += f"{next(rows)} | "
                for k in range(3):
                    for l in range(3):
                        sq = self.grid[i, k, j, l]
                        if sq == 0:
                            board += ". "
                        elif sq == 1:
                            board += "O "
                        else:
                            board += "X "
                    board += "| "
                board += "\n"
        board += "    0 1 2   3 4 5   6 7 8\n"

        return board

    def __hash__(self):
        return hash(self.grid.tobytes())


def ucb1(parent, child, temp):
    exploitation = child.score / child.visit_count * parent.board.player
    exploration = temp * math.sqrt(math.log(parent.visit_count / child.visit_count))
    return exploitation + exploration


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


class Carlos:
    def __init__(self, print_info=False):
        self.root = Node(Board_9x9(), None)
        self.print_info = print_info


    def run(self, board, time_limit=1, n_iter=10000):

        if (h := hash(board)) != hash(self.root.board):
            if self.root.is_fully_expanded:
                self.root = self.root.children[h]
            else:
                self.root = Node(board, None)

        s = time.time()
        i = 0

        for i in range(n_iter):
            node = self.select(self.root)
            score = self.simulate(node.board)
            self.backpropagate(node, score)
            if time.time() - s > time_limit:
                break

        if self.print_info:
            print(f"{i/(time.time() - s):.0f} iter/ second")
            moves_n_score = [(c.board.last_move, c.score) for c in self.root.children.values()]
            moves_n_score.sort(key=lambda x: x[1])
            print(moves_n_score[:5])

        self.root = self.get_best_move(self.root, 0)
        self.root.parent = None

        return self.root

    def select(self, node):
        while not node.board.is_leaf:
            if node.is_fully_expanded:
                node = self.get_best_move(node, 2)
            else:
                return self.expand(node)
        return node

    @staticmethod
    def fully_expand(node):
        states = node.board.generate_states()
        for state in states:
            node.children[hash(state)] = Node(state, node)
        node.is_fully_expanded = True

    @staticmethod
    def expand(node):
        states = node.board.generate_states()

        for state in states:
            if (h := hash(state)) not in node.children:
                node.children[h] = (new_node := Node(state, node))

                if next(states, -1) == -1:
                    node.is_fully_expanded = True

                return new_node

        assert 1 == 2

    @staticmethod
    def simulate(board):
        while not board.is_leaf:
            board = board.make_random_move()
        return board.term

    @staticmethod
    def backpropagate(node, score):
        while node is not None:
            node.visit_count += 1
            node.score += score
            node = node.parent

    @staticmethod
    def get_best_move(node, temp):
        best_score = float('-inf')
        best_moves = []

        for child_node in node.children.values():
            move_score = ucb1(node, child_node, temp=temp)

            if move_score > best_score:
                best_score = move_score
                best_moves = [child_node]

            elif move_score == best_score:
                best_moves.append(child_node)

        return random.choice(best_moves)
