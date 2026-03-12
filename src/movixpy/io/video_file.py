class VideoFile:
    def __init__(self, path):
        self.path = path
    
    def __get_more_info(self):
        self.fps = 30.0
        self.duration_sec = 10.0
        
    def extract_frames(self, output_dir, on_complete=None):
        pass
    
        