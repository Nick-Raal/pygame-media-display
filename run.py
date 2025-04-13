import os
import sys
import signal
import pygame
import pygame_menu
from pygame_menu import themes
import cv2

from displayhatmini import DisplayHATMini

print("""Display HAT Mini: Basic Pygame Demo""")

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
    print(f"Button pressed: {pin}") 
    key = {
        display_hat.BUTTON_A: 'a',
        display_hat.BUTTON_B: 'b',
        display_hat.BUTTON_X: 'x',
        display_hat.BUTTON_Y: 'y'
    }[pin]
    event = pygame.KEYDOWN if display_hat.read_button(pin) else pygame.KEYUP
    pygame.event.post(pygame.event.Event(event, unicode=key, key=pygame.key.key_code(key)))
    print(f"Simulated KeyDown: key='{key}', key_code={pygame.key.key_code(key)}")

display_hat.on_button_pressed(button_callback)

def start_the_game():
    mainmenu._open()
 
def level_menu():
    pass

mainmenu = pygame_menu.Menu('Memory Module', 320, 240, 
                                 theme=themes.THEME_SOLARIZED)
mainmenu.add.button('Open', start_the_game)
mainmenu.add.button('Quit', pygame_menu.events.EXIT)

arrow = pygame_menu.widgets.LeftArrowSelection(arrow_size = (10, 15))

def open(f):
    pygame_menu.events.EXIT
    if f.endswith('.mp4'):
        clock = pygame.time.Clock()
        cap = cv2.VideoCapture(f.title)
        playing, img = cap.read()
        shape = img.shape[1::-1]
        while playing:
            screen.blit(pygame.image.frombuffer(img.tobytes(), shape, "BGR"), (0, 0))
            update_display()
            clock.tick(60)
            playing, img = cap.read()

folder = pygame_menu.Menu('Memories', 320, 240)
file_type = '.mp4'  # change to your file type
files = [f for f in os.listdir('.') if f.endswith(file_type)]
for file in files:
    folder.add.button(file.title, open(file))


# clock = pygame.time.Clock()
# cap = cv2.VideoCapture('video.mp4')
# running, img = cap.read()
# shape = img.shape[1::-1]

running = True
while running:
    
    if mainmenu.is_enabled():
        mainmenu.update(pygame.event.get())
        mainmenu.draw(screen)
        if (mainmenu.get_current().get_selected_widget()):
            arrow.draw(screen, mainmenu.get_current().get_selected_widget())
        
    # screen.blit(pygame.image.frombuffer(img.tobytes(), shape, "BGR"), (0, 0))
    update_display()
    # clock.tick(60)
    # running, img = cap.read()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            break
        if event.type == pygame.KEYUP:
            if mainmenu.is_enabled():
                if event.key == pygame.key.key_code('x'):
                    mainmenu._index -= 1
                elif event.key == pygame.key.key_code('y'):
                    mainmenu._index += 1
                if mainmenu._index > len(mainmenu.get_widgets()) - 1:
                        mainmenu._index = 0
                elif mainmenu._index < 0:
                    mainmenu._index = len(mainmenu.get_widgets()) - 1
            if event.key in (pygame.key.key_code('b'), pygame.K_ESCAPE):
                running = False
                break
                 

screen.fill((0, 0, 0))
update_display()
pygame.quit()
sys.exit(0)