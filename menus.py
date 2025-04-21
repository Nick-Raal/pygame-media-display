import pygame
import pygame_menu
import cv2
import time

from run import update_display, screen, _exit


    
custom_theme = pygame_menu.themes.THEME_SOLARIZED.copy()
custom_theme.title_font = pygame_menu.font.FONT_FRANCHISE

def open(f):
    pygame_menu.events.EXIT
    if f.endswith('.mp4'):
        clock = pygame.time.Clock()
        cap = cv2.VideoCapture(f)
        playing, img = cap.read()
        shape = img.shape[1::-1]
        while playing:
            screen.blit(pygame.image.frombuffer(img.tobytes(), shape, "BGR"), (0, 0))
            update_display()
            clock.tick(60)
            playing, img = cap.read()
        cap.release()
    elif f.endswith('.png'):
        img = cv2.imread(f)
        shape = img.shape[1::-1]
        screen.blit(pygame.image.frombuffer(img.tobytes(), shape, "BGR"), (0, 0))
        update_display()
        time.sleep(2)
        


folder = pygame_menu.Menu('Memories', 320, 240, 
    enabled=False, 
    theme=custom_theme,
    overflow=True)
folder.set_onclose(pygame_menu.events.BACK)

file_types = ('.mp4', '.png') 
files = [f for f in os.listdir('.') if f.endswith(file_types)]

for file in files:
    folder.add.button(Path(file).stem, lambda f=file: open(f))

mainmenu = pygame_menu.Menu('Memory Module', 320, 240, 
                                 theme=custom_theme, overflow=True)
mainmenu.add.button('Open', folder)
mainmenu.add.button('Quit', pygame_menu.events.EXIT)
mainmenu.set_onclose(_exit)