import pygame

from Q_inspire_connection import fix_connection
from Constants import Width, Bar, Height, full_collapse_config
from Board import Board




class Game:

    def __init__(self, screen, game_config):
        self.screen = screen
        self.backend = fix_connection()
        self.selected = 0
        self.turn = 1
        self.q_counter = 0
        self.pos_moves = {}
        self.full_collapse = game_config["full_collapse"]
        self.sq_size = game_config["square_size"]
        self.piece_rows = game_config["piece_rows"]
        self.rows = game_config["rows"]
        self.cols = game_config["cols"]
        self.board = Board(self.backend, self.rows, self.cols, self.piece_rows, self.sq_size)
        self.board.update_board()

    def get_row_col_from_mouse(self, pos):
        x, y = pos
        row = y // self.sq_size
        col = x // self.sq_size
        return row, col

    def update(self):
        self.board.draw_squares(self.screen)
        self.board.draw_pieces(self.screen)
        self.board.draw_buttons(self.screen)
        self.board.draw_double_ent(self.screen)
        if self.selected != 0:
            self.board.draw_possible_moves(self.screen, self.pos_moves)
        pygame.display.update()

    def convert_to_Q(self, c_pos):
        return int(self.cols / 2 * c_pos[0] + c_pos[1] // 2)

    def check_for_valid_selection(self, row, col):
        if self.board.board_color[row][col] == self.turn:
            self.selected_piece = (row, col)
            self.selected = 1
            self.pos_moves = self.board.check_valid_moves(self.selected_piece)
        else:
            self.selected_piece = None

    def change_selected_piece(self, row, col):
        self.selected_piece = (row, col)
        self.pos_moves = self.board.check_valid_moves(self.selected_piece)
        self.q_counter = 0

    def perform_c_move(self, row, col):
        clicked = (row, col)
        failed_attack = False
        failed_move = False

        if len(self.pos_moves[clicked]) == 0:
            if self.board.board_color[row][col] == 0:
                self.perform_c_empty(row, col)
            elif self.board.board_color[row][col] == self.turn and self.board.board[row][col] < 0.9:
                self.perform_c_own_color(row, col, failed_move)
            self.board.update_board()
        else:
            while not failed_attack and len(self.pos_moves[clicked]) != 0:
                defend = self.pos_moves[clicked][0:2]
                defender = (defend[0], defend[1])

                del self.pos_moves[clicked][0:2]

                attacker = self.selected_piece
                if len(self.pos_moves[clicked]) != 0:
                    if defend[0] - self.selected_piece[0] < 0 and defend[1] - self.selected_piece[1] < 0:
                        behind = (defend[0] - 1, defend[1] - 1)
                    elif defend[0] - self.selected_piece[0] > 0 and defend[1] - self.selected_piece[1] < 0:
                        behind = (defend[0] + 1, defend[1] - 1)
                    elif defend[0] - self.selected_piece[0] < 0 and defend[1] - self.selected_piece[1] > 0:
                        behind = (defend[0] - 1, defend[1] + 1)
                    else:
                        behind = (defend[0] + 1, defend[1] + 1)
                else:
                    behind = clicked

                if self.full_collapse:
                    # Full collapse
                    suc_a, suc_b, suc_c = self.board.quantum_circuit.full_collapse(self.convert_to_Q(attacker), \
                                                                              self.convert_to_Q(defender),
                                                                              self.convert_to_Q(behind))
                    self.board.update_board()
                else:
                    # Partial collapse code
                    self.board.quantum_circuit.part_collapse(self.convert_to_Q(attacker), \
                                              self.convert_to_Q(defender), self.convert_to_Q(behind))
                    self.board.update_board()
                    suc_a, suc_b, suc_c = round(self.board.board[attacker]), round(self.board.board[defender]), round(
                        self.board.board[behind])

                if suc_a == 0:
                    failed_attack = True
                    if suc_b == 0:
                        self.board.board_color[defender[0]][defender[1]] = 0
                elif suc_b == 0:
                    self.perform_c_empty(defender[0], defender[1])
                elif suc_b == 1 and suc_c == 0:
                    self.perform_c_empty(behind[0], behind[1], other=attacker)
                    self.board.quantum_circuit.remove_collapsed_piece(self.convert_to_Q(defender))
                    self.board.board_color[defender[0]][defender[1]] = 0

                self.board.update_board()

        if not failed_move:
            self.selected = 0
            self.turn = -self.turn
            self.update()
            self.board.move_sound()

    def perform_c_empty(self, row, col, other=False):
        new_position = (row, col)
        self.board.board_kings[new_position]= self.board.board_kings[self.selected_piece]
        self.board.board_kings[self.selected_piece] = 0
        if not other:
            self.board.quantum_circuit.c_empty(self.convert_to_Q(self.selected_piece), self.convert_to_Q(new_position))
        else:
            self.board.quantum_circuit.c_empty(self.convert_to_Q(other), self.convert_to_Q(new_position))
            
    def perform_q_empty(self,row,col):
        new_position = (row, col)
        self.board.board_kings[new_position]= self.board.board_kings[self.selected_piece]
        self.board.quantum_circuit.q_empty((self.convert_to_Q(self.selected_piece), self.convert_to_Q(new_position)))
            
        
    def perform_c_own_color(self, row, col, failed_move):
        new_position = (row, col)
        if self.board.board[self.selected_piece] > 0.98:
            self.board.quantum_circuit.c_self_unentangled(self.convert_to_Q(self.selected_piece),
                                                     self.convert_to_Q(new_position))
        else:
            failed_move = self.board.quantum_circuit.c_self_entangled \
                (self.convert_to_Q(self.selected_piece), self.convert_to_Q(new_position), failed_move)

        self.board.board_kings[new_position] = self.board.board_kings[self.selected_piece]
        return failed_move
    
    def perform_q_own_color(self,row,col):
        new_position = (row, col)
        if self.board.board[self.selected_piece] > 0.98:
            self.board.quantum_circuit.q_empty(self.convert_to_Q(self.selected_piece),
                                                     self.convert_to_Q(new_position))
        else:
            self.board.quantum_circuit.q_entangled \
                (self.convert_to_Q(self.selected_piece), self.convert_to_Q(new_position))
        

    def perform_q_move(self, row, col):
        if self.board.board_color[row][col] == 0:
                self.perform_q_empty(row, col)
        elif self.board.board_color[row][col] == self.turn and self.board.board[row][col] < 0.9:
                self.perform_q_own_color(row, col)
        
        self.board.update_board()
        self.selected = 0
        self.turn = -self.turn
        self.update()
        self.board.move_sound()
        
        
        # self.new_pos = (row, col)
        # self.board.quantum_circuit.q_empty(self.convert_to_Q(self.selected_piece), \
        #                               self.convert_to_Q(self.new_pos))
        # self.board.board_kings[self.new_pos] = self.board.board_kings[self.selected_piece]
        # self.selected = 0
        # self.q_counter = 0
        # self.turn = -self.turn

        # self.board.update_board()
        # self.board.move_sound()

    def move_allowed(self, row, col):
        return (row, col) in self.pos_moves

    def play(self):
        FPS = 60
        run = True
        clock = pygame.time.Clock()

        while run:
            clock.tick(FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                    self.board.quantum_circuit.append_to_full_circuit(last=True)
                    self.board.quantum_circuit.draw_circuit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()
                    row, col = self.get_row_col_from_mouse(pos)
                    if row >= self.rows:
                        if col == self.cols - 1:
                            self.board.quantum_mode = not self.board.quantum_mode
                            self.q_counter = 0
                        elif col == 0:
                            self.board.entangle_mode = not self.board.entangle_mode
                            self.q_counter = 0

                    elif self.selected == 0:
                        self.check_for_valid_selection(row, col)

                    elif self.selected == 1 and self.board.board_color[row][col] == self.turn \
                            and not self.board.entangle_mode:
                        self.change_selected_piece(row, col)

                    elif self.selected == 1 and not self.board.quantum_mode and self.move_allowed(row, col):
                        self.perform_c_move(row, col)

                    elif self.selected == 1 and self.board.quantum_mode and self.move_allowed(row, col):
                        self.perform_q_move(row, col)
            self.update()

        pygame.quit()


if __name__ == "__main__":
    screen = pygame.display.set_mode((Width, Height), pygame.DOUBLEBUF, 32)
    game = Game(screen, full_collapse_config)
    pygame.display.set_caption('Quantum checkers')
    icon = pygame.image.load('./img/icon.png')
    pygame.display.set_icon(icon)
    game.play()










