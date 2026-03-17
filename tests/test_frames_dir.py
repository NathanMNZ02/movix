import asyncio
from movixpy.io.video_file import VideoFile
from movixpy.io.frames_dir import FramesDir

video_file = VideoFile.from_video(r"/Users/nathanmonzani/Downloads/videoplayback.mp4")
frames_dir = asyncio.run(FramesDir.from_video(r"/Users/nathanmonzani/Downloads/test", video_file=video_file))
new_video_file = asyncio.run(VideoFile.from_frames_dir(
    r"/Users/nathanmonzani/Downloads/new_videoplayback.mp4",
    fps=video_file.fps,
    crf=30,
    frames_dir=frames_dir
))
