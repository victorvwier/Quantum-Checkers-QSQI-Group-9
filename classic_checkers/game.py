from classic_checkers.src.board import Board
from classic_checkers.src.position import Position

print("Initial board")
b = Board()
b.print_board()

print("Performing a classical move from (0,0) to (0,1)...")
b.classical_move(Position(0, 0), Position(0, 1))
b.print_board()

print("Performing a quantum move from (1,1) to [(0,2), (2,2)]...")
b.quantum_move(Position(1, 1), [Position(0, 2), Position(2, 2)])
b.print_board()

print("Performing a quantum move from (2,2) to [(1,3), (3,3)]...")
b.quantum_move(Position(2, 2), [Position(1, 3), Position(3, 3)])
b.print_board()

print("Performing a classical move from (3,3) to (4,4)...")
b.classical_move(Position(3, 3), Position(4, 4))
b.print_board()

print("Performing a collapse on position (0,2)...")
b.collapse(Position(0, 2))
b.print_board()

print("hello")