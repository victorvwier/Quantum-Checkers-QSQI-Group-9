import pygame

from Q_inspire_connection import fix_connection

from Board import Board
from Constants import Rows, Cols, Width, Height, Square_Size, Full_Collapse


def get_row_col_from_mouse(pos):
    x, y = pos
    row = y // Square_Size
    col = x // Square_Size
    return row, col


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
        Board.draw_kings(win)
        if self.selected != 0:
            Board.draw_possible_moves(win, self.pos_moves)
        pygame.display.update()

    def convert_to_Q(self, c_pos):
        return int(Cols / 2 * c_pos[0] + c_pos[1] // 2)

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
        behind = None

        if len(game.pos_moves[clicked]) == 0:
            if Board.board_color[row][col] == 0:
                game.perform_c_empty(row, col)
            elif Board.board_color[row][col] == game.turn and Board.board[row][col] < 0.9:
                game.perform_c_own_color(row, col)
            Board.update_board()
        else:
            while not failed_attack and len(self.pos_moves[clicked]) != 0:
                defend = self.pos_moves[clicked][0:2]
                defender = (defend[0], defend[1])

                del self.pos_moves[clicked][0:2]

                attacker = game.selected_piece
                if len(self.pos_moves[clicked]) != 0:
                    if defend[0] - game.selected_piece[0] < 0 and defend[1] - game.selected_piece[1] < 0:
                        behind = (defend[0] - 1, defend[1] - 1)
                    elif defend[0] - game.selected_piece[0] > 0 and defend[1] - game.selected_piece[1] < 0:
                        behind = (defend[0] + 1, defend[1] - 1)
                    elif defend[0] - game.selected_piece[0] < 0 and defend[1] - game.selected_piece[1] > 0:
                        behind = (defend[0] - 1, defend[1] + 1)
                    else:
                        behind = (defend[0] + 1, defend[1] + 1)
                else:
                    behind = clicked
                    

                if Full_Collapse:
                    # Full collapse
                    suc_a, suc_b, suc_c = Board.quantum_circuit.full_collapse(game.convert_to_Q(attacker), \
                                                                              game.convert_to_Q(defender),
                                                                              game.convert_to_Q(behind))
                    Board.update_board()
                else:
                    # Partial collapse code
                    Board.Qcirc.part_collapse(game.convert_to_Q(attacker), \
                                              game.convert_to_Q(defender), game.convert_to_Q(behind))
                    Board.update_board()
                    suc_a, suc_b, suc_c = round(Board.board[attacker]), round(Board.board[defender]), round(
                        Board.board[behind])

                if suc_a == 0:
                    failed_attack = True
                    if suc_b == 0:
                        Board.board_color[defender[0]][defender[1]] = 0
                    Board.board_color[attacker[0]][attacker[1]]
                elif suc_b == 0:
                    game.perform_c_empty(defender[0], defender[1])
                    failed_attack = True
                elif suc_b == 1 and suc_c == 0:
                    game.perform_c_empty(behind[0], behind[1], other=attacker)
                    Board.quantum_circuit.remove_collapsed_piece(game.convert_to_Q(defender))
                    Board.board_color[defender[0]][defender[1]] = 0
                    game.selected_piece = behind

                Board.update_board()

        self.selected = 0
        self.turn = -self.turn
        game.update()
        Board.move_sound()

    def perform_c_empty(self, row, col, other=False):
        new_position = (row, col)
        Board.board_kings[new_position]= Board.board_kings[game.selected_piece]
        Board.board_kings[game.selected_piece] = 0
        if not other:
            Board.quantum_circuit.c_empty(game.convert_to_Q(game.selected_piece), game.convert_to_Q(new_position))
        else:
            Board.quantum_circuit.c_empty(game.convert_to_Q(other), game.convert_to_Q(new_position))

    def perform_c_own_color(self, row, col):
        new_position = (row, col)
        Board.quantum_circuit.c_own_color(game.convert_to_Q(game.selected_piece), game.convert_to_Q(new_position))
        Board.board_kings[new_position]= Board.board_kings[game.selected_piece]

    def perform_q_move(self, row, col):
        self.new_pos = (row, col)
        Board.quantum_circuit.q_empty(game.convert_to_Q(self.selected_piece), \
                                      game.convert_to_Q(self.new_pos))
        Board.board_kings[self.new_pos]= Board.board_kings[game.selected_piece]    
        self.selected = 0
        self.q_counter = 0
        self.turn = -self.turn


        Board.update_board()
        Board.move_sound()

    def move_allowed(self, row, col):
        return (row, col) in self.pos_moves


qi_backend = fix_connection()

win = pygame.display.set_mode((Width, Height), pygame.DOUBLEBUF, 32)

pygame.display.set_caption('Quantum checkers')
FPS = 60
Board = Board(qi_backend)
game = game(qi_backend)
icon = pygame.image.load('./img/icon.png')
pygame.display.set_icon(icon)


def main():
    run = True
    clock = pygame.time.Clock()

    while run:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                Board.quantum_circuit.draw_circuit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                row, col = get_row_col_from_mouse(pos)
                if row == Rows:
                    if col == Cols - 1:
                        Board.quantum_mode = not Board.quantum_mode
                        game.q_counter = 0
                    elif col == 0:
                        Board.entangle_mode = not Board.entangle_mode
                        game.q_counter = 0

                elif game.selected == 0:
                    game.check_for_valid_selection(row, col)

                elif game.selected == 1 and Board.board_color[row][col] == game.turn \
                        and not Board.entangle_mode:
                    game.change_selected_piece(row, col)

                elif game.selected == 1 and not Board.quantum_mode and game.move_allowed(row, col):
                    game.perform_c_move(row, col)

                elif game.selected == 1 and Board.quantum_mode and game.move_allowed(row, col):
                    game.perform_q_move(row, col)
        game.update()

    pygame.quit()


main()
