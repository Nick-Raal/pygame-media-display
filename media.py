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
        
    def get_title(self):
        return self.title
        
class Video(Media):
    def open(self):
        try:
            cap = cv2.VideoCapture(self.file)
            img = cap.read()
        except Exception as e:
            cap.release()
            print("file not found")
            
        shape = img.shape[1::-1]

        return pygame.image.frombuffer(img.tobytes(), shape, "BGR"), (0, 0)
    

        
