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
    """
    Represents a static image media file.

    Attributes:
        title (str): The name of the media object
        file (str): The path to the media file.
    """
    
    def open(self, c):
        """
        Uses opencv's imread function to open an image file before wrapping it in an image capture class, 
        to make it mimic an opencv VideoCapture object
        
        Args:
            c (pygame.time.Clock): The clock that controls the framerate of the media playback, irrelevant for static images
            
        Returns:
            ImageCapture: The image file wrapped in an ImageCapture
            pygame.time.Clock: The clock that was passed as an argument, reinitialized
        """
    
        try:
            c = pygame.time.Clock()
            frame = cv2.imread(self.file)
            cap = ImageCapture(frame)
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
    
class ImageCapture:
    """
    Wraps a OpenCV image read to allow it to mimic a VideoCapture for ease of playback
    
    Attributes:
        frame (np.array): the image being wrapped, stored as an array of BGR values
    """
    def __init__(self, frame):
        self.frame = frame

    def read(self):
        return True, self.frame

    def release(self):
        pass  # No actual resource to release