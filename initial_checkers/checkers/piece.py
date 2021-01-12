import pygame
from .constants import Black, White, Square_Size, Gold

class piece:
    Padding = 15
    Outline = 5
    
    def __init__(self,row,col,color):
        self.row = row
        self.col = col
        self.color = color
        self.outer_color = color
        self.king = False
        self.x = 0
        self.y = 0
        self.calc_pos()
        
    def calc_pos(self):
        self.x = Square_Size * self.col + Square_Size // 2
        self.y = Square_Size * self.row + Square_Size // 2
      
        
    def make_king(self):
        self.king = True
        
    def draw(self, win):
        radius = Square_Size//2 - self.Padding
        if self.king:
            self.outer_color = Gold
        
        pygame.draw.circle(win,self.outer_color, (self.x,self.y),radius+self.Outline)
        pygame.draw.circle(win,self.color, (self.x,self.y),radius)
        
    def move(self,row,col):
        self.row = row
        self.col = col
        self.calc_pos()
        
    def __repr__ (self):
        return str(self.color)