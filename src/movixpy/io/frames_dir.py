import os
from typing import Callable

from ..proc.opencv_runner import OpenCvRunner
from ..proc.ffmpeg_runner import FFmpegRunner

class FramesDir:
    @classmethod
    def from_dir(
        cls, 
        path: str
        ):
        """
        Create object from frames directory path.

        Args:
            path (str): path of frames dir
        """
        if not os.path.isdir(path):
            raise ValueError("Invalid directory")

        valid_ext = ('.jpg', '.jpeg', '.png', '.bmp', '.tiff')

        frames = sorted(
            f for f in os.listdir(path)
            if os.path.splitext(f)[1].lower() in valid_ext
        )

        if not frames:
            raise ValueError("No valid frames found")

        return cls(path, frames)
    
    @classmethod
    async def from_video(
        cls,
        path: str,
        video_file
        ):
        """
        Create object from video extracting frames from it

        Args:
            path (str): path of frames dir (output path)
            video_file (VideoFile): video file obj
        """
        from .video_file import VideoFile
        
        if not isinstance(video_file, VideoFile):
            raise TypeError(f"Expected VideoFile, got {type(video_file).__name__}")
        
        os.makedirs(path, exist_ok=True)

        await video_file.extract_frames(output_path=path)

        return cls.from_dir(path)   
         
    def __init__(self, path: str, frames: list[str]):
        self.path = path
        self.frames = frames
        self.width = self.__get_width()
        self.height = self.__get_height()  
            
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
        if idx >= len(self.frames):
            raise IndexError("Frame index out of range")
        return os.path.join(self.path, self.frames[idx])
    
    def __get_width(self) -> int:
        """
        Return the width of the first frames in the directory 

        Returns:
            int: width
        """
        if not self.frames:
            raise ValueError("No frames available")
        return OpenCvRunner(self.__getitem__(0)).width()
    
    def __get_height(self) -> int:
        """
        Return the height of the first frames in the directory

        Returns:
            int: height
        """
        if not self.frames:
            raise ValueError("No frames available")
        return OpenCvRunner(self.__getitem__(0)).height()
     
    async def create_video(
        self, 
        output_path: str, 
        fps: int,
        crf: int,
        ):
        """
        Create video from frames directory
        """        
        ext = os.path.splitext(output_path)[1].lower()
        if ext not in ['.mp4', '.mov', '.avi']:
            raise ValueError(f"Video extension {ext} not allowed")
        
        await FFmpegRunner().create_video_from_frames_async(self.path, output_path, fps, crf)
    
    async def create_gif(
        self,
        output_path: str,
    ):
        """
        Create gif from frames directory
        """
        ext = os.path.splitext(output_path)[1].lower()
        if ext != '.gif':
            raise ValueError("Gif extension not allowed")
        
        await FFmpegRunner().create_gif_from_frames_async(self.path, output_path)