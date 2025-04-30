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
import cProfile
import pstats
import io

print("""PYGAME MEDIA DISPLAY""")


def restart_program():
    """
    Restarts the program by finding the path to the python executable
    """
    
    print("Restarting...")
    pygame.quit()
    python = sys.executable
    os.execv(python, [python] + sys.argv)

if pygame.vernum < (2, 0, 0):
    print("Need PyGame >= 2.0.0:\n    python3 -m pip install pygame --upgrade")
    sys.exit(1)
    
    
if(__name__ == '__main__'):
    control = DisplayHatController()
    control.get_screen().fill((0, 0, 0))
    control.update_display([pygame.Rect(0, 0, 320, 240),])

    font = pygame.font.SysFont("Comic Sans MS", 30)
    multiline_text(control.get_screen(), "Welcome To Memory Module\nChecking for updates" ,font, (160, 120))
    control.update_display([pygame.Rect(0, 0, 320, 240),])
    #time.sleep(2)

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
                control.update_display([pygame.Rect(0, 0, 320, 240),])
                multiline_text(control.get_screen(), "Up to date" ,font, (160, 120))
                control.update_display([pygame.Rect(0, 0, 320, 240),])
                break
            elif "Updating" in line:
                control.get_screen().fill((0, 0, 0))
                control.update_display([pygame.Rect(0, 0, 320, 240),])
                multiline_text(control.get_screen(), "Update Found\nRestarting" ,font, (160, 120))
                control.update_display([pygame.Rect(0, 0, 320, 240),])
                #time.sleep(1)
                control.get_screen().fill((0, 0, 0))
                control.update_display([pygame.Rect(0, 0, 320, 240),])
                restart_program()
                break
        #wait for the process to fully exit
        process.wait()      
    except Exception as e:
        print(e)
    
def main():
    memmod = MemoryModule(control.get_screen())
    clock = pygame.time.Clock()
    running, dirty_rect =  memmod.updater()
    while running:
        control.update_display(dirty_rect)
        running, dirty_rect =  memmod.updater()
        clock.tick(60)
        print(clock.get_fps())
        
profiler = cProfile.Profile()
profiler.enable()

main()  # This will include calls to your Raspberry Pi display logic, etc.

profiler.disable()

# Print nicely formatted stats
s = io.StringIO()
stats = pstats.Stats(profiler, stream=s).sort_stats("cumtime")
stats.print_stats("update_display")

print(s.getvalue())

print("\nExiting!...\n")
control.screen.fill((0, 0, 0))
control.update_display([pygame.Rect(0, 0, 320, 240),])
pygame.quit()
sys.exit(0)
