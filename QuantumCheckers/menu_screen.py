from Constants import Width, Height, Grey, Red, Green, White, Black, Blue_Piece, Red_Piece, Transparent_Grey, Transparent_White, \
    Slightly_Transparent_White, Transparent, full_collapse_config, partial_collapse_config
import pygame
import pygame.gfxdraw
import pygame.freetype
import pygame.mixer
from pygame_button import Button
from main_screen import Game


screen = pygame.display.set_mode((Width, Height), pygame.DOUBLEBUF, 32)
run = True

def render_text(surface, x, y, text, color, font_size=Width * 0.05):
    font = pygame.freetype.Font('fonts/title.ttf', font_size)
    textsurface = font.render(text, fgcolor=color)[0]
    dx = int(textsurface.get_size()[0] / 2)
    dy = int(textsurface.get_size()[1] / 2)
    surface.blit(textsurface, (int(x - dx), int(y - dy)))

def make_button(x, y, w, h, text, callback):
    pygame.font.init()
    BUTTON_STYLE = {
        "hover_color": Grey,
        "clicked_color": Grey,
        "clicked_font_color": Green,
        "hover_font_color": Green,
        "font": pygame.font.Font('./fonts/button.ttf', 24),
        "font_color": Transparent_Grey
    }

    button = Button(
        (x - w//2, y - h//2, w, h), Black, callback, text=text, **BUTTON_STYLE
    )

    return button

def how_to_play():
    print("how to play")
    import webbrowser
    webbrowser.open('https://victorvwier.github.io/Quantum-Checkers-QSQI-Group-9/')  # Go to example.com

def start_game_full_collapse():
    print("start the game")
    game = Game(screen, full_collapse_config)
    game.play()
    global run
    run = False

def start_game_partial_collapse():
    print("start the game")
    game = Game(screen, partial_collapse_config)
    game.play()
    global run
    run = False

def draw_title(screen):
    font_size = 32
    render_text(screen, Width // 2, Height // 2.5 - font_size, "Quantum", White, font_size=70)
    render_text(screen, Width // 2, Height // 2.5 + font_size, "Checkers", White, font_size=70)

def draw_background(screen, index):
    bg = pygame.image.load("./img/gif2/frame_{:02d}.png".format((index % (43 * 8)) // 8))
    bg = pygame.transform.scale(bg, (Width, Height))
    screen.blit(bg, (0, 0, Width, Height))

def main():
    global run
    pygame.display.set_caption("Quantum checkers")
    FPS = 60
    icon = pygame.image.load('./img/icon.png')
    pygame.display.set_icon(icon)

    pygame.init()
    pygame.freetype.init()
    pygame.font.init()
    clock = pygame.time.Clock()

    start_button_full = make_button(Width // 2, Height // 1.9, Width // 2.5, Height // 16, "Start a full collapse game", start_game_full_collapse)
    start_button_partial = make_button(Width // 2, Height // 1.7, Width // 2.5, Height // 16, "Start a partial collapse game", start_game_partial_collapse)
    help_button = make_button(Width // 2, Height // 1.53, Width // 2.5, Height // 16, "How to play?", how_to_play)

    index = 0
    while run:
        draw_background(screen, index)
        index += 1
        draw_title(screen)
        start_button_full.update(screen)
        start_button_partial.update(screen)
        help_button.update(screen)
        pygame.display.update()
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            else:
                help_button.check_event(event)
                start_button_full.check_event(event)
                start_button_partial.check_event(event)
    pygame.quit()


main()


