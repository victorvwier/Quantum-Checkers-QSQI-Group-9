import pygame
from .constants import White, Black, Rows, Cols, Board_White, Board_Brown, Square_Size
from .piece import piece


class Board:

    def __init__(self):
        self.board = []
        self.white_left = self.black_left = 12
        self.black_kings = self.black_kings = 0
        self.create_board()

    def draw_squares(self, win):
        win.fill(Board_Brown)
        for row in range(Rows):
            for col in range(row % 2, Rows, 2):
                pygame.draw.rect(win, Board_White, (row * Square_Size, \
                                                    col * Square_Size, Square_Size, Square_Size))

    def move(self, piece, row, col):
        self.board[piece.row][piece.col], self.board[row][col] = \
            self.board[row][col], self.board[piece.row][piece.col]
        piece.move(row, col)

        if row == Rows - 1 or row == 0:
            piece.make_king()
            if piece.color == White:
                self.white_kings += 1
            else:
                self.black_kings += 1

    def get_piece(self, row, col):
        return (self.board[row][col])

    def create_board(self):
        for row in range(Rows):
            self.board.append([])

            for col in range(Cols):
                if col % 2 == ((row + 1) % 2):
                    if row < 3:
                        self.board[row].append(piece(row, col, White))
                    elif row > 4:
                        self.board[row].append(piece(row, col, Black))
                    else:
                        self.board[row].append(0)
                else:
                    self.board[row].append(0)

    def draw(self, win):
        self.draw_squares(win)
        for row in range(Rows):
            for col in range(Cols):
                piece = self.board[row][col]
                if piece != 0:
                    piece.draw(win)

    def remove(self, pieces):
        for piece in pieces:
            self.board[piece.row][piece.col] = 0
            if piece != 0:
                if piece.color == Black:
                    self.black_left -= 1
                else:
                    self.white_left -= 1

    def winner(self):
        if self.black_left <= 0:
            return White
        elif self.white_left <= 0:
            return Black

        return None

    def get_valid_moves(self, piece):
        moves = {}
        left = piece.col - 1
        right = piece.col + 1
        row = piece.row

        if piece.color == Black or piece.king:
            moves.update(self._traverse_left(row - 1, max(row - 3, -1), -1, piece.color, left))
            moves.update(self._traverse_right(row - 1, max(row - 3, -1), -1, piece.color, right))

        if piece.color == White or piece.king:
            moves.update(self._traverse_left(row + 1, min(row + 3, Rows), 1, piece.color, left))
            moves.update(self._traverse_right(row + 1, min(row + 3, Rows), 1, piece.color, right))

        return moves

    def _traverse_left(self, start, stop, step, color, left, skipped=[]):
        moves = {}
        last = []
        for r in range(start, stop, step):
            if left < 0:
                break

            current = self.board[r][left]
            if current == 0:
                if skipped and not last:
                    break
                elif skipped:
                    moves[(r, left)] = last + skipped
                else:
                    moves[(r, left)] = last

                if last:
                    if step == -1:
                        row = max(r - 3, 0)
                    else:
                        row = min(r + 3, Rows)

                    moves.update(self._traverse_left(r + step, row, step, color, left - 1, skipped=last))
                    moves.update(self._traverse_right(r + step, row, step, color, left + 1, skipped=last))
                break

            elif current.color == color:
                break

            else:
                last = [current]

            left -= 1
        return moves

    def _traverse_right(self, start, stop, step, color, right, skipped=[]):
        moves = {}
        last = []
        for r in range(start, stop, step):
            if right >= Cols:
                break

            current = self.board[r][right]
            if current == 0:
                if skipped and not last:
                    break
                elif skipped:
                    moves[(r, right)] = last + skipped
                else:
                    moves[(r, right)] = last

                if last:
                    if step == -1:
                        row = max(r - 3, 0)
                    else:
                        row = min(r + 3, Rows)

                    moves.update(self._traverse_left(r + step, row, step, color, right - 1, skipped=last))
                    moves.update(self._traverse_right(r + step, row, step, color, right + 1, skipped=last))
                break

            elif current.color == color:
                break

            else:
                last = [current]

            right += 1

        return moves
