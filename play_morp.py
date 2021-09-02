from Morp import Morp, Board_3x3
import re


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
