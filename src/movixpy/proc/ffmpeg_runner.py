import imageio_ffmpeg
import subprocess   

class FFmpegRunner:     
    def __init__(self):
        self.ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
        print(self.ffmpeg_exe)

    def __create_ffmpeg_process(self, args: list[str]):
        return subprocess.Popen([self.ffmpeg_exe] + args)
    
    async def extract_frames_async(self, input_file: str, output_dir: str, on_complete: callable = None):
        process = self.__create_ffmpeg_process([
            "-i", rf"{input_file}", 
            rf"{output_dir}/%05d.jpg"
            ])
        process.wait()
        
        if on_complete:
            on_complete()
        
    async def create_video_from_frames_async(self, input_dir: str, output_file: str, on_complete=None):
        pass
    
    async def create_gif_from_frames_async(self, input_dir: str, output_file: str, on_complete=None):
        pass
    