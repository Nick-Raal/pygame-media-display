import subprocess
import pygame
import pygame_menu
import sys
from driver import DisplayHatController

print("""PYGAME MEDIA DISPLAY""")

if pygame.vernum < (2, 0, 0):
    print("Need PyGame >= 2.0.0:\n    python3 -m pip install pygame --upgrade")
    sys.exit(1)
    
control = DisplayHatController()



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