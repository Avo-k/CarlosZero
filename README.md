# CarlosZero

A first experiment with Monte Carlo Tree Search (MCTS).

Both bots are using simple implementations of MCTS to simulate games 
and choose which move is best in given positions.

- **Morp** plays classical Tic-Tac-Toe (3\*3 grid)
- **Carlos** plays ultimate Tic-Tac-Toe (3\*3\*3 grid)

## Carlos

### Ultimate TicTacToe rules

Ultimate tic-tac-toe is a board game composed of nine tic-tac-toe boards
arranged in a 3 × 3 grid. Players take turns playing in the smaller
tic-tac-toe boards until one of them wins in the larger tic-tac-toe board.

Put simply you need to win 3 tic-tac-toe boards in a row to win the game. 
But you can only play in the grid relative to where your opponent played 
her last move:


```
    0 1 2   3 4 5   6 7 8
0 | . . . | . . . | . . . |
1 | . . . | . . . | . . . |
2 | . . . | . . . | . . . |
   -----------------------
3 | . . . | . . X | . . . |
4 | . . . | . . . | . . . |
5 | . . . | . . . | . . . |
   -----------------------
6 | . . . | . . . | . . . |
7 | . . . | . . . | . . . |
8 | . . . | . . . | . . . |
    0 1 2   3 4 5   6 7 8
    
legal moves: '0 3', '0 4', '0 5', '1 3', '1 4', '1 5', '2 3', '2 4', '2 5'
```
For example, if X played in the top right square of their local board, 
then O needs to play next in the local board at the top right of the 
global board. O can then play in any one of the nine available spots 
in that local board, each move sending X to a different local board.

If a move is played so that it is to win a local board by the rules of 
normal tic-tac-toe, then the entire local board is marked as a victory 
for the player in the global board.
Once a local board is won by a player or it is filled completely, no 
more moves may be played in that board. If a player is sent to such a 
board, then that player may play in any other board.

source [wikipedia](https://en.wikipedia.org/wiki/Ultimate_tic-tac-toe)