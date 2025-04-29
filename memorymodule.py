"""
memorymodule.py

This package contains the MemoryModule class, which controls a memory module
"""

import os
import pygame

import asyncio

import subprocess

import pygame_menu
from pygame_menu import themes

from displayhatmini import DisplayHATMini
import pygame_menu.events

from media import Video, Image

from themes import custom_theme

import socket

async def button_resize(button, start, end, time):
    current = start
    current_time = 0
    time_step = 0.01
    while current_time <= time:
        current = min(current_time / time, 1)  # clamp between 0 and 1
        eased_progress = 1 - (1 - current) ** 2
        new_size = start + (end - start) * eased_progress
        button.scale(new_size, new_size, True, True)
        button.render()
        print(current_time, " - ", new_size)
        await asyncio.sleep(time_step)
        current_time += time_step
    
class MemoryModule:
    """
    MemoryModule manages a multimedia user interface using pygame_menu.
    
    This class provides an interactive interface for playing videos and displaying images,
    as well as viewing network settings and switching Wi-Fi connections. It supports both
    image (.png, .jpeg) and video (.mp4) files.

    Attributes:
        running (bool): Indicates whether the module should keep running.
        screen (pygame.Surface): The display surface where content is rendered.
        current_media_item (Video or Image): The currently loaded media item.
        clock (pygame.time.Clock): Clock object for managing frame rate.
        img (np.ndarray): Current frame/image being displayed.
        playing (bool): Flag indicating if media is being actively played.
        folder (pygame_menu.Menu): Menu containing all media files.
        settings (pygame_menu.Menu): Settings menu with IP and Wi-Fi info.
        mainmenu (pygame_menu.Menu): The main menu interface.

    Methods:
        __init__(screen): Initializes the menu system and loads media.
        select(event_list, menu): Handles custom navigation logic for menu control.
        exit_handler(event_list): Handles exit behavior while playing media.
        updater(screen): Updates the display by showing media or menu content.
        play(m): Begins playing a selected media item.
        quit(): Sets the running flag to False to exit the main loop.
    """

        
    def __init__(self, screen):
        """
        Initializes the Memory Module by creating menus.
        
        args:
            screen (pygame.Surface): The surface the Memory Module will be rendered onto
        """
        self.running = True
        
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

        video_file_types = ('.mp4',) 
        image_file_types = ('.png', '.jpeg')
        media_file_types = video_file_types + image_file_types

        media = [
            Video(f) if f.endswith(video_file_types) else Image(f)
            for f in os.listdir('.') if f.endswith(media_file_types)
        ]

        for med in media:
            self.folder.add.button(med.get_title(), lambda m=med: self.play(m))
            
        def get_wifi_name():
            """
            Uses subprocess along with the ncli command to find the SSID of the currently connected wifi network.
            
            Returns:
                str: The ssid of the current network.
            """
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
            """
            Uses subprocess to launch BalenaOS' wifi-connect system which allows the user to connect to a captive wifi portal and change
            the memory module's current network
            
            This function waits until internet connectivity is established via the portal, and 
            then updates the displayed SSID label with the newly connected network.

            Returns:
                str or None: Returns an error message string if an exception occurs, 
                otherwise returns None.
            """
            
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
        ip_label.set_font(pygame_menu.font.FONT_NEVIS, 22, (255, 255, 255), (255, 255, 255), (255, 255, 255), (255, 255, 255), None, False)
        ssid_label = self.settings.add.label(get_wifi_name())
        ssid_label.set_font(pygame_menu.font.FONT_NEVIS, 22, (255, 255, 255), (255, 255, 255), (255, 255, 255), (255, 255, 255), None, False)
        change_network_button = self.settings.add.button("Change Network", change_wifi)
        self.settings.set_onclose(pygame_menu.events.BACK)

        self.mainmenu = pygame_menu.Menu('Memory Module', 320, 240, 
                                        theme=custom_theme, overflow=True)
        
        open_button = self.mainmenu.add.button('Open', self.folder)
        settings_button = self.mainmenu.add.button('Settings', self.settings)
        quit_button = self.mainmenu.add.button('Quit', self.quit)
        def button_select_handler(buttons):
            for b in buttons:
                if not b.is_selected():
                    asyncio.create_task(button_resize(b, 1.2, 1, 0.2))
                else:
                    asyncio.create_task(button_resize(b, 1.0, 1.2, 0.2))
                    
        mainmenu_buttons = [open_button, settings_button, quit_button]
        for b in mainmenu_buttons:
            b.set_onselect(lambda: button_select_handler(mainmenu_buttons))
        
        self.mainmenu.set_onupdate(self.select)
        self.folder.set_onupdate(self.select)
        self.settings.set_onupdate(self.select)
        

        
    def select(self, event_list, menu):
        """
        Handle custom menu navigation using physical buttons.
        
        Typically used as an on_update callback by the various pygame_menu.Menus that
        comprise Memory Module

        Args:
            event_list (list): A list of pygame events.
            menu (pygame_menu.Menu): The currently focused menu.
        """
        
        for event in event_list:
            print("Got this event: ", event)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.key.key_code('x'):
                    menu._index -= 1
                elif event.key == pygame.key.key_code('y'):
                    menu._index += 1
                elif event.key == (pygame.key.key_code('b')):
                    print(menu)
                    menu.close()
                    menu.enable()
                    
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
                    
    def exit_handler(self, event_list):
        """
        Checks for one specific event and exits playback if that event is found.
        
        Used for exit_handling in logic outside of the pygame_menu update system
        
        Args:
            event_list (list): A list of pygame events
        """
        
        for event in event_list:
            if event.type == pygame.KEYUP:
                if event.key == pygame.key.key_code('b'):
                    print('close')
                    self.playing = False
                        
    def updater(self): 
        """
        Controls the central logic of the MemoryModule. 
        This function should be called by a higher level package each frame.
        
        Returns:
            bool: self.running, which determines if the module is running or not
        """
        if self.playing:
            self.screen.blit(pygame.image.frombuffer(self.img.tobytes(), self.img.shape[1::-1], "BGR"), (0, 0))
            self.clock.tick(60)
            self.playing, self.img =  self.current_media_item.read()  
            self.exit_handler(pygame.event.get())
        elif not self.playing and not self.mainmenu.get_current().is_enabled():
            self.mainmenu.get_current().enable()
        else:
            if self.mainmenu.get_current().is_enabled():
                self.mainmenu.get_current().update(pygame.event.get())
                try:
                    self.mainmenu.get_current().draw(self.screen)
                except RuntimeError as e:
                    print("Tried to draw a disabled menu!", e)
                    
        return self.running
            
    def play(self, m):
        """
        Opens and prepares a media file (a photo or a video) for playback
        
        Args:
            m (Video or Image): A media item with `.open()` and `.read()` methods.
        """
        self.mainmenu.get_current().disable()
        self.current_media_item, self.clock  = m.open(self.clock)
        self.playing, self.img = self.current_media_item.read()

    def quit(self):
        """
        Sets the self.running flag to False, which effectively exits the program
        """
        self.running = False