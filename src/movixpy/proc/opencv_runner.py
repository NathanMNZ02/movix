import cv2 

class OpenCvRunner:
    def __init__(self, filename: str):
        self.mat = cv2.imread(filename)
        
    def resize():
        pass

    def crop():
        pass
    
    def width(self):
        return self.mat.shape[1]
    
    def height(self):
        return self.mat.shape[0]