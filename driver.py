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

        # Rotate and convert the Pygame surface
        surface = pygame.transform.rotate(self.screen, 180)
        surface = surface.convert(16, 0)  # Assumes RGB565 format

        # Get raw bytes from the surface
        pixelbytes = bytearray(surface.get_buffer())

        # More efficient in-place byte swap (still pure Python)
        for i in range(0, len(pixelbytes), 2):
            pixelbytes[i], pixelbytes[i + 1] = pixelbytes[i + 1], pixelbytes[i]

        # Send in larger chunks if your driver allows
        CHUNK_SIZE = 8192  # Try 8192 or 16384 if 4096 is too small
        for i in range(0, len(pixelbytes), CHUNK_SIZE):
            self.display_hat.st7789.data(pixelbytes[i:i + CHUNK_SIZE])
        
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