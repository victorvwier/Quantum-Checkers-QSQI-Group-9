import pygame
import pygame.gfxdraw
import pygame.freetype
import pygame.mixer

from Constants import Grey, Width, \
    Board_Brown, Board_White, Red, Green, White, Black, Blue_Piece, Red_Piece, Transparent_Grey, Transparent_White, \
    Slightly_Transparent_White, Bar, Dark_Grey
from QuantumCircuit import Quantumcircuit
import numpy as np
import math


class Board:
    def __init__(self, backend, rows, cols, piece_rows, square_size):
        self.rows = rows
        self.cols = cols
        self.piece_rows = piece_rows
        self.n_tiles = rows * cols // 2
        self.quantum_circuit = Quantumcircuit(rows, cols, piece_rows, backend)
        self.board = np.zeros((rows, cols))
        self.board_color = np.zeros((rows, cols))
        self.white_left = self.black_left = cols * piece_rows // 2
        self.quantum_mode = False
        self.entangle_mode = False
        self.square_size = square_size
        self.board_kings = np.zeros((rows, cols))
        self.ent_counter = np.zeros((rows, cols))

        pygame.init()
        pygame.freetype.init()

    def update_board(self):
        # self.Qcirc.Qboard = self.Qcirc.get_probability_comp(backend=backend)
        # for i in range (self.n_tiles):
        #     self.Qcirc.Qboard[i] = self.Qcirc.get_probability_exact(i)

        self.quantum_circuit.quantum_board = self.quantum_circuit.get_probability_exact2()

        j = 0
        for row in range(self.rows):
            for col in range(row % 2, self.rows, 2):
                self.board[row][col] = self.quantum_circuit.quantum_board[j]
                self.board_color[row][col] = self.quantum_circuit.color[j]
                self.ent_counter[row][col] = self.quantum_circuit.ent_counter[j]
                j += 1
                if self.board[row][col] < 0.02:
                    self.board_color[row][col] = 0
                    self.board_kings[row][col] = 0
        self.check_kings()
        print(self.quantum_circuit.ent_counter)

    def draw_squares(self, win):
        win.fill(Grey)
        for row in range(self.rows):
            for col in range(row % 2, self.rows, 2):
                pygame.draw.rect(win, Board_White,
                                 (row * self.square_size, col * self.square_size, self.square_size, self.square_size))

        bg = pygame.image.load("./img/bar.png")
        win.blit(bg, (0, Width, Width, Bar))

        self.render_text(win, (self.rows // 2) * self.square_size, self.cols * self.square_size + Bar // 2,
                         'quantum checkers', White,
                         font_size=Bar * 0.5, font_path='fonts/title.ttf')

    def draw_buttons(self, win):
        qmode_color = Green if self.quantum_mode else Transparent_White
        self.render_text(win, (self.rows - 0.5) * self.square_size, self.cols * self.square_size + Bar // 2,
                         'quantum moves {}'.format("on" if self.quantum_mode else "off"), qmode_color)

        entangle_color = Green if self.entangle_mode else Transparent_White
        self.render_text(win, 0.5 * self.square_size, self.cols * self.square_size + Bar // 2,
                         'entangling {}'.format("on" if self.entangle_mode else "off"), entangle_color)

    def move_sound(self):
        move_sound = pygame.mixer.Sound('sound/move.wav')
        move_sound.play()

    def render_text(self, surface, x, y, text, color, font_size=12, font_path=None):
        font = pygame.freetype.SysFont("Consolas", font_size)
        if font_path is not None:
            font = pygame.freetype.Font(font_path, int(font_size))
        textsurface = font.render(text, fgcolor=color)[0]
        dx = int(textsurface.get_size()[0] / 2)
        dy = int(textsurface.get_size()[1] / 2)
        surface.blit(textsurface, (int(x - dx), int(y - dy)))

    def draw_pieces(self, win):
        radius = int(0.3 * self.square_size)
        min_prob = 0.3
        for row in range(self.rows):
            for col in range(self.cols):
                king = self.board_kings[row][col] == 1 and self.board[row][col] > min_prob
                x = col * self.square_size + self.square_size // 2
                y = row * self.square_size + self.square_size // 2
                probability = self.board[row][col]

                if self.board_color[row][col] == 1:
                    self._draw_circles(win, Blue_Piece, probability, (x, y), radius, king)

                if self.board_color[row][col] == -1:
                    self._draw_circles(win, Red_Piece, probability, (x, y), radius, king)

    def _draw_circles(self, surface, color, probability, center, radius, king):
        target_rect = pygame.Rect(center, (0, 0)).inflate((radius * 2, radius * 2))
        shape_surf = pygame.Surface(target_rect.size, pygame.SRCALPHA)
        self.draw_pie(shape_surf, radius, radius, radius, color, probability, king=king)
        surface.blit(shape_surf, target_rect)

    def draw_possible_moves(self, win, moves):

        for move in moves:
            row, col = move
            pygame.draw.circle(win, Transparent_Grey, (col * self.square_size + self.square_size // 2 \
                                                           , row * self.square_size + self.square_size // 2), 15)

    def draw_pie(self, surface, cx, cy, r, color, probability, king=False):
        angle = int(probability * 360)
        p = [(cx, cy)]
        for n in range(0, angle):
            x = cx + int(r * math.cos(n * math.pi / 180))
            y = cy + int(r * math.sin(n * math.pi / 180))
            p.append((x, y))
        p.append((cx, cy))

        # Draw pie segment
        if len(p) > 2:
            pygame.gfxdraw.aapolygon(surface, p, color)
            pygame.gfxdraw.filled_polygon(surface, p, color)

        pygame.gfxdraw.aacircle(surface, cx, cy, int(0.9 * r), Dark_Grey)
        pygame.gfxdraw.filled_circle(surface, cx, cy, int(0.9 * r), Dark_Grey)

        if king:
            crown = pygame.transform.scale(pygame.image.load("./img/crown.png"), (30, 30))
            surface.blit(crown, (cx - 15, cy - r // 2 - 20))
            # pygame.draw.circle(surface, Green, (cx, cy), int(r), width=2)

        self.render_text(surface, cx, cy, "{:.2f}".format(probability), Transparent_White)

    def draw_double_ent(self, win):
        for row in range(self.rows):
            for col in range(self.cols):
                if self.ent_counter[row][col] == 2:
                    pygame.draw.circle(win, Red, (col * self.square_size + self.square_size // 2,
                                                  row * self.square_size + self.square_size // 2 + self.square_size / 6), 8)

    def check_kings(self):
        for tile_col in range(0, self.cols, 2):
            if self.board_color[0][tile_col] == -1:
                self.board_kings[0][tile_col] = 1
        for tile_col in range(1, self.cols, 2):
            if self.board_color[self.rows - 1][tile_col] == 1:
                self.board_kings[self.rows - 1][tile_col] = 1

    def check_valid_moves(self, selected_piece):
        moves = {}
        left = selected_piece[1] - 1
        right = selected_piece[1] + 1
        row = selected_piece[0]
        color = self.board_color[selected_piece[0]][selected_piece[1]]
        sel = selected_piece
        # self.board_for_val_moves(selected_piece,color)

        if color == -1 or self.board_kings[selected_piece]:
            moves.update(self._traverse_left(row - 1, max(row - 3, -1), -1, color, left, sel))
            moves.update(self._traverse_right(row - 1, max(row - 3, -1), -1, color, right, sel))

        if color == 1 or self.board_kings[selected_piece]:
            moves.update(self._traverse_left(row + 1, min(row + 3, self.rows), 1, color, left, sel))
            moves.update(self._traverse_right(row + 1, min(row + 3, self.rows), 1, color, right, sel))

        return moves

    def _traverse_left(self, start, stop, step, color, left, sel, skipped=[]):
        moves = {}
        last = []
        where_in = -1
        for r in range(start, stop, step):
            where_in += 1
            if left < 0:
                break
            currentc = self.board_color[r][left]
            currentp = self.board[r][left]

            if where_in == 0:
                if currentc == 0 and len(last) == 0 and len(skipped) == 0:
                    moves[(r, left)] = last
                    break
                elif currentc == color and len(last) == 0 and currentp < 0.98 \
                        and len(skipped) == 0 and self.board_kings[r][left] == self.board_kings[sel] \
                        and self.ent_counter[sel] < 2:

                    moves[(r, left)] = last
                    break
                elif currentc == -color and len(last) == 0:
                    last = (r, left)
            else:
                if len(last) != 0 and self.quantum_mode == False:
                    if currentp > 0.98:
                        break
                    else:
                        moves[(r, left)] = skipped + [last[0], last[1]]
                        if color == 1:
                            row = min(r + 3, self.rows)
                        else:
                            row = max(r - 3, -1)
                        moves.update(self._traverse_left(r + step, row, step, color, left - 1, sel, skipped=list(last)))
                        moves.update(self._traverse_right(r + step, row, step, color, left + 1, sel, skipped=list(last)))

            left -= 1

        return moves

    def _traverse_right(self, start, stop, step, color, right, sel, skipped=[]):
        moves = {}
        last = []
        where_in = -1
        for r in range(start, stop, step):
            if right >= self.cols:
                break
            where_in += 1
            currentc = self.board_color[r][right]
            currentp = self.board[r][right]

            if where_in == 0:
                if currentc == 0 and len(last) == 0 and len(skipped) == 0:
                    moves[(r, right)] = last
                    break
                elif currentc == color and len(last) == 0 and currentp < 0.98 \
                        and len(skipped) == 0 and self.board_kings[r][right] == self.board_kings[sel] \
                        and self.ent_counter[sel] < 2:

                    moves[(r, right)] = last
                    break
                elif currentc == -color and len(last) == 0:
                    last = (r, right)
            else:
                if len(last) != 0 and self.quantum_mode == False:
                    if currentp > 0.98:
                        break
                    else:
                        moves[(r, right)] = skipped + [last[0], last[1]]
                        if color == 1:
                            row = min(r + 3, self.rows)
                        else:
                            row = max(r - 3, -1)
                            moves.update(
                                self._traverse_left(r + step, row, step, color, right - 1, sel, skipped=list(last)))
                            moves.update(
                                self._traverse_right(r + step, row, step, color, right + 1, sel, skipped=list(last)))

            right += 1

        return moves
