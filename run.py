"""
run.py

This is the primary python module of the Memory Module system.
It brings together all the other modules on top of handling startup updates.
"""
import subprocess
import pygame
import pygame_menu
import os
import time
import sys
from driver import DisplayHatController
from util import multiline_text
from memorymodule import MemoryModule

print("""PYGAME MEDIA DISPLAY""")


def restart_program():
    print("Restarting...")
    pygame.quit()
    python = sys.executable
    os.execv(python, [python] + sys.argv)

if pygame.vernum < (2, 0, 0):
    print("Need PyGame >= 2.0.0:\n    python3 -m pip install pygame --upgrade")
    sys.exit(1)
    
control = DisplayHatController()
control.get_screen().fill((0, 0, 0))
control.update_display()

font = pygame.font.SysFont("Comic Sans MS", 30)
multiline_text(control.get_screen(), "Welcome To Memory Module\nChecking for updates" ,font, (160, 120))
control.update_display()
time.sleep(2)

try:
    process = subprocess.Popen(
        ["git", "pull", "origin", "main"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,  # ensures output is decoded into strings
    )
    
    # Wait for the specific messages
    for line in process.stdout:
        print(line.strip())  # optional: print the output live
        if "Already up to date." in line:
            control.get_screen().fill((0, 0, 0))
            control.update_display()
            multiline_text(control.get_screen(), "Up to date" ,font, (160, 120))
            control.update_display()
            break
        elif "Updating" in line:
            control.get_screen().fill((0, 0, 0))
            control.update_display()
            multiline_text(control.get_screen(), "Update Found\nRestarting" ,font, (160, 120))
            control.update_display()
            time.sleep(1)
            control.get_screen().fill((0, 0, 0))
            control.update_display()
            restart_program()
            break
    #wait for the process to fully exit
    process.wait()      
except Exception as e:
    print(e)
   
   
memmod = MemoryModule(control.get_screen())
running = True 
while running:
    memmod.updater(control.get_screen())
    control.update_display()

