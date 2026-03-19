import asyncio
import tkinter as tk
from PIL import Image, ImageTk
import numpy as np

import movixpy.io as mxi
from movixpy.viewer import SingleViewer

class MiniViewer:
    def __init__(self, width: int, height: int):
        self.root = tk.Tk()
        self.root.title("Viewer")

        self.canvas = tk.Canvas(self.root, width=width, height=height)
        self.canvas.pack()
        self._tk_img = None

    def update_from_path(self, path: str):
        img = Image.open(path)
        self._tk_img = ImageTk.PhotoImage(img)
        self.canvas.create_image(0, 0, anchor="nw", image=self._tk_img)
        self.root.update()

    def update_from_array(self, mat: np.ndarray):
        """Compatibile con l'output numpy di OpenCV (BGR -> RGB)."""
        img = Image.fromarray(mat[..., ::-1])  # BGR -> RGB
        self._tk_img = ImageTk.PhotoImage(img)
        self.canvas.create_image(0, 0, anchor="nw", image=self._tk_img)
        self.root.update()

    def start(self):
        self.root.mainloop()
        
async def load_video():
        video_file = mxi.VideoFile.from_video(r"C:/Easy4Pro/Video/01.mp4")
        video_file.extract_frames("")
    
viewer = MiniViewer(1920, 1080)
