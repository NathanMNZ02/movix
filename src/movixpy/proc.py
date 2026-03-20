import cv2 
import numpy as np
import asyncio
import imageio_ffmpeg
import tempfile, os

from typing import Tuple

################################################################################################################################################################
###
### FFMPEG CLASS 
###
################################################################################################################################################################

class FFmpegRunner:     
    def __init__(self):
        self.ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()

    async def _run(self, args: list[str]) -> None:
        """
        Run ffmpeg process asynchronously
        """
        try:
            process = await asyncio.create_subprocess_exec(
                self.ffmpeg_exe, *args,
                stdout=asyncio.subprocess.DEVNULL,
                stderr=asyncio.subprocess.DEVNULL
            )
        except NotImplementedError: # fallback and run with subprocess (sync)
            import subprocess

            result = subprocess.run(
                [self.ffmpeg_exe, *args],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )

            if result.returncode != 0:
                raise RuntimeError(
                    f"FFmpeg failed (sync fallback)\n"
                    f"stderr: {result.stderr.decode(errors='ignore')}"
                )
                
            return
        
        _, stderr = await process.communicate()
        if process.returncode != 0:
            raise RuntimeError(
                f"FFmpeg failed with return code {process.returncode}\n"
                f"stderr: {stderr.decode(errors='ignore')}"
            )
        
    async def extract_frames(
        self, 
        input_path: str, 
        quality: int,
        output_dir: str, 
        ):
        """
        Extract frames from video async
        """
        if quality not in range(1, 32):
            raise ValueError("Quality should be in the range 1-31")
        
        await self._run([
            "-i", input_path, 
            "-q:v", "2",
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
        await self._run([
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

        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
            palette_path = tmp.name

        try:
            # Pass 1: generate palette
            await self._run([
                "-i", f"{input_dir}/%05d.jpg",
                "-vf", palette_filter,
                "-y", palette_path
            ])

            # Pass 2: encode gif using palette
            await self._run([
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
    
################################################################################################################################################################
###
### OPENCV CLASS 
###
################################################################################################################################################################

class OpenCvRunner:
    @staticmethod
    def read_video_metadata(input_path: str) -> dict:
        """
        Return video metadata
        """
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
        
    @classmethod
    def from_color(cls, width: int, height: int, color: Tuple[int, int, int]) -> "OpenCvRunner":
        """
        Create canvas with specific color
        """
        instance = cls.__new__(cls)
        instance.mat = np.full((height, width, 3), color, dtype=np.uint8)
        return instance
    
    @classmethod
    def from_path(cls, path: str) -> "OpenCvRunner":
        """
        Create matrix from image path
        """
        instance = cls.__new__(cls)
        instance.mat = cv2.imread(path)
        return instance
    
    def __init__(self):
        self.mat = None
        
    def resize(
        self, 
        width: int, 
        height: int
        ):
        """
        Change the image size.
        """
        self.mat = cv2.resize(self.mat, (width, height), interpolation=cv2.INTER_LINEAR)
        
    def rotate(
        self, 
        angle: int,
        background_color: Tuple[int, int, int]
    ) -> "OpenCvRunner":
        """
        Rotates the image while maintaining its original dimensions. Uncovered areas are filled with background_color.
        """
        h, w = self.mat.shape[:2]
        cx, cy = w // 2, h // 2

        M = cv2.getRotationMatrix2D((cx, cy), -angle, 1.0)
        self.mat = cv2.warpAffine(
            self.mat, M, (w, h),
            borderMode=cv2.BORDER_CONSTANT,
            borderValue=background_color
        )
        
    def paste(self, src: "OpenCvRunner", rect: Tuple[int, int, int, int]):
        """
        Paste src into the canvas at position rect(x, y, w, h).
        
        Raises:
            ValueError: if src is not the same size as rect.
        """
        x, y, rw, rh = rect

        if src.width() != rw or src.height() != rh:
            raise ValueError(f"The source image ({src.width()}x{src.height()}) does not match the rectangle ({rw}x{rh})")

        cw, ch = self.width(), self.height()
        if x >= cw or y >= ch or x + rw <= 0 or y + rh <= 0:
            return self

        src_x1 = max(0, -x)
        src_y1 = max(0, -y)
        src_x2 = min(rw, cw - x)
        src_y2 = min(rh, ch - y)

        dst_x1 = max(0, x)
        dst_y1 = max(0, y)
        dst_x2 = dst_x1 + (src_x2 - src_x1)
        dst_y2 = dst_y1 + (src_y2 - src_y1)

        self.mat[dst_y1:dst_y2, dst_x1:dst_x2] = src.mat[src_y1:src_y2, src_x1:src_x2]
        
    def width(self):
        """
        Return the image width
        """
        
        if self.mat is not None:
            return self.mat.shape[1]
        else:
            raise Exception("Mat is none")
    
    def height(self):
        """
        Return the image height
        """
        if self.mat is not None: 
            return self.mat.shape[0]
        else:
            raise Exception("Mat is none")