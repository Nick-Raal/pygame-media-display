import pygame
import cv2

class Media:
    """
    Represents a base media file.

    Attributes:
        file (str): The path to the media file.
    """
    
    def __init__ (self, file):
        self.file = file
        
    def open():
        print("default open")
        
class Video(Media):
    def open():
        try:
            cap = cv2.VideoCapture(self.file)
            img = cap.read()
        except Exception as e:
            cap.release()
            print("file not found")
            
        shape = img.shape[1::-1]

        return pygame.image.frombuffer(img.tobytes(), shape, "BGR"), (0, 0)
    

        
