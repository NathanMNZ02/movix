import asyncio
from movixpy.io import VideoFile
from movixpy.viewer import SingleViewer

def on_frame_update(idx: int, path: str):
    print(f"{idx} - {path}")

async def main():
    video_file = VideoFile.from_video(r"C:/Easy4Pro/Video/01.mp4")
    video_file.extract_frames()
    viewer = await SingleViewer(video_file, on_frame_update)
    
    viewer.start()
    viewer.play()
    
    await asyncio.sleep(20)  # <-- deve essere await
    
    viewer.stop()

asyncio.run(main())