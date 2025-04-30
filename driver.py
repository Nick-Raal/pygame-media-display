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
            x1, y1 = dirty_rect.topleft
            x2, y2 = dirty_rect.bottomright
            x2 -= 1  # Convert from exclusive to inclusive bounds
            y2 -= 1
            
            # Adjust for 180 degree rotation if needed
            # Since you're rotating the surface, we need to adjust coordinates too
            width, height = self.screen.get_size()
            rotated_x1 = width - x2 - 1
            rotated_y1 = height - y2 - 1
            rotated_x2 = width - x1 - 1
            rotated_y2 = height - y1 - 1
            
            # Set window with rotated coordinates
            self.display_hat.st7789.set_window(
                rotated_x1, rotated_y1,
                rotated_x2, rotated_y2
            )
            
            # Extract just this portion of the screen
            subsurface = self.screen.subsurface(dirty_rect)
            # Rotate and convert the subsurface
            rotated = pygame.transform.rotate(subsurface, 180).convert(16, 0)
        
            
            # Process pixels for this rectangle only
            pixelbytes = np.frombuffer(rotated.get_buffer(), dtype=np.uint16)
            pixelbytes = pixelbytes.byteswap()
            data = bytearray(pixelbytes)
            
            # Send the data for just this rectangle
            chunk_size = 8192
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