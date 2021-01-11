import pygame
from checkers.constants import *
from checkers.board import Board
from checkers.game import Game

win = pygame.display.set_mode((Width,Height))
pygame.display.set_caption('Checkers')
FPS = 60

def get_row_col_from_mouse(pos):
    x,y = pos
    row = y // Square_Size
    col = x // Square_Size
    return(row,col)


def main():
    run = True
    clock = pygame.time.Clock()
    game = Game(win)
    
    
    while run:
        clock.tick(FPS)
        
        if game.winner() != None:
            print(game.winner())
            run = False
        
        for event in pygame.event.get():
            
            if event.type == pygame.QUIT:
                run = False
                
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                row,col = get_row_col_from_mouse(pos)
                game.select(row,col)
            
        game.update()
        
    pygame.quit()
    
main()