import os
import sys
import signal
import pygame
import time
from pathlib import Path

import pygame_menu
from pygame_menu import themes
import cv2

from displayhatmini import DisplayHATMini

print("""PYGAME MEDIA DISPLAY""")

if pygame.vernum < (2, 0, 0):
    print("Need PyGame >= 2.0.0:\n    python3 -m pip install pygame --upgrade")
    sys.exit(1)
    
def _exit(sig, frame):
    global running
    running = False
    print("\nExiting!...\n")


def update_display():
    display_hat.st7789.set_window()
    # Grab the pygame screen as a bytes object
    pixelbytes = pygame.transform.rotate(screen, 180).convert(16, 0).get_buffer()
    # Lazy (slow) byteswap:
    pixelbytes = bytearray(pixelbytes)
    pixelbytes[0::2], pixelbytes[1::2] = pixelbytes[1::2], pixelbytes[0::2]
    # Bypass the ST7789 PIL image RGB888->RGB565 conversion
    for i in range(0, len(pixelbytes), 4096):
        display_hat.st7789.data(pixelbytes[i:i + 4096])


display_hat = DisplayHATMini(None)

pygame.init()

os.putenv('SDL_VIDEODRIVER', 'dummy')
pygame.display.init()  # Need to init for .convert() to work
pygame.display.set_mode((display_hat.WIDTH, display_hat.HEIGHT))
screen = pygame.Surface((display_hat.WIDTH, display_hat.HEIGHT))

signal.signal(signal.SIGINT, _exit)

# Plumbing to convert Display HAT Mini button presses into pygame events
def button_callback(pin):
    key = {
        display_hat.BUTTON_A: 'a',
        display_hat.BUTTON_B: 'b',
        display_hat.BUTTON_X: 'x',
        display_hat.BUTTON_Y: 'y'
    }[pin]
    event = pygame.KEYDOWN if display_hat.read_button(pin) else pygame.KEYUP
    pygame.event.post(pygame.event.Event(event, unicode=key, key=pygame.key.key_code(key)))

display_hat.on_button_pressed(button_callback)

def start_the_game():
    mainmenu._open(folder)
    
custom_theme = pygame_menu.themes.THEME_SOLARIZED.copy()
custom_theme.title_font = pygame_menu.font.FONT_FRANCHISE

mainmenu = pygame_menu.Menu('Memory Module v1', 320, 240, 
                                 theme=custom_theme, overflow=True)
mainmenu.add.button('Open', start_the_game)
mainmenu.add.button('Quit', pygame_menu.events.EXIT)

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

# Add buttons directly to the frame mainmenu.get_current()
file_types = ('.mp4', '.png') 
files = [f for f in os.listdir('.') if f.endswith(file_types)]

for file in files:
    folder.add.button(Path(file).stem, lambda f=file: open(f))
# clock = pygame.time.Clock()
# cap = cv2.VideoCapture('video.mp4')
# running, img = cap.read()
# shape = img.shape[1::-1]

running = True
while running:
        
    if mainmenu.is_enabled():
        mainmenu.get_current().update(pygame.event.get())
        mainmenu.get_current().draw(screen)
    
    
    
    # screen.blit(pygame.image.frombuffer(img.tobytes(), shape, "BGR"), (0, 0))
    update_display()
    # clock.tick(60)
    # running, img = cap.read()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            break
        if event.type == pygame.KEYUP:
            if event.key == pygame.key.key_code('x'):
                mainmenu.get_current()._index -= 1
            elif event.key == pygame.key.key_code('y'):
                mainmenu.get_current()._index += 1
            if mainmenu.get_current()._index > len(mainmenu.get_current().get_widgets()) - 1:
                mainmenu.get_current()._index = 0
            elif mainmenu.get_current()._index < 0:
                mainmenu.get_current()._index = len(mainmenu.get_current().get_widgets()) - 1
            widg = mainmenu.get_current().get_widgets()[mainmenu.get_current()._index]
            widg.select(update_menu=True)
            if event.key == pygame.key.key_code('a'):
                mainmenu.get_current().get_selected_widget().apply()
            mainmenu.get_current().get_scrollarea().scroll_to_rect(mainmenu.get_current().get_selected_widget().get_rect())
        if event.key == (pygame.key.key_code('b')):
            pygame_menu.events.EXIT

screen.fill((0, 0, 0))
update_display()
pygame.quit()
sys.exit(0)