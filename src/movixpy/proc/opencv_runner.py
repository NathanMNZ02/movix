import cv2 

class OpenCvRunner:
    @staticmethod
    def read_video_metadata(input_path: str) -> dict:
        cap = cv2.VideoCapture(input_path)

        if not cap.isOpened():
            raise ValueError(f"Cannot open video file: {input_path}")

        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = (
            frame_count / fps
            if fps and fps > 0
            else 0
        )

        cap.release()

        return {
            "width": width,
            "height": height,
            "fps": fps,
            "frame_count": frame_count,
            "duration": duration
        }
        
    def __init__(self, filename: str):
        self.mat = cv2.imread(filename)
        
    def resize(
        self,
        width: int,
        height: int,
        aspect_ratio: bool
    ):
        pass

    def crop(
        self, 
        x: float,
        y: float,
        width: float,
        height: float,
    ):
        pass
    
    def width(self):
        if self.mat is not None:
            return self.mat.shape[1]
        else:
            raise Exception("Mat is none")
    
    def height(self):
        if self.mat is not None: 
            return self.mat.shape[0]
        else:
            raise Exception("Mat is none")