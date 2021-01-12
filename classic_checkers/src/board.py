from .piece import Piece
from .position import Position

size = 5


class Board:
    def __init__(self):
        """
        Constructs the board object.
        """
        self.pieces = list()
        for i in range(size):
            if i % 2 == 0:
                self.pieces.append(Piece(Position(i, 0)))
            else:
                self.pieces.append(Piece(Position(i, 1)))

    def get_board(self):
        """
        Constructs the board array from the list of pieces.
        :return: a 2D array of probabilities.
        """
        board = [[0 for _ in range(size)] for _ in range(size)]
        for piece in self.pieces:
            for position in piece.positions.keys():
                prob = piece.positions.get(position)
                board[position.x][position.y] = prob
        return board

    def print_board(self):
        """
        Prints the board.
        """
        form = "{:.2f}"
        board = self.get_board()

        # format the board to a desired shape
        for x in range(size):
            for y in range(size):
                board[x][y] = form.format(board[x][y])

        for row in board:
            print('|'.join(map(str, row)))
        print("")

    def classical_move(self, current_position, new_position):
        """
        Move a piece from one position to another.
        :param current_position: starting position.
        :param new_position: desired position after move.
        """
        # get the board
        board = self.get_board()
        # check if the move is valid
        assert current_position.x < size and current_position.y < size and new_position.x < size \
               and new_position.y < size, "one of the positions is out of bounds "
        assert board[current_position.x][current_position.y] != 0, "there is no piece in the current position"
        assert board[new_position.x][new_position.y] == 0, "that position is already occupied"

        for piece in self.pieces:
            if current_position in piece.positions:
                piece.classical_move(current_position, new_position)

    def quantum_move(self, current_position, new_positions):
        """
        Move a piece from one position to a superposition of new positions.
        :param current_position: starting position.
        :param new_positions: list of desired positions after move.
        """
        board = self.get_board()
        assert current_position.x < size and current_position.y < size, \
            "Position {} is out of bounds.".format(current_position)
        assert board[current_position.x][current_position.y] != 0, "there is no piece in the current position"
        for new_position in new_positions:
            assert new_position.x < size and new_position.y < size, "Position {} is out of bounds.".format(new_position)
            assert board[new_position.x][new_position.y] == 0, "Position {} is already occupied".format(new_position)

        for piece in self.pieces:
            if current_position in piece.positions:
                piece.quantum_move(current_position, new_positions)

    def collapse(self, collapse_position):
        """
        Performs a collapse of a piece at a given position.
        :param collapse_position: One of the positions occupied by the piece that should be collapsed.
        """
        for piece in self.pieces:
            if collapse_position in piece.positions:
                piece.collapse()
