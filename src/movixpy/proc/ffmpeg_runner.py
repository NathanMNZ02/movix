import asyncio
import imageio_ffmpeg
import subprocess  
from typing import Callable 

class FFmpegRunner:     
    def __init__(self):
        self.ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()

    async def __run(self, args: list[str]) -> None:
        """
        Run ffmpeg process asynchronously
        """
        process = await asyncio.create_subprocess_exec(
            self.ffmpeg_exe, *args,
            stdout=asyncio.subprocess.DEVNULL,
            stderr=asyncio.subprocess.DEVNULL
        )
        returncode = await process.wait()
        if returncode != 0:
            raise RuntimeError(f"FFmpeg failed with return code {returncode}")
        
    async def extract_frames(
        self, 
        input_path: str, 
        output_dir: str, 
        ):
        """
        Extract frames from video async
        """
        await self.__run([
            "-i", input_path, 
            f"{output_dir}/%05d.jpg"
        ])
        
    async def create_video_from_frames_async(
        self, 
        input_dir: str, 
        output_file: str,
        fps: int = 30,
        crf: int = 23,
        ):
        """
        Create video from frames async.

        Args:
            input_dir (str): directory containing frames (e.g. 00001.jpg ...)
            output_file (str): output video path (.mp4, .mov, .avi)
            fps (int): frames per second of the output video
            crf (int): constant rate factor 0-51, lower = better quality.
                       Ignored if video_bitrate takes priority (codec-dependent).
            on_created (Callable | None): optional callback invoked after creation
        """
        await self.__run([
            "-framerate", str(fps),
            "-i", f"{input_dir}/%05d.jpg",
            "-c:v", "libx264",
            "-crf", str(crf),
            "-pix_fmt", "yuv420p",  
            "-y",                    # overwrite output without asking
            output_file
        ])
    
    async def create_gif_from_frames_async(
        self, 
        input_dir: str,
        output_file: str,
        fps: int = 15,
        width: int = -1,
        ):
        """
        Create gif from frames async.

        Args:
            input_dir (str): directory containing frames
            output_file (str): output gif path
            fps (int): frames per second of the gif. Lower = smaller file.
            width (int): output width in pixels. -1 keeps original width.
                         Height is scaled automatically to preserve aspect ratio.
            on_created (Callable | None): optional callback invoked after creation
        """
        palette_filter = (
            f"fps={fps},scale={width}:-1:flags=lanczos,palettegen"
        )
        frames_filter = (
            f"fps={fps},scale={width}:-1:flags=lanczos"
        )

        import tempfile, os
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
            palette_path = tmp.name

        try:
            # Pass 1: generate palette
            await self.__run([
                "-i", f"{input_dir}/%05d.jpg",
                "-vf", palette_filter,
                "-y", palette_path
            ])

            # Pass 2: encode gif using palette
            await self.__run([
                "-i", f"{input_dir}/%05d.jpg",
                "-i", palette_path,
                "-lavfi", f"{frames_filter}[x];[x][1:v]paletteuse",
                "-y", output_file
            ])
        finally:
            os.remove(palette_path)
    
    async def change_file_size_async(
        self, 
        input_file: str,
        width: int,
        height: int,
        aspect_ratio: bool,
    ):
        """
        Modify file size and maintain aspect ratio if aspect_ratio == true
        """
        pass