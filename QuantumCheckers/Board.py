import pygame
import pygame.gfxdraw
import pygame.freetype
import pygame.mixer

from Constants import Rows, Cols, Piece_Rows, Square_Size, Grey, \
    Board_Brown, Board_White, Red, Green, White, Black, Blue_Piece, Red_Piece, Transparent_Grey, Transparent_White, \
    Slightly_Transparent_White,Gold,crown
from QuantumCircuit import Quantumcircuit
import numpy as np
import math


class Board:
    def __init__(self, backend):
        self.n_tiles = Rows * Cols // 2
        self.quantum_circuit = Quantumcircuit(Rows, Cols, Piece_Rows, backend)
        self.board = np.zeros((Rows, Cols))
        self.board_color = np.zeros((Rows, Cols))
        self.white_left = self.black_left = Cols * Piece_Rows // 2
        self.quantum_mode = False
        self.entangle_mode = False
        self.board_kings =  np.zeros((Rows, Cols))

        pygame.init()
        pygame.freetype.init()

    def update_board(self):
        # self.Qcirc.Qboard = self.Qcirc.get_probability_comp(backend=backend)
        # for i in range (self.n_tiles):
        #     self.Qcirc.Qboard[i] = self.Qcirc.get_probability_exact(i)

        self.quantum_circuit.quantum_board = self.quantum_circuit.get_probability_exact2()

        j = 0
        for row in range(Rows):
            for col in range(row % 2, Rows, 2):
                self.board[row][col] = self.quantum_circuit.quantum_board[j]
                self.board_color[row][col] = self.quantum_circuit.color[j]
                j += 1
                if self.board[row][col] < 0.02:
                    self.board_color[row][col] = 0
                    self.board_kings[row][col] = 0
        self.check_kings()

    def draw_squares(self, win):
        win.fill(Board_Brown)
        for row in range(Rows):
            for col in range(row % 2, Rows, 2):
                pygame.draw.rect(win, Board_White, (row * Square_Size, col * Square_Size, Square_Size, Square_Size))
        pygame.draw.rect(win, Grey, (0, Cols * Square_Size, Cols * Square_Size, Square_Size))

        pygame.draw.rect(win, Grey, (0, Cols * Square_Size, Square_Size, Square_Size // 2))
        pygame.draw.rect(win, Grey, ((Rows - 1) * Square_Size, Cols * Square_Size, Square_Size, Square_Size // 2))

        self.render_text(win, (Rows // 2) * Square_Size, (Cols + 0.25) * Square_Size, 'quantum checkers', White, font_size=Square_Size*0.2)

    def draw_buttons(self, win):
        qmode_color = Green if self.quantum_mode else Transparent_White
        self.render_text(win, (Rows - 0.5) * Square_Size, (Cols + 0.25) * Square_Size, 'quantum moves {}'.format("on" if self.quantum_mode else "off"), qmode_color)

        entangle_color = Green if self.entangle_mode else Transparent_White
        self.render_text(win, 0.5 * Square_Size, (Cols + 0.25) * Square_Size, 'entangling {}'.format("on" if self.entangle_mode else "off"), entangle_color)

    def move_sound(self):
        move_sound = pygame.mixer.Sound('sound/move.wav')
        move_sound.play()

    def render_text(self, surface, x, y, text, color, font_size=Square_Size * 0.1):
        font = pygame.freetype.SysFont('Consolas', font_size)
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
        
    def draw_kings(self,win):
        min_prob = 0.3
        for row in range(Rows):
            for col in range(Cols):
                if self.board_kings[row][col] == 1 and self.board[row][col] > min_prob:
                    win.blit(crown,(col*Square_Size+Square_Size//2-62,row*Square_Size+Square_Size//2-125)) 
                    
                    
        
    def check_kings(self):
        for tile_col in range(0,2,Cols):
            if self.board_color[0][tile_col] == -1:
                self.board_kings[0][tile_col] = 1
        for tile_col in range(1,2,Cols):
            if self.board_color[Rows-1][tile_col] == 1:
                self.board_kings[Rows-1][tile_col] = 1

    def check_valid_moves(self, selected_piece):
        moves = {}
        left = selected_piece[1] - 1
        right = selected_piece[1] + 1
        row = selected_piece[0]
        color = self.board_color[selected_piece[0]][selected_piece[1]]
        # self.board_for_val_moves(selected_piece,color)

        if color == -1 or self.board_kings[selected_piece]:
            moves.update(self._traverse_left(row - 1, max(row - 3, -1), -1, color, left))
            moves.update(self._traverse_right(row - 1, max(row - 3, -1), -1, color, right))

        if color == 1 or self.board_kings[selected_piece]:
            moves.update(self._traverse_left(row + 1, min(row + 3, Rows), 1, color, left))
            moves.update(self._traverse_right(row + 1, min(row + 3, Rows), 1, color, right))

        return moves
    

    def _traverse_left(self, start, stop, step, color, left, skipped=[]):
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
                        and len(skipped) == 0:

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
                            row = min(r + 3, Rows)
                        else:
                            row = max(r - 3, -1)
                        moves.update(self._traverse_left(r + step, row, step, color, left - 1, skipped=list(last)))
                        moves.update(self._traverse_right(r + step, row, step, color, left + 1, skipped=list(last)))

            left -= 1

        return moves

    def _traverse_right(self, start, stop, step, color, right, skipped=[]):
        moves = {}
        last = []
        where_in = -1
        for r in range(start, stop, step):
            if right >= Cols:
                break
            where_in += 1
            currentc = self.board_color[r][right]
            currentp = self.board[r][right]

            if where_in == 0:
                if currentc == 0 and len(last) == 0 and len(skipped) == 0:
                    moves[(r, right)] = last
                    break
                elif currentc == color and len(last) == 0 and currentp < 0.98 \
                        and len(skipped) == 0:

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
                            row = min(r + 3, Rows)
                        else:
                            row = max(r - 3, -1)
                            moves.update(self._traverse_left(r + step, row, step, color, right - 1, skipped=list(last)))
                            moves.update(
                                self._traverse_right(r + step, row, step, color, right + 1, skipped=list(last)))

            right += 1

        return moves

        # if self.board[r][right]<0.95:
        #     if skipped and not last:
        #         break
        #     elif skipped:
        #         moves[(r, right)] = last + skipped
        #     elif current == 0:
        #         moves[(r, right)] = last

        #     if last:
        #         if step == -1:
        #             row = max(r - 3, 0)
        #         else:
        #             row = min(r + 3, Rows)

        #         moves.update(self._traverse_left(r + step, row, step, color, right - 1, skipped=last))
        #         moves.update(self._traverse_right(r + step, row, step, color, right + 1, skipped=last))
        #     break

        # elif current == color:
        #     if self.board[r][right] < 0.95:
        #         moves[(r, right)] = last
        #         break
        #     else:
        #         break

        # else:
        #     #last = [current]
        #     last = [r,right]
