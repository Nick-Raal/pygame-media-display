import pygame
import cv2
from pathlib import Path

class Media:
    """
    Represents a base media file.

    Attributes:
        title (str): The name of the media object
        file (str): The path to the media file.
    """
    
    def __init__ (self, file):
        self.file = file
        self.title = Path(file).stem
        
    def open(self):
        print("default open")
        return True
        
    def get_title(self):
        return self.title
    
class Image(Media):
    def open(self, c):
        try:
            c = pygame.time.Clock()
            cap = cv2.imread(self.file)
            return cap, c
        except Exception as e:
            cap.release()
            print("file not found")
            return None
        
class Video(Media):
    def open(self, c):
        
        try:
            c = pygame.time.Clock()
            cap = cv2.VideoCapture(self.file)
            return cap, c
        except Exception as e:
            cap.release()
            print("file not found")
            return None
    
    
    

        
