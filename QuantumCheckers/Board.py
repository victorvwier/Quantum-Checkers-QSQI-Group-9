import pygame
import pygame.gfxdraw
import pygame.freetype
import pygame.mixer

from Constants import Rows, Cols, Piece_Rows, Square_Size, Grey, \
    Board_Brown, Board_White, Red, Green, White, Black, Blue_Piece, Red_Piece, Transparent_Grey, Transparent_White, Slightly_Transparent_White
from QuantumCircuit import Quantumcircuit
import numpy as np
import math


class Board:

    def __init__(self):
        self.n_tiles = Rows * Cols // 2
        self.Qcirc = Quantumcircuit(Rows, Cols, Piece_Rows)
        self.board = np.zeros((Rows, Cols))
        self.board_color = np.zeros((Rows, Cols))
        self.white_left = self.black_left = Cols * Piece_Rows // 2
        self.qmode = False
        self.chmode = True

        pygame.init()
        pygame.mixer.init()
        pygame.freetype.init()

    def update_board(self, backend):

        # self.Qcirc.Qboard = self.Qcirc.get_probability_comp(backend=backend)

        # for i in range (self.n_tiles):
        #     self.Qcirc.Qboard[i] = self.Qcirc.get_probability_exact(i)

        self.Qcirc.Qboard = self.Qcirc.get_probability_exact2()

        j = 0
        for row in range(Rows):
            for col in range(row % 2, Rows, 2):
                self.board[row][col] = self.Qcirc.Qboard[j]
                self.board_color[row][col] = self.Qcirc.color[j]
                j += 1

    def draw_squares(self, win):
        win.fill(Board_Brown)
        for row in range(Rows):
            for col in range(row % 2, Rows, 2):
                pygame.draw.rect(win, Board_White, (row * Square_Size, \
                                                    col * Square_Size, Square_Size, Square_Size))
        pygame.draw.rect(win, Grey, ((Rows - 1) * Square_Size, 0 \
                                         , Square_Size, Square_Size))
        pygame.draw.rect(win, Grey, (0, (Cols - 1) * Square_Size \
                                         , Square_Size, Square_Size))

    def draw_buttons(self, win):

        if not self.qmode:
            self.render_text(win, (Rows - 0.5) * Square_Size, 5 / 12 * Square_Size, 'Select', Transparent_White)
        else:
            self.render_text(win, (Rows - 0.5) * Square_Size, 5 / 12 * Square_Size, 'Deselect', Transparent_White)
        self.render_text(win, (Rows - 0.5) * Square_Size, 7 / 12 * Square_Size, 'Q_mode', Transparent_White)

        if not self.chmode:
            self.render_text(win, 0.5 * Square_Size, (Rows - 7 / 12) * Square_Size, 'Entangle', Transparent_White)
        else:
            self.render_text(win, 0.5 * Square_Size, (Rows - 7/12) * Square_Size, 'Change', Transparent_White)
        self.render_text(win, 0.5 * Square_Size, (Rows - 5/12) * Square_Size, 'Q_mode', Transparent_White)

    def move_sound(self):
        move_sound = pygame.mixer.Sound('sound/move.wav')
        move_sound.play()

    def render_text(self, surface, x, y, text, color):
        font = pygame.freetype.SysFont('Consolas', Square_Size * 0.1)
        textsurface = font.render(text, fgcolor=color)[0]
        dx = int(textsurface.get_size()[0] / 2)
        dy = int(textsurface.get_size()[1] / 2)
        surface.blit(textsurface, (int(x - dx), int(y - dy)))

    def draw_pieces(self, win):
        radius = int(0.3 * Square_Size)
        for row in range(Rows):
            for col in range(Cols):
                if self.board_color[row][col] == 1:
                    x = col * Square_Size + Square_Size // 2
                    y = row * Square_Size + Square_Size // 2
                    probability = self.board[row][col]
                    self._draw_circles(win, Blue_Piece, probability, (x, y), radius)

                if self.board_color[row][col] == -1:
                    x = col * Square_Size + Square_Size // 2
                    y = row * Square_Size + Square_Size // 2
                    probability = self.board[row][col]
                    self._draw_circles(win, Red_Piece, probability, (x, y), radius)

    def _draw_circles(self, surface, color, probability, center, radius):
        target_rect = pygame.Rect(center, (0, 0)).inflate((radius * 2, radius * 2))
        shape_surf = pygame.Surface(target_rect.size, pygame.SRCALPHA)
        self.draw_pie(shape_surf, radius, radius, radius, color, probability)
        surface.blit(shape_surf, target_rect)

    def draw_possible_moves(self, win, moves):

        for move in moves:
            row, col = move
            pygame.draw.circle(win, Transparent_Grey, (col * Square_Size + Square_Size // 2 \
                                                           , row * Square_Size + Square_Size // 2), 15)

    def draw_pie(self, surface, cx, cy, r, color, probability):
        angle = int(probability * 360)
        p = [(cx, cy)]
        for n in range(0, angle):
            x = cx + int(r * math.cos(n * math.pi / 180))
            y = cy + int(r * math.sin(n * math.pi / 180))
            p.append((x, y))
        p.append((cx, cy))

        # Draw pie segment
        if len(p) > 2:
            pygame.gfxdraw.aapolygon(surface, p, White)
            pygame.gfxdraw.filled_polygon(surface, p, White)

        pygame.gfxdraw.aacircle(surface, cx, cy, int(0.9 * r), color)
        pygame.gfxdraw.filled_circle(surface, cx, cy, int(0.9 * r), color)

        self.render_text(surface, cx, cy, "{:.2f}".format(probability), Transparent_White)

    def check_valid_moves(self, selected_piece):

        moves = {}
        left = selected_piece[1] - 1
        right = selected_piece[1] + 1
        row = selected_piece[0]
        color = self.board_color[selected_piece[0]][selected_piece[1]]

        if color == -1:
            moves.update(self._traverse_left(row - 1, max(row - 3, -1), -1, color, left))
            moves.update(self._traverse_right(row - 1, max(row - 3, -1), -1, color, right))

        if color == 1:
            moves.update(self._traverse_left(row + 1, min(row + 3, Rows), 1, color, left))
            moves.update(self._traverse_right(row + 1, min(row + 3, Rows), 1, color, right))

        return moves

    def _traverse_left(self, start, stop, step, color, left, skipped=[]):
        moves = {}
        last = []
        for r in range(start, stop, step):
            if left < 0:
                break

            current = self.board_color[r][left]
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

            elif current == color:
                if self.board[r][left] < 0.95:
                    moves[(r, left)] = last
                    break
                else:
                    break

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

            current = self.board_color[r][right]
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

            elif current == color:
                if self.board[r][right] < 0.95:
                    moves[(r, right)] = last
                    break
                else:
                    break

            else:
                last = [current]

            right += 1

        return moves
