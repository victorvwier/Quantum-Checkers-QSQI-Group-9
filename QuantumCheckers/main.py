
import os
import pygame

from Q_inspire_connection import get_authentication
from quantuminspire.qiskit import QI

from Board import Board
from Constants import Rows,Cols,Piece_Rows,Width,Height,Square_Size,\
    Board_Brown,Board_White

QI_EMAIL = os.getenv('QI_EMAIL')
QI_PASSWORD = os.getenv('QI_PASSWORD')
QI_URL = os.getenv('API_URL', 'https://api.quantum-inspire.com/')            
            
authentication = get_authentication()
QI.set_authentication(authentication, QI_URL)
qi_backend = QI.get_backend('QX single-node simulator')

win = pygame.display.set_mode((Width,Height), pygame.DOUBLEBUF, 32)
pygame.display.set_caption('Checkers')
FPS = 60
Board = Board()

    # Board.Qcirc.draw_circuit()
    # Board.find_board()
    
def intitialize_game():
    selected = 0
    turn = 1
    q_counter = 0
    return turn,selected,q_counter

def get_row_col_from_mouse(pos):
    x,y = pos
    row = y // Square_Size
    col = x // Square_Size
    return(row,col)

def update():
    Board.update_board()
    Board.draw_squares(win)
    Board.draw_pieces(win)
    Board.draw_entangle_button(win)
    pygame.display.update()
    
def check_for_valid_selection(row,col,turn,selected):
    if Board.board_color[row][col] == turn:
        selected_piece = (row,col)
        selected = 1
        pos_moves = Board.check_valid_moves(selected_piece)
        print(pos_moves)
    else:
        selected_piece = None
    return selected_piece,selected

def change_selected_piece(row,col):
    selected_piece = (row,col)
    pos_moves = Board.check_valid_moves(selected_piece)
    print(pos_moves)
    q_counter = 0
    return selected_piece

def Convert_to_Q(C_pos):
    return(int(Cols/2*C_pos[0]+C_pos[1]//2))

def main():
    run = True
    clock = pygame.time.Clock()
    turn,selected,q_counter= intitialize_game()
    
    while run:
        clock.tick(FPS)
        
        for event in pygame.event.get():
            
            if event.type == pygame.QUIT:
                run = False
                Board.Qcirc.draw_circuit()
                
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                row,col = get_row_col_from_mouse(pos)
                if row == 0 and col == Cols-1:
                    Board.qmode = not(Board.qmode)
                    q_counter = 0
                    
                elif selected == 0:
                    selected_piece,selected = check_for_valid_selection(row,col,turn,selected)
                
                elif selected == 1 and Board.board_color[row][col] == turn:
                    selected_piece = change_selected_piece(row,col)
                    
                elif selected == 1 and Board.board_color[row][col] == 0 and \
                    Board.qmode == False:
                        new_position = (row,col)
                        Board.Qcirc.swap(Convert_to_Q(selected_piece),Convert_to_Q(new_position))
                        selected = 0
                        turn = - turn
                elif selected == 1 and Board.board_color[row][col] ==0 and \
                    Board.qmode == True:
                        if q_counter == 0:
                            new_pos1 = (row,col)
                            q_counter = 1
                        elif q_counter == 1:
                            new_pos2 = (row,col)
                            Board.Qcirc.sqrtswap(Convert_to_Q(selected_piece),\
                                                 Convert_to_Q(new_pos1), Convert_to_Q(new_pos2))
                            selected = 0
                            q_counter = 0
                            turn = -turn
                                       
                
            
        update()
        
    pygame.quit()
    

main()
    
    
    
    
    