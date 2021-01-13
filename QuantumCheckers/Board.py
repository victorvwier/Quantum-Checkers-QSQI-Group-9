import pygame
from Constants import Rows,Cols,Piece_Rows,Square_Size,Grey,\
    Board_Brown,Board_White,Red,Green,White,Black
from QuantumCircuit import Quantumcircuit
import numpy as np

class Board:
    
    def __init__(self):
        self.n_tiles = Rows*Cols//2
        self.Qcirc = Quantumcircuit(Rows,Cols,Piece_Rows)
        self.board = np.zeros((Rows,Cols))
        self.board_color = np.zeros((Rows,Cols))
        self.white_left = self.black_left = Cols*Piece_Rows//2
        self.update_board()
        self.qmode = False
        
    def update_board(self):
        
        for i in range (self.n_tiles):
            self.Qcirc.Qboard[i]= self.Qcirc.get_probability(i)
        j = 0
        for row in range(Rows):
            for col in range (row % 2,Rows,2):
                self.board[row][col] = self.Qcirc.Qboard[j]
                self.board_color[row][col] = self.Qcirc.color[j]
                j+=1

        
    
    def draw_squares(self,win):
        win.fill(Board_Brown)
        for row in range(Rows):
            for col in range (row % 2,Rows,2):
                pygame.draw.rect(win,Board_White,(row*Square_Size,\
                                col*Square_Size,Square_Size,Square_Size))
        pygame.draw.rect(win,Grey,((Rows-1)*Square_Size,0\
                        ,Square_Size,Square_Size))
        
    def draw_entangle_button(self, win ):
        pygame.font.init()
        myfont = pygame.font.SysFont('Arial', 18)
        if self.qmode == False:
            textsurface = myfont.render('Select', False, Green)
            win.blit(textsurface,((Rows-1)*Square_Size+10,5))
            textsurface = myfont.render('Q_mode', False, Green)
            win.blit(textsurface,((Rows-1)*Square_Size+10,30))
        else:
            textsurface = myfont.render('Deselect', False, Red)
            win.blit(textsurface,((Rows-1)*Square_Size+10,5))
            textsurface = myfont.render('Q_mode', False, Red)
            win.blit(textsurface,((Rows-1)*Square_Size+10,30))
        
    def draw_pieces(self,win):
        radius = 30
        for row in range (Rows):
            for col in range (Cols):
                if self.board_color[row][col] == 1:
                    x = col*Square_Size + Square_Size //2
                    y = row*Square_Size + Square_Size //2
                    my_color = pygame.Color(255,255,255,int(self.board[row][col]*255))
                    self._draw_circles(win,my_color,(x,y),radius)
                    
                if self.board_color[row][col] == -1:
                    x = col*Square_Size + Square_Size //2
                    y = row*Square_Size + Square_Size //2
                    my_color = pygame.Color(0,0,0,int(abs(self.board[row][col]*255)))
                    self._draw_circles(win,my_color,(x,y),radius)
                    
    def _draw_circles(self,surface,color,center,radius):
        target_rect = pygame.Rect(center, (0, 0)).inflate((radius * 2, radius * 2))
        shape_surf = pygame.Surface(target_rect.size, pygame.SRCALPHA)
        pygame.draw.circle(shape_surf, color, (radius, radius), radius)
        surface.blit(shape_surf, target_rect)
        
    def check_valid_moves(self,selected_piece):
        
        moves = {}
        left = selected_piece[1] -1
        right = selected_piece[1] + 1
        row = selected_piece[0]
        color = self.board_color[selected_piece[0]][selected_piece[1]]
        
        if color == -1:
            moves.update(self._traverse_left(row-1,max(row-3,-1),-1,color,left))
            moves.update(self._traverse_right(row-1,max(row-3,-1),-1,color,right))
        
        if color == 1:
            moves.update(self._traverse_left(row+1,min(row+3,Rows),1,color,left))
            moves.update(self._traverse_right(row+1,min(row+3,Rows),1,color,right))
            
        return moves
    
    def _traverse_left(self,start,stop,step,color,left,skipped=[]):
        moves = {}
        last = []
        for r in range(start,stop,step):
            if left < 0:
                break
            
            current = self.board[r][left]
            if current == 0:
                if skipped and not last:
                    break
                elif skipped:
                    moves[(r,left)]= last+skipped
                else:
                    moves[(r,left)] = last
                    
                if last:
                    if step == -1:
                        row = max(r-3,0)
                    else:
                        row = min (r+3,Rows)
                        
                    moves.update(self._traverse_left(r+step,row,step,color,left-1,skipped=last))
                    moves.update(self._traverse_right(r+step,row,step,color,left+1,skipped=last))
                break
                        
            elif current.color == color:
                break
            
            else:
                last = [current]
            
            
            left -= 1
        return moves
    
    def _traverse_right(self,start,stop,step,color,right,skipped=[]):
        moves = {}
        last = []
        for r in range(start,stop,step):
            if right >= Cols:
                break
            
            current = self.board[r][right]
            if current == 0:
                if skipped and not last:
                    break
                elif skipped:
                    moves[(r,right)]= last+skipped
                else:
                    moves[(r,right)] = last
                    
                if last:
                    if step == -1:
                        row = max(r-3,0)
                    else:
                        row = min (r+3,Rows)
                        
                    moves.update(self._traverse_left(r+step,row,step,color,right-1,skipped=last))
                    moves.update(self._traverse_right(r+step,row,step,color,right+1,skipped=last))
                break
                        
            elif current.color == color:
                break
            
            else:
                last = [current]
            
            
            right += 1
            
        return moves
        
        