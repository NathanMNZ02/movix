from ..proc.opencv_runner import OpenCvRunner
from ..proc.ffmpeg_runner import FFmpegRunner

class VideoFile:
    @classmethod
    def from_video(
        cls,
        path: str
        ):
        """
        Create object from video path

        Args:
            path (str): video path
        """
        return cls(path)
    
    @classmethod
    async def from_frames_dir(
        cls, 
        path: str,
        fps: int,
        crf: int,
        frames_dir
    ):
        """
        Create object from frames dir converting the frames into a video.
        
        Args:
            path (str): video path
            frames_dir (FramesDir): frames dir instance
        """
        from .frames_dir import FramesDir
        
        if not isinstance(frames_dir, FramesDir):
            raise TypeError(f"Expected FramesDir, got {type(frames_dir).__name__}")
        
        await frames_dir.create_video(path, fps, crf)
        
        return cls(path)
                  
    def __init__(self, path):
        self.path = path
        
        metadata = OpenCvRunner.read_video_metadata(path)
        self.width = metadata["width"]
        self.height = metadata["height"]
        self.fps = metadata["fps"]
        self.frame_count = metadata["frame_count"]
        self.duration_sec = metadata["duration"]
        
    async def extract_frames(self, output_path):
        await FFmpegRunner().extract_frames(
            self.path,
            output_path
        )
    
        