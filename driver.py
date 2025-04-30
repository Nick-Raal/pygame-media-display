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
        

    def update_display(self, dirty_rects):

        for dirty_rect in dirty_rects:
            # Extract just this portion of the screen
            subsurface = self.screen.subsurface(dirty_rect)
            # Rotate and convert the subsurface
            rotated = pygame.transform.rotate(subsurface, 180).convert(16, 0)
            

            # Set the window for this specific rectangle
            self.display_hat.st7789.set_window(
                dirty_rect.x, dirty_rect.y, 
                dirty_rect.x + dirty_rect.width - 1, 
                dirty_rect.y + dirty_rect.height - 1
            )
            print("ao ", dirty_rect)
            
            # Process pixels for this rectangle only
            pixelbytes = np.frombuffer(rotated.get_buffer(), dtype=np.uint16)
            pixelbytes = pixelbytes.byteswap()
            data = bytearray(pixelbytes)
            
            # Send the data for just this rectangle
            chunk_size = 4096
            for i in range(0, len(data), chunk_size):
                self.display_hat.st7789.data(data[i:i + chunk_size])
        
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