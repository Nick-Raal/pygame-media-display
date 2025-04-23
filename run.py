import os
import sys
import signal
import pygame

import pygame_menu
import cv2
import time

import subprocess

import pygame_menu
from pygame_menu import themes

from displayhatmini import DisplayHATMini
import pygame_menu.events

from media import Video

import socket

print("""PYGAME MEDIA DISPLAY""")

if pygame.vernum < (2, 0, 0):
    print("Need PyGame >= 2.0.0:\n    python3 -m pip install pygame --upgrade")
    sys.exit(1)
    
def _exit(sig, frame):
    global running
    running = False
    print("\nExiting!...\n")
    screen.fill((0, 0, 0))
    update_display()
    pygame.quit()
    sys.exit(0)


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


    
custom_theme = pygame_menu.themes.THEME_SOLARIZED.copy()
custom_theme.title_font = pygame_menu.font.FONT_FRANCHISE

def play(m):
    clock = pygame.time.Clock()
    playing, var = m.open()
    while playing:
        screen.blit(pygame.image.frombuffer(var.tobytes(), var.shape[1::-1], "BGR"), (0, 0))
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break
            if event.type == pygame.KEYDOWN:
                    if event.key == (pygame.key.key_code('b')):
                        playing=False


# def open(f):
#     pygame_menu.events.EXIT
#     if f.endswith('.mp4'):
#         clock = pygame.time.Clock()
#         cap = cv2.VideoCapture(f)
#         playing, img = cap.read()
#         shape = img.shape[1::-1]
#         while playing:
#             screen.blit(pygame.image.frombuffer(img.tobytes(), shape, "BGR"), (0, 0))
#             update_display()
#             clock.tick(60)
#             playing, img = cap.read()
#             for event in pygame.event.get():
#                 if event.type == pygame.QUIT:
#                     running = False
#                     break
#                 if event.type == pygame.KEYDOWN:
#                     if event.key == (pygame.key.key_code('b')):
#                         playing=False

#         cap.release()
#     elif f.endswith('.png'):
#         img = cv2.imread(f)
#         shape = img.shape[1::-1]
#         screen.blit(pygame.image.frombuffer(img.tobytes(), shape, "BGR"), (0, 0))
#         update_display()
#         playing = True
#         while playing:
#             for event in pygame.event.get():
#                 if event.type == pygame.QUIT:
#                     running = False
#                     break
#                 if event.type == pygame.KEYDOWN:
#                     if event.key == (pygame.key.key_code('b')):
#                         playing=False


folder = pygame_menu.Menu('Memories', 320, 240, 
    enabled=False, 
    theme=custom_theme,
    overflow=True)
folder.set_onclose(pygame_menu.events.BACK)

file_types = ('.mp4') 
media = [Video(f) for f in os.listdir('.') if f.endswith(file_types)]

for med in media:
    folder.add.button(med.get_title(), lambda m=med: play(m))
    
settings = pygame_menu.Menu('Settings', width=320, height=240, enabled=False, theme=custom_theme)
ip_address = socket.gethostbyname(socket.gethostname() + ".local")
settings.add.label(ip_address)


def get_wifi_name():
    try:
        result = subprocess.check_output(
            ["nmcli", "-t", "-f", "active,ssid", "dev", "wifi"],
            encoding="utf-8"
        )
        for line in result.strip().split("\n"):
            if line.startswith("yes:"):
                return line.split(":")[1]
    except Exception as e:
        return f"Error: {e}"
    
def change_wifi():
    try:
        # Start wifi-connect and capture its output
        process = subprocess.Popen(
            ["sudo", "wifi-connect", "--portal-ssid", "MemoryModule"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,  # ensures output is decoded into strings
        )

        # Wait for the specific message
        for line in process.stdout:
            print(line.strip())  # optional: print the output live
            if "Internet connectivity established" in line:
                print("🎉 Network connected!")
                break

        #Optionally wait for the process to fully exit
        process.wait()
        ssid_label._title=get_wifi_name()
    except Exception as e:
        return f"Error: {e}"
    

ssid_label = settings.add.label(get_wifi_name())
change_network_button = settings.add.button("Change Network", change_wifi)
settings.set_onclose(pygame_menu.events.BACK)

mainmenu = pygame_menu.Menu('Memory Module', 320, 240, 
                                 theme=custom_theme, overflow=True)
mainmenu.add.button('Open', folder)
mainmenu.add.button('Settings', settings)
mainmenu.add.button('Quit', pygame_menu.events.EXIT)
mainmenu.set_onclose(_exit)


running = True
while running:
        
    if mainmenu.get_current().is_enabled():
        mainmenu.get_current().update(pygame.event.get())
        mainmenu.get_current().draw(screen)
    
    update_display()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            screen.fill((0, 0, 0))
            update_display()
            pygame.quit()
            sys.exit(0)
            break
        if event.type == pygame.KEYDOWN:
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
            if(mainmenu.get_current().get_selected_widget()):
                mainmenu.get_current().get_scrollarea().scroll_to_rect(mainmenu.get_current().get_selected_widget().get_rect())
            if event.key == (pygame.key.key_code('b')):
                mainmenu.get_current().close()
                mainmenu.get_current().enable()

screen.fill((0, 0, 0))
update_display()
pygame.quit()
sys.exit(0)