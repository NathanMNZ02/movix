from proc.ffmpeg_runner import FFmpegRunner

class SingleViewer:
    def __init__(self, video_path: str, on_frame_update: callable):
        self.on_frame_update = on_frame_update
        self._frames_dir = None
        self._frame_start = 0
        self._frame_end = 0
        self._is_playing = False  
        self._is_stop = True  
            
        ffmpeg_runner = FFmpegRunner()
        ffmpeg_runner.extract_frames(
            video_path, 
            "output_frames", 
            on_complete=self._on_frames_extracted)
                        
    def _on_frames_extracted(self):
        self.frame_start = 0
    
    def play(self):
        if not self._is_playing:
            self._is_playing = True
    
    def pause(self):
        if self._is_playing:
            self._is_playing = False
    
    def stop(self): 
        self._is_stop = True