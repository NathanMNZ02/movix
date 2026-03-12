import os
import asyncio
from .video_file import VideoFile
from ..proc.opencv_runner import OpenCvRunner
from ..proc.ffmpeg_runner import FFmpegRunner

class FramesDir:
    def __init__(self, path: str, video_file: VideoFile = None, on_created=None):        
        self.path = path
        
        if os.path.exists(path) and not os.path.isdir(path):
            raise ValueError(f"FramesDir path '{path}' is not a directory.")
        
        if not os.path.exists(path) and video_file == None:
            raise ValueError(f"FramesDir path '{path}' does not exist and no video file provided to create frames.")
        
        if video_file != None:
            if not os.path.exists(path):
                os.makedirs(path)

            def on_complete():
                self.frames = sorted(os.listdir(path))
                if on_created:
                    on_created()
                    
            ffmpeg_runner = FFmpegRunner()
            asyncio.run(ffmpeg_runner.extract_frames(
                video_file.path, 
                path, 
                on_complete=on_complete 
            ))
        else:
            supported_images = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']
            
            self.frames = sorted(os.listdir(path))
            if not self.frames:
                raise ValueError(f"FramesDir path '{path}' is empty.")
            
            if not any(os.path.splitext(f)[1].lower() in supported_images for f in self.frames):
                raise ValueError(f"FramesDir path '{path}' does not contain any supported image files.")
            
    def __len__(self) -> int:
        """
        Returns the number of frames in the directory
        
        Returns:
            int: frame count
        """
        return len(self.frames)
    
    def __getitem__(self, idx: int):
        """
        Return the complete frame path of frame at idx
        """
        return os.path.join(self.path, self.frames[idx])
            
    def create_video(self, output_file: str, on_created = None):
        """
        Create video from frames directory
        """
        return FFmpegRunner().create_video_from_frames(self.path, output_file, on_created)
            
    def get_width(self) -> int:
        """
        Return the width of the first frames in the directory 

        Returns:
            int: width
        """
        return OpenCvRunner(self.__getitem__(0)).width()
    
    def get_height(self) -> int:
        """
        Return the height of the first frames in the directory

        Returns:
            int: height
        """
        return OpenCvRunner(self.__getitem__(0)).height()
    