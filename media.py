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
        
class Video(Media):
    def open(self):
        try:
            cap = cv2.VideoCapture(self.file)
            img = cap.read()
            return img
        except Exception as e:
            cap.release()
            print("file not found")
            return img[0]
    
    
    

        
