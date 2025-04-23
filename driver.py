import pygame
import pygame_menu
import os
import signal
import sys
from displayhatmini import DisplayHATMini

class DisplayHatController:   
    def __init__(self):
        self.display_hat = DisplayHATMini(None)
        pygame.init()
        os.putenv('SDL_VIDEODRIVER', 'dummy')
        pygame.display.init()  # Need to init for .convert() to work
        pygame.display.set_mode((self.display_hat.WIDTH, self.display_hat.HEIGHT))
        self.screen = pygame.Surface((self.display_hat.WIDTH, self.display_hat.HEIGHT))
        signal.signal(signal.SIGINT, self._exit)

    def update_display(self):
        self.display_hat.st7789.set_window()
        # Grab the pygame screen as a bytes object
        pixelbytes = pygame.transform.rotate(self.screen, 180).convert(16, 0).get_buffer()
        # Lazy (slow) byteswap:
        pixelbytes = bytearray(pixelbytes)
        pixelbytes[0::2], pixelbytes[1::2] = pixelbytes[1::2], pixelbytes[0::2]
        # Bypass the ST7789 PIL image RGB888->RGB565 conversion
        for i in range(0, len(pixelbytes), 4096):
            self.display_hat.st7789.data(pixelbytes[i:i + 4096])
        
    # Plumbing to convert Display HAT Mini button presses into pygame events
    def button_callback(self, pin):
        key = {
            self.display_hat.BUTTON_A: 'a',
            self.display_hat.BUTTON_B: 'b',
            self.display_hat.BUTTON_X: 'x',
            self.display_hat.BUTTON_Y: 'y'
        }[pin]
        event = pygame.KEYDOWN if self.display_hat.read_button(pin) else pygame.KEYUP
        pygame.event.post(pygame.event.Event(event, unicode=key, key=pygame.key.key_code(key)))

    def get_screen(self):
        return self.screen

    def _exit(self, sig,frame):
        global running
        running = False
        print("\nExiting!...\n")
        self.screen.fill((0, 0, 0))
        self.update_display()
        pygame.quit()
        sys.exit(0)