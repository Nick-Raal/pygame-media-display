import os
import pygame

import subprocess

import pygame_menu
from pygame_menu import themes

from displayhatmini import DisplayHATMini
import pygame_menu.events

from media import Video

import socket
    
custom_theme = pygame_menu.themes.THEME_SOLARIZED.copy()
custom_theme.title_font = pygame_menu.font.FONT_FRANCHISE

class MemoryModule:
        
    def __init__(self, screen):
        
        self.screen = screen
        
        self.current_media_item = None
        self.clock = None
        self.img = None
        self.playing = False
        
        self.folder = pygame_menu.Menu('Memories', 320, 240, 
        enabled=False, 
        theme=custom_theme,
        overflow=True)
        self.folder.set_onclose(pygame_menu.events.BACK)

        file_types = ('.mp4') 
        media = [Video(f) for f in os.listdir('.') if f.endswith(file_types)]

        for med in media:
            self.folder.add.button(med.get_title(), lambda m=med: screen.blit(self.play(self.screen, m)))
            
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
                        break

                #Optionally wait for the process to fully exit
                process.wait()
                ssid_label._title=get_wifi_name()
            except Exception as e:
                return f"Error: {e}"
            


        self.settings = pygame_menu.Menu('Settings', width=320, height=240, enabled=False, theme=custom_theme)
        ip_address = socket.gethostbyname(socket.gethostname() + ".local")
        ip_label = self.settings.add.label(ip_address)
        #ip_label.set_font(font_size=10)
        ssid_label = self.settings.add.label(get_wifi_name())
        #ssid_label.set_font(font_size=10)
        change_network_button = self.settings.add.button("Change Network", change_wifi)
        self.settings.set_onclose(pygame_menu.events.BACK)

        self.mainmenu = pygame_menu.Menu('Memory Module', 320, 240, 
                                        theme=custom_theme, overflow=True)
        self.mainmenu.add.button('Open', self.folder)
        self.mainmenu.add.button('Settings', self.settings)
        self.mainmenu.add.button('Quit', pygame_menu.events.EXIT)
        
        self.mainmenu.set_onupdate(self.select)
        self.folder.set_onupdate(self.select)
        self.settings.set_onupdate(self.select)
        
    def select(self, event_list, menu):
        for event in event_list:
            print("Got this event: ", event)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.key.key_code('x'):
                    menu._index -= 1
                elif event.key == pygame.key.key_code('y'):
                    menu._index += 1
                elif event.key == (pygame.key.key_code('b')):
                    print(menu)
                    #menu.close()
                elif event.key == pygame.key.key_code('a'):
                    menu.get_selected_widget().apply()
                
                if menu._index > len(menu.get_widgets()) - 1:
                    menu._index = 0
                elif menu._index < 0:
                    menu._index = len(menu.get_widgets()) - 1
                widg = menu.get_widgets()[menu._index]
                widg.select(update_menu=True)
                if(menu.get_selected_widget()):
                    menu.get_scrollarea().scroll_to_rect(menu.get_selected_widget().get_rect())
            elif event.type == pygame.KEYUP:
                if event.key == pygame.key.key_code('b'):
                    print('close')
                    menu.close()
                    menu.enable()
    
    def updater(self, screen):      
        if self.playing:
            self.screen.blit(pygame.image.frombuffer(self.img.tobytes(), self.img.shape[1::-1], "BGR"), (0, 0))
            self.clock.tick(60)
            self.playing, self.img =  self.current_media_item.read()
            
        elif self.mainmenu.get_current().is_enabled():
            self.mainmenu.get_current().update(pygame.event.get())
            self.mainmenu.get_current().draw(screen)
        
            
    def play(self, m):
        self.mainmenu.get_current().disable()
        self.current_media_item, self.clock  = m.open()
        self.playing, self.img = self.current_media_item.read()


#classic control
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


    
    # mainmenu.set_onclose(_exit)

