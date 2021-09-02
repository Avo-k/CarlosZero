from Carlos import Carlos, Board_9x9
import random
import re


def main():

    carlos = Carlos(print_info=False)
    b = Board_9x9()
    turn = 0

    print(b)
    print("please enter a move in the form 'x y'")
    print("where x is the row and y is the column")
    print("and both are integers 0 to 8 inclusive\n")

    while not b.is_leaf:

        if turn:
            b = carlos.run(b, 1, 10000).board
            print(b)

        else:
            move = (-1, -1)
            legal_moves = b.legal_moves()
            # move = random.choice(legal_moves)
            while move not in legal_moves:
                examples = random.sample(legal_moves,k=9) if len(legal_moves) > 9 else legal_moves
                print(end="example of legal moves: ")
                print(*[repr(f"{x} {y}") for x, y in examples], sep=", ")
                move = input("Your move: ")
                if re.match(r"[0-8]\s[0-8]", move):
                    move = tuple(map(int, move.split()))
                else:
                    print(repr(move), "is an illegal move")
            b = b.make_move(move)

        turn ^= 1

    print(b)
    print("You win!" if b.term > 0 else "You lose" if b.term < 0 else "The game is a draw")
    input("press enter to play again")
    main()


if __name__ == "__main__":
    main()
