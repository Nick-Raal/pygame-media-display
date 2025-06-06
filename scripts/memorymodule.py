"""
memorymodule.py

This package contains the MemoryModule class, which controls a memory module
"""

import os
import pygame

import subprocess

import pygame_menu
from pygame_menu import themes

from displayhatmini import DisplayHATMini
import pygame_menu.events

from media import Video, Image

import pygame_menu.menu
from themes import custom_theme

import socket
    
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
        self.has_drawn = False
        
        self.selector_image = pygame.image.load("../graphics/selector.png").convert()
        
        self.folder = MenuWrapper('Memories', 320, 240, 
        enabled=False, 
        theme=custom_theme,
        overflow=True)
        self.folder.set_onclose(pygame_menu.events.BACK)

        video_file_types = ('.mp4',) 
        image_file_types = ('.png', '.jpeg')
        media_file_types = video_file_types + image_file_types

        media = [
            Video(f) if f.endswith(video_file_types) else Image(f)
            for f in os.listdir('..') if f.endswith(media_file_types)
        ]
        
        for med in media:
            self.folder.add_button(med.get_title(), lambda m=med: self.play(m))
            
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
            
        self.settings = MenuWrapper('Settings', width=320, height=240, enabled=False, theme=custom_theme)
        
        ip_address = socket.gethostbyname(socket.gethostname() + ".local")
        ip_label = self.settings.add.label(ip_address)
        ip_label.set_font(pygame_menu.font.FONT_NEVIS, 22, (255, 255, 255), (255, 255, 255), (255, 255, 255), (255, 255, 255), None, False)
        ssid_label = self.settings.add.label(get_wifi_name())
        ssid_label.set_font(pygame_menu.font.FONT_NEVIS, 22, (255, 255, 255), (255, 255, 255), (255, 255, 255), (255, 255, 255), None, False)
        self.settings.add_button("Change Network", change_wifi)
        
        self.settings.set_onclose(pygame_menu.events.BACK)

        self.mainmenu = MenuWrapper('', 320, 240, 
                                        theme=custom_theme, overflow=True)
        
        self.mainmenu.add_button('Open', self.folder)
        self.mainmenu.add_button('Settings', self.settings)
        self.mainmenu.add_button('Quit', self.quit)
        
        self.select_rect = SelectRect(0, 0, 20, 50, self.mainmenu.buttons[0].get_rect().centery)
        
        #TODO: Change this into a loop structure
        self.mainmenu.add_select_rect_callbacks(self.select_rect)
        self.settings.add_select_rect_callbacks(select_rect=self.select_rect)
        self.folder.add_select_rect_callbacks(self.select_rect)
        
        self.select_rect.reset_position(self.mainmenu)
        
        self.mainmenu.set_onupdate(self.select)
        self.folder.set_onupdate(self.select)
        self.settings.set_onupdate(self.select)
        
        self.mainmenu.set_onbeforeopen(self.need_to_draw)
        self.folder.set_onbeforeopen(self.need_to_draw)
        self.settings.set_onbeforeopen(onbeforeopen=self.need_to_draw)
        
    def drawing_handler(self):
        new_rect, old_rect = self.select_rect.update()
        if not self.has_drawn:
            #print("draw new")
            self.mainmenu.draw(self.screen)
            self.screen.blit(self.selector_image, self.select_rect.topleft)
            self.has_drawn=True
            return [pygame.Rect(0,0,320,240),]
        else:
            # Redraw the menu - this will clear the old rectangle position
            self.mainmenu.draw(self.screen)
            
            # Return both rectangles as dirty areas
            # Making them slightly larger to ensure no artifacts remain
            expanded_old = old_rect.inflate(20, 20)
            expanded_new = new_rect.inflate(20, 20)
            
            # Draw the rectangle at its new position
            self.screen.blit(self.selector_image, self.select_rect.topleft)
            
            return [expanded_new.unionall(tuple([expanded_old])),]
            #return [pygame.Rect(0,0,320,240),]
            
    def need_to_draw(self, from_menu, to_menu):
        self.select_rect.reset_position(to_menu)
        self.has_drawn = False
        
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
            if event.type == pygame.KEYDOWN:
                old_index = menu._index
                
                if event.key == pygame.key.key_code('x'):
                    menu._index -= 1
                elif event.key == pygame.key.key_code('y'):
                    menu._index += 1
                elif event.key == (pygame.key.key_code('b')):
                    # Store reference to the current menu before closing
                    current_menu = menu
                    print("oldmenu ", current_menu.get_title())
                    
                    # Close the current menu
                    menu.close()
                    
                    # Get the new current menu after closing
                    new_current = self.mainmenu.get_current()
                    
                    # Manually trigger onbeforeopen
                    if new_current != current_menu:  # Only if we actually changed menus
                        print("changed menus")
                        self.need_to_draw(current_menu, to_menu=new_current)
                    
                    print("curmenu ", new_current.get_title())
                    
                elif event.key == pygame.key.key_code('a'):
                    menu.get_selected_widget().apply()
                
                # Handle wrap-around navigation
                if menu._index > len(menu.get_widgets()) - 1:
                    menu._index = 0
                elif menu._index < 0:
                    menu._index = len(menu.get_widgets()) - 1
                
                # Only update selection if the index actually changed
                if old_index != menu._index:
                    # Select the widget at the new index
                    widget = menu.get_widgets()[menu._index]
                    widget.select(update_menu=True)
                    
                    # Only scroll to the widget if it's actually selected
                    if menu.get_selected_widget() == widget:
                        # First check if widget is already visible before scrolling
                        widget_rect = widget.get_rect()
                        scroll_area = menu.get_scrollarea()
                        
                        # Get visible area and widget position in absolute coordinates
                        visible_rect = scroll_area.get_view_rect()
                        widget_pos = scroll_area.to_absolute_position(widget_rect)
                        
                        # Only scroll if the widget is not fully visible
                        if (widget_pos.top < visible_rect.top or 
                            widget_pos.bottom > visible_rect.bottom):
                            menu.get_scrollarea().scroll_to_rect(widget_rect)
                            
                        # Force update of select rect position
                        self.select_rect.change_target(menu.get_scrollarea().to_real_position(menu.get_selected_widget().get_rect()).centery)
                        self.has_drawn = False
                        
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
                    self.has_drawn = False
                        
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
            self.has_drawn = False
            self.mainmenu.get_current().enable()
        else:
            if self.mainmenu.get_current().is_enabled():
                self.mainmenu.get_current().update(pygame.event.get())
                try:
                    return self.running, self.drawing_handler()
                except RuntimeError as e:
                    print("Tried to draw a disabled menu!", e)
                    
        return self.running, [pygame.Rect(0, 0, 320, 240),]
            
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
        
class SelectRect(pygame.Rect):
    def __init__(self, x, y, width, height, target=None):
        super().__init__(x, y, width, height)
        self.target = target
        self.current_position = self.centery
        self.timer = 0
        self.duration = 0.2
        self.old_rect = self.copy()
    
    def change_target(self, new_target):
        print("target changed ", new_target)
        self.target = new_target
        self.current_position = self.centery
        self.timer = 0
    
    def update(self):
        self.timer += 1/60
        old_rect = self.copy()  # Store the old position before updating
        
        t = min(self.timer / self.duration, 1)
        if self.timer <= 1:
            self.y = int(self.easing(t, self.current_position, self.target) - self.height/2)
        else:
            self.y = int(self.target - self.height/2)  # Snap to final position
        
        # Return both the new (self) and old rectangle positions
        return self, old_rect

    def reset_position(self, menu):
        # Get the target position
        target_y = menu.buttons[0].get_rect().centery
        target_x = menu.get_widest_button().left
        
        # Set both current position and target to the same value (no animation)
        self.x = target_x
        self.y = target_y - self.height/2
        self.target = target_y
        self.current_position = target_y
        
        # Reset timer to skip animation
        self.timer = self.duration  # Set timer to equal or exceed duration
        
        # Update old_rect for rendering
        self.old_rect = self.copy()
        
    def easing(self, time, start, end):
        first_quart = start + (end - start) * 0.25
        third_quart = start + (end - start) * 0.75
        return start * (1-time)**3 + 3 * first_quart * time * (1 - time)**2 + 3 * third_quart * (1-time) * time**2 + end * time **3
        
class MenuWrapper (pygame_menu.Menu):
    def __init__(self, title, width, height, theme, **kwargs):
        super().__init__(title, width, height, theme=theme, **kwargs)
        self.buttons = []
        self.widest_button = None
        
    def add_button(self, title, action = None, **kwargs):
        self.buttons.append(self.add.button(title, action, **kwargs))
        
    def add_select_rect_callbacks(self, select_rect):
        self.widest_button = self.buttons[0]
        for b in self.buttons:
            if b.get_rect().width > self.widest_button.get_rect().width:
                self.widest_button = b
            b.set_onselect(lambda b=b: select_rect.change_target(b.get_rect().centery))
            
    def get_widest_button(self):
        return self.widest_button.get_rect()