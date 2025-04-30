"""
driver.py

Provides a class that handles the hardware interfacing with the displayhatmini
"""

import pygame
import os
import signal
import sys
import numpy as np
from displayhatmini import DisplayHATMini

class DisplayHatController:   
    def __init__(self):
        self.display_hat = DisplayHATMini(None)
        pygame.init()
        os.putenv('SDL_VIDEODRIVER', 'dummy')
        pygame.display.init()  # Need to init for .convert() to work
        pygame.display.set_mode((self.display_hat.WIDTH, self.display_hat.HEIGHT))
        self.screen = pygame.Surface((self.display_hat.WIDTH, self.display_hat.HEIGHT))
        for sig in [signal.SIGINT, signal.SIGTERM, signal.SIGHUP, signal.SIGQUIT]:
            signal.signal(sig, self._exit)
        self.display_hat.on_button_pressed(self.button_callback)
        

    def update_display(self):
        self.display_hat.st7789.set_window()
        # Grab the pygame screen as a bytes object
        surface = pygame.transform.flip(self.screen, False, True).convert(16,0)
        pixelbytes = surface.get_buffer()
        
        # Use numpy for efficient byteswap
        pixelbytes = np.frombuffer(pixelbytes, dtype=np.uint16)
        pixelbytes.byteswap(inplace=True)
        
        # Convert back to a bytearray (not bytes) which should work with SPI
        pixelbytes_bytearray = bytearray(pixelbytes)
        
        # Send in 4096-byte chunks
        for i in range(0, len(pixelbytes_bytearray), 4096):
            chunk = pixelbytes_bytearray[i:i + 4096]
            self.display_hat.st7789.data(chunk)
        
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
        print("\nExiting!...\n")
        self.screen.fill((0, 0, 0))
        self.update_display()
        pygame.quit()
        sys.exit(0)