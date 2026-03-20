import time
import asyncio
import numpy as np

from typing import Tuple
from typing import Callable

from .io import FramesDir
from .io import MotionFramesDir

from .proc import OpenCvRunner

################################################################################################################################################################
###
### SINGLE VIEWER CLASS
###
################################################################################################################################################################

class SingleViewer:        
    def __init__(
        self, 
        frames_dir: FramesDir, 
        fps: int,
        on_frame_update: Callable,
        ):
        self._on_frame_update = on_frame_update
        
        self._delay = 1 / fps
        self._frames_dir = frames_dir
        
        self._frame_idx = 0
        self._frame_start = 0
        self._frame_end = len(frames_dir)
        self._is_stop = True 
        
        self._play_event = asyncio.Event()
        
        self._task = None 
                
    async def _run(self):
        """
        Run loop
        """
        step = 1
        
        slow_c = 0
        speed_c = 0
        while not self._is_stop:
            
            self._frame_idx = 0
            while self._frame_idx < self._frame_end:
                if self._is_stop:
                    break
                
                await self._play_event.wait()
                
                proc_time = 0
                if self._on_frame_update is not None:
                    start = time.time()
                    self._on_frame_update(self._frame_idx, self._frames_dir[self._frame_idx])  
                    end = time.time()
                    
                    proc_time = end - start
                    
                remaining_time = self._delay * step - proc_time
                if remaining_time >= 0:
                    if remaining_time > self._delay:
                        speed_c += 1
                        slow_c = 0
                        
                        if speed_c >= 30:
                            step -= 1
                            speed_c = 0
                    
                    await asyncio.sleep(remaining_time)
                else:
                    speed_c = 0
                    slow_c += 1
                    
                    if slow_c > 5:
                        step += 1
                        slow_c = 0
                
                self._frame_idx += step
 
    def start(self, loop: asyncio.AbstractEventLoop = None):
        """
        Start the viewer loop (and play for the first time)
        """
        if self._task is None:
            self._is_stop = False
            
            if loop:
                asyncio.run_coroutine_threadsafe(self._run(), loop)
            else:
                self._task = asyncio.create_task(self._run())
                
            self.play()
                        
    def play(self):
        """
        Play the viewer loop 
        """
        self._play_event.set()
    
    def pause(self):
        """
        Pause the viewer loop
        """
        self._play_event.clear()
            
    def set_frame_idx(self, frame_idx: int):
        """
        Set new frame idx
        """
        if self._play_event.is_set():
            self.pause()
            
        if frame_idx in range(self._frame_start, self._frame_end):
            self._frame_idx = frame_idx
            self._on_frame_update(self._frame_idx, self._frames_dir[self._frame_idx])
            
        self.play()
            
    def set_frame_start(self, frame_start: int):
        """
        Set new frame start
        """
        if frame_start in range(self._frame_start, self._frame_end):
            self._frame_start = frame_start
    
    def set_frame_end(self, frame_end: int):
        """
        Set new frame end
        """
        if frame_end in  range(self._frame_start, self._frame_end):
            self._frame_end = frame_end
    
    def stop(self): 
        """
        Stop the viewer 
        """
        self._is_stop = True
        self._play_event.set()                       
        if self._task is not None:
            self._task.cancel()
        self._task = None
        
################################################################################################################################################################
###
### MULTI VIEWER CLASS
###
################################################################################################################################################################  
        
class MultiViewer:     
    def __init__(
        self, 
        motion_frames_dirs: list[MotionFramesDir],
        fps: int,
        canvas_width: int,
        canvas_height: int,
        background_color: Tuple[int, int, int],
        on_frame_update: Callable
        ):         
        self._on_frame_update = on_frame_update
        
        self._delay = 1 / fps
        self._motion_frames_dirs = motion_frames_dirs
        
        self._canvas_width = canvas_width
        self._canvas_height = canvas_height
        self._background_color = background_color
        
        self._frame_idx = 0
        self._frame_start = 0
        self._frame_end = max([len(m) for m in motion_frames_dirs]) # frame end = max frame count
        self._is_stop = True 
        
        self._play_event = asyncio.Event()
        
        self._task = None 
        
    def _composite_frames(self) -> np.ndarray:
        """
        Generate the composite frame
        """
        canvas_runner = OpenCvRunner.from_color(self._canvas_width, self._canvas_height, self._background_color)
        for mfd in self._motion_frames_dirs:
            mfd_runner = OpenCvRunner.from_path(mfd[self._frame_idx])
            
            key = mfd.get_frame_position(self._frame_idx)
            if key != None:
                mfd_runner.resize(key[3], key[4])
                mfd_runner.rotate(key[0], self._background_color)
                canvas_runner.paste(mfd_runner, rect = (int(key[1]), int(key[2]), key[3], key[4]))
        return canvas_runner.mat
                
    async def _run(self):
        """
        Run loop
        """
        step = 1
        
        slow_c = 0
        speed_c = 0
        while not self._is_stop:
            
            self._frame_idx = 0
            while self._frame_idx < self._frame_end:
                if self._is_stop:
                    break
                
                await self._play_event.wait()
                
                proc_time = 0
                if self._on_frame_update is not None:
                    start = time.time()
                    self._on_frame_update(self._frame_idx, self._composite_frames()) 
                    end = time.time()
                    
                    proc_time = end - start
                    
                remaining_time = self._delay * step - proc_time
                if remaining_time >= 0:
                    if remaining_time > self._delay:
                        speed_c += 1
                        slow_c = 0
                        
                        if speed_c >= 30:
                            step -= 1
                            speed_c = 0
                    
                    await asyncio.sleep(remaining_time)
                else:
                    speed_c = 0
                    slow_c += 1
                    
                    if slow_c > 5:
                        step += 1
                        slow_c = 0
                
                self._frame_idx += step
                
    def start(self, loop: asyncio.AbstractEventLoop = None):
        """
        Start the viewer loop (and play for the first time)
        """
        if self._task is None:
            self._is_stop = False
            
            if loop:
                asyncio.run_coroutine_threadsafe(self._run(), loop)
            else:
                self._task = asyncio.create_task(self._run())
                
            self.play()
                        
    def play(self):
        """
        Play the viewer loop 
        """
        self._play_event.set()
    
    def pause(self):
        """
        Pause the viewer loop 
        """
        self._play_event.clear()
            
    def set_frame_idx(self, frame_idx: int):
        """
        Set new frame idx
        """
        if self._play_event.is_set():
            self.pause()
            
        if frame_idx in range(self._frame_start, self._frame_end):
            self._frame_idx = frame_idx
            self._on_frame_update(self._frame_idx, self._composite_frames())
            
        self.play()
            
    def set_frame_start(self, frame_start: int):
        """
        Set new frame start
        """
        if frame_start in range(self._frame_start, self._frame_end):
            self._frame_start = frame_start
    
    def set_frame_end(self, frame_end: int):
        """
        Set new frame end
        """
        if frame_end in  range(self._frame_start, self._frame_end):
            self._frame_end = frame_end
    
    def stop(self): 
        """
        Stop the viewer 
        """
        self._is_stop = True
        self._play_event.set()                       
        if self._task is not None:
            self._task.cancel()
        self._task = None                            
