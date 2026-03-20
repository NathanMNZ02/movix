import os
import shutil

from typing import Tuple

from .proc import OpenCvRunner
from .proc import FFmpegRunner

################################################################################################################################################################
###
### FRAMES DIR CLASS
###
################################################################################################################################################################

class FramesDir:
    @classmethod
    def from_frames_dir(
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
    def from_image(
        cls, 
        path: str,
        image_path: str
    ):
        """
        Create object from image copy image in the directory

        Args:
            path (str): _description_
            image_path (str): _description_

        Raises:
            ValueError: _description_
        """        
        valid_ext = ('.jpg', '.jpeg', '.png', '.bmp', '.tiff')
        if not os.path.isfile(image_path) or os.path.splitext(image_path)[1].lower() not in valid_ext:
            raise ValueError(f"The path {image_path} does not refer to an image with extension {valid_ext}")

        os.makedirs(path, exist_ok=True)

        dest = os.path.join(path, os.path.basename(image_path))
        shutil.copy2(image_path, dest)
                
        return cls.from_frames_dir(path)   

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
        if not isinstance(video_file, VideoFile):
            raise TypeError(f"Expected VideoFile, got {type(video_file).__name__}")
        
        os.makedirs(path, exist_ok=True)

        await video_file.extract_frames(output_path=path)
        return cls.from_frames_dir(path)   
         
    def __init__(self, path: str, frames: list[str]):
        self.path = path
        self.frames = frames
        self.width = self._get_width()
        self.height = self._get_height()  
            
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
    
    def _get_width(self) -> int:
        """
        Return the width of the first frames in the directory 

        Returns:
            int: width
        """
        if not self.frames:
            raise ValueError("No frames available")
        return OpenCvRunner.from_path(self.__getitem__(0)).width()
    
    def _get_height(self) -> int:
        """
        Return the height of the first frames in the directory

        Returns:
            int: height
        """
        if not self.frames:
            raise ValueError("No frames available")
        return OpenCvRunner.from_path(self.__getitem__(0)).height()
     
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
        
    def loop(
        self, 
        target_frames: int,
        ):
        """
        Extends the sequence to target_frames by looping from the beginning.
        Example: [0,1,2,3] → [0,1,2,3,0,1,2,3,0,1...]
        """
        if target_frames <= len(self.frames):
            raise ValueError(f"target_frames must be greater than current frame count ({len(self.frames)})")
        
        frames_to_add = target_frames - len(self.frames)
        for i in range(frames_to_add):
            src = self[i % len(self.frames)]
            dest_name = f"{len(self.frames) + i:05d}{os.path.splitext(src)[1]}"
            dest = os.path.join(self.path, dest_name)
            shutil.copy2(src, dest)
            self.frames.append(dest_name)
            
    def freeze(
        self, 
        target_frames: int,
        ):
        """
        Extends the sequence to target_frames by repeating the last frame.
        Example: [0,1,2,3] → [0,1,2,3,3,3,3,3,3...]
        """
        if target_frames <= len(self.frames):
            raise ValueError(f"target_frames must be greater than current frame count ({len(self.frames)})")
        
        last_frame = self[len(self.frames) - 1]
        ext = os.path.splitext(last_frame)[1]
        frames_to_add = target_frames - len(self.frames)
        for i in range(frames_to_add):
            dest_name = f"{len(self.frames) + i:05d}{ext}"
            dest = os.path.join(self.path, dest_name)
            shutil.copy2(last_frame, dest)
            self.frames.append(dest_name)
            
    def bounce(
        self,
        target_frames: int,
        ):
        """
        Extends the sequence to target_frames with a ping-pong effect.
        Example: [0,1,2,3] → [0,1,2,3,2,1,0,1,2,3...]
        """
        if target_frames <= len(self.frames):
            raise ValueError(f"target_frames must be greater than current frame count ({len(self.frames)})")

        frames_to_add = target_frames - len(self.frames)
        bounce = list(range(len(self.frames))) + list(range(len(self.frames) - 2, 0, -1))
        for i in range(frames_to_add):
            src = self[bounce[i % len(bounce)]]
            ext = os.path.splitext(src)[1]
            dest_name = f"{len(self.frames) + i:05d}{ext}"
            dest = os.path.join(self.path, dest_name)
            shutil.copy2(src, dest)
            self.frames.append(dest_name)
    
                
################################################################################################################################################################
###
### VIDEO FILE CLASS 
###
################################################################################################################################################################

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
        """
        Extact frames from video
        """
        if not os.path.isdir(output_path):
            os.mkdir(output_path)
            
        await FFmpegRunner().extract_frames(
            self.path,
            2,
            output_path
        )
    
################################################################################################################################################################
###
### KEY POSITION DATACLASS 
###
################################################################################################################################################################

class KeyPosition:
    """
    Position of a media within the canvas for specific frames
    """
    def __init__(self, frame_idx: int, position: Tuple[float, float, int, int], angle: int):
        self.frame_idx = frame_idx
        self.position = position
        self.angle = angle
        
################################################################################################################################################################
###
### MOTION FRAMES DIR CLASS
###
################################################################################################################################################################

class MotionFramesDir(FramesDir):
    """
    A FramesDir with an associated MediaMovement, describing how
    the frames should be positioned and animated on a canvas.
    """

    @classmethod
    def from_frames_dir(cls, path: str, key_positions: list[KeyPosition]) -> "MotionFramesDir":
        frames_dir_instance = FramesDir.from_frames_dir(path, path)
        return cls(
            path=frames_dir_instance.path,
            frames=frames_dir_instance.frames,
            key_positions=key_positions
        )

    @classmethod
    def from_image(cls, path: str, image_path: str, key_positions: list[KeyPosition]) -> "MotionFramesDir":
        frames_dir_instance = FramesDir.from_image(path, image_path)
        return cls(
            path=frames_dir_instance.path,
            frames=frames_dir_instance.frames,
            key_positions=key_positions
        )

    @classmethod
    async def from_video(cls, path: str, video_file, key_positions: list[KeyPosition]) -> "MotionFramesDir":
        frames_dir_instance = await FramesDir.from_video(path, video_file)
        return cls(
            path=frames_dir_instance.path,
            frames=frames_dir_instance.frames,
            key_positions=key_positions
        )

    def __init__(self, path: str, frames: list[str], key_positions: list[KeyPosition]):
        super().__init__(path, frames)
        self._validate_key_positions(key_positions)
        self.key_positions = sorted(key_positions, key=lambda k: k.frame_idx)
        
    def _validate_key_positions(
        self,
        key_positions: list[KeyPosition]
        ):
        """
        Check if the input list of key position is correct for the frames dir
        """
        total = self.__len__()
        for kp in key_positions:
            if not (0 <= kp.frame_idx < total):
                raise ValueError(f"KeyPosition.frame_idx={kp.frame_idx} out of range 0..{total - 1}")
            
    def add(
        self, 
        key_position: KeyPosition
        ):
        """
        Add new key position
        """
        if not (0 <= key_position.frame_idx < self.__len__()):
            raise ValueError(f"frame_idx={key_position.frame_idx} out of range 0..{self.__len__() - 1}")
        
        self.key_positions = [k for k in self.key_positions if k.frame_idx not in range(key_position.frame_idx - 10, key_position.frame_idx + 10)]
        self.key_positions.append(key_position)
        self.key_positions.sort(key=lambda k: k.frame_idx)
    
    def remove(self, frame_idx: int):
        """
        Rimuove la KeyPosition con il frame_idx indicato.
        Raises:
            ValueError: se non esiste nessuna KeyPosition con quel frame_idx
            ValueError: se rimuovendo il keyframe ne rimarrebbe meno di 2 
                        rendendo l'interpolazione impossibile (opzionale, vedi sotto)
        """
        match = next((k for k in self.key_positions if k.frame_idx == frame_idx), None)
        if match is None:
            raise ValueError(f"Nessuna KeyPosition trovata con frame_idx={frame_idx}")

        self.key_positions.remove(match)
        
    def get_frame_position(
        self,
        frame_idx: int
        ) -> Tuple[int, float, float, int, int] | None:
        """
        Interpolates (angle, x, y, w, h) for frame_idx between the two
        nearest MediaPosition keyframes. Returns None if no keyframes defined.
        """
        if not self.key_positions:
            return None

        keyframes = sorted(self.key_positions, key=lambda k: k.frame_idx)

        if frame_idx <= keyframes[0].frame_idx:
            k = keyframes[0]
            return (k.angle, k.position[0], k.position[1], k.position[2], k.position[3])

        if frame_idx >= keyframes[-1].frame_idx:
            k = keyframes[-1]
            return (k.angle, k.position[0], k.position[1], k.position[2], k.position[3])

        prev = next(k for k in reversed(keyframes) if k.frame_idx <= frame_idx)
        next_ = next(k for k in keyframes if k.frame_idx > frame_idx)

        span = next_.frame_idx - prev.frame_idx
        t = (frame_idx - prev.frame_idx) / span

        a = int(prev.angle + (next_.angle - prev.angle) * t)
        x = prev.position[0] + (next_.position[0] - prev.position[0]) * t
        y = prev.position[1] + (next_.position[1] - prev.position[1]) * t
        w = int(prev.position[2] + (next_.position[2] - prev.position[2]) * t)
        h = int(prev.position[3] + (next_.position[3] - prev.position[3]) * t)

        return (a, x, y, w, h)