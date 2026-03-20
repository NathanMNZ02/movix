# Movix

Movix is a Python library for advanced video, GIF, and image handling.  
It provides tools to convert videos into frames, create videos/GIFs from frames, and display media content in a simple and programmable way.

---

## Main Features

### 1. IO

Manages input/output for videos, GIFs, and frames:

- **`VideoFile`** – represents a video file.  
- **`GifFile`** – represents a GIF file.  
- **`FramesDir`** – represents a directory of frames.

**Automatic operations**:

- Convert a `VideoFile` into a `FramesDir`.  
- Create a `VideoFile` from a `FramesDir`.  
- Create a `GifFile` from a `FramesDir`.  
- Convert a `GifFile` into a `FramesDir`.  

> This makes it easy to transform and manipulate video content without dealing directly with FFmpeg or OpenCV.

---

### 2. proc

Provides abstractions for core libraries:

- **`FFmpegRunner`** – simple wrapper for FFmpeg.  
- **`OpenCvRunner`** – simple wrapper for OpenCV.  

> Both classes make it easier to use these libraries even if you are not familiar with them.

---

### 3. viewer

Handles video and image visualization:

- **`SingleViewer`** – displays a single video frame by frame, passing the current frame path via a callback, and automatically plays at N fps (default uses the original video fps).  
- **`MultiViewer`** – more advanced viewer that allows displaying multiple videos/images simultaneously with support for layer-based editing.

---

## Installation

During development, install the library in editable mode:

```bash
pip install -e .
```

Required dependencies:

- Python >= 3.9

- opencv-python-headless

- imageio-ffmpeg

---

## Usage Examples

Usage examples are available as Jupyter notebooks in the `tests/` folder. Each notebook demonstrates a specific feature of the library and can be run independently.

---

## Advanced Features

- Cross-platform support (Windows/Linux/macOS)

- Synchronous and asynchronous API for frame extraction and video creation

- Intuitive handling of videos, GIFs, and images

- Supports multimedial editing via MultiViewer
