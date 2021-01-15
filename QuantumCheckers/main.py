import pygame

from Q_inspire_connection import fix_connection

from Board import Board
from Constants import Rows, Cols, Width, Height, Square_Size


def get_row_col_from_mouse(pos):
    x, y = pos
    row = y // Square_Size
    col = x // Square_Size
    return (row, col)


def Convert_to_Q(C_pos):
    return int(Cols / 2 * C_pos[0] + C_pos[1] // 2)


class game():

    def __init__(self, qi_backend):
        self.selected = 0
        self.turn = 1
        self.q_counter = 0
        self.pos_moves = {}
        self.backend = qi_backend
        Board.update_board()

    def update(self):
        Board.draw_squares(win)
        Board.draw_pieces(win)
        Board.draw_buttons(win)
        if self.selected != 0:
            Board.draw_possible_moves(win, self.pos_moves)
        pygame.display.update()

    def Convert_to_Q(self, C_pos):
        return (int(Cols / 2 * C_pos[0] + C_pos[1] // 2))

    def check_for_valid_selection(self, row, col):
        if Board.board_color[row][col] == self.turn:
            self.selected_piece = (row, col)
            self.selected = 1
            self.pos_moves = Board.check_valid_moves(self.selected_piece)
        else:
            self.selected_piece = None

    def change_selected_piece(self, row, col):
        self.selected_piece = (row, col)
        self.pos_moves = Board.check_valid_moves(self.selected_piece)
        self.q_counter = 0

    def perform_c_move(self, row, col):
        clicked = (row, col)
        failed_attack = False

        if len(game.pos_moves[clicked]) == 0:
            if Board.board_color[row][col] == 0:
                game.perform_c_empty(row, col)
            elif Board.board_color[row][col] == game.turn and Board.board[row][col] < 0.9:
                game.perform_c_own_color(row, col)
        else:
            while not (failed_attack) and len(self.pos_moves[clicked]) != 0:
                defender = self.pos_moves[clicked][0:2]
                print(defender)
                del self.pos_moves[clicked][0:2]
                suc_a, suc_b = Board.Qcirc.collapse(game.Convert_to_Q(game.selected_piece), game.Convert_to_Q(defender))

                if suc_a == 0:
                    failed_attack = True
                    if suc_b == 0:
                        Board.board_color[defender[0]][defender[1]] = 0
                    Board.board_color[game.selected_piece[0]][game.selected_piece[1]]
                    Board.update_board()
                elif suc_b == 0:
                    game.perform_c_empty(defender[0], defender[1])
                elif suc_b == 1:
                    game.perform_c_empty(clicked[0], clicked[1])
                game.update()
                Board.move_sound()

    def perform_c_empty(self, row, col):
        new_position = (row, col)
        Board.Qcirc.c_empty(Convert_to_Q(game.selected_piece), Convert_to_Q(new_position))
        self.selected = 0
        self.turn = - self.turn
        Board.update_board()

    def perform_c_own_color(self, row, col):
        new_position = (row, col)
        Board.Qcirc.c_own_color(Convert_to_Q(game.selected_piece), Convert_to_Q(new_position))
        self.selected = 0
        self.turn = - self.turn
        Board.update_board()

    def perform_q_move(self, row, col):
        if self.q_counter == 0:
            self.new_pos1 = (row, col)
            self.q_counter = 1
        elif self.q_counter == 1:
            self.new_pos2 = (row, col)
            # Board.Qcirc.sqrtswap(Convert_to_Q(self.selected_piece),\

            Board.Qcirc.q_empty(Convert_to_Q(self.selected_piece), \
                                Convert_to_Q(self.new_pos1), Convert_to_Q(self.new_pos2))
            self.selected = 0
            self.q_counter = 0
            self.turn = -self.turn

        Board.update_board()
        Board.move_sound()

    def move_allowed(self, row, col):
        return ((row, col) in self.pos_moves)


qi_backend = fix_connection()

win = pygame.display.set_mode((Width, Height), pygame.DOUBLEBUF, 32)

pygame.display.set_caption('Checkers')
FPS = 60
Board = Board(qi_backend)
game = game(qi_backend)


def main():
    run = True
    clock = pygame.time.Clock()

    while run:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                # Board.Qcirc.draw_circuit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                row, col = get_row_col_from_mouse(pos)
                if row == 0 and col == Cols - 1:
                    Board.qmode = not (Board.qmode)
                    game.q_counter = 0

                elif row == Rows - 1 and col == 0:
                    Board.chmode = not (Board.chmode)
                    game.q_counter = 0

                elif game.selected == 0:
                    game.check_for_valid_selection(row, col)

                elif game.selected == 1 and Board.board_color[row][col] == game.turn \
                        and Board.chmode:
                    game.change_selected_piece(row, col)

                elif game.selected == 1 and Board.qmode == False and game.move_allowed(row, col):
                    game.perform_c_move(row, col)

                elif game.selected == 1 and Board.board_color[row][col] == 0 and \
                        Board.qmode == True and game.move_allowed(row, col):
                    game.perform_q_move(row, col)
        game.update()

    pygame.quit()


main()
