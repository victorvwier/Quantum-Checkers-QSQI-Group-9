import pygame

# game details
Rows = 6
Cols = 6
Piece_Rows = 1
Full_Collapse = True

# gui settings
Width = 950
Height = int((Rows + 0.5) / Rows * Width)
Square_Size = Width // Cols

# colors
Red = (255, 0, 0)
White = (255, 255, 255)
Gold = (239, 235, 14)
Grey = (46, 46, 46)
Green = (0, 255, 0)
Transparent_White = (255, 255, 255, 128)
Slightly_Transparent_White = (255, 255, 255, 172)
Transparent_Grey = (128, 128, 128, 128)
Blue_Piece = (26, 18, 112)
Red_Piece = (112, 18, 18)
Black = (0, 0, 0)
Blue = (0, 0, 255)
Board_Brown = (241, 241, 241)
Board_White = (163, 180, 216)

crown_file = 'crown.png'
if Rows == 4:
    crown = pygame.transform.scale(pygame.image.load(crown_file),(123,75))
else:
    crown = pygame.transform.scale(pygame.image.load(crown_file),(82,50))