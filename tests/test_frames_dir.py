from movixpy.io.video_file import VideoFile
from movixpy.io.frames_dir import FramesDir

video_file = VideoFile(r"C:\Easy4Pro\Video\01.mp4")
frames_dir = FramesDir(r"C:\\Easy4Pro\\Video\\movix", video_file=video_file, on_created=lambda:
    print("Creato")
    )
print(frames_dir[0])
print(frames_dir.get_width())
