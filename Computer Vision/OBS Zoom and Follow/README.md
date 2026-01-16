# OBS Zoom and Follow - Object Tracking System

A computer vision application that automatically tracks, zooms in on, and follows objects in video streams. This tool is perfect for creating dynamic video content where the camera automatically follows a subject.

## Features

- **Real-time Object Tracking**: Uses CSRT (Discriminative Correlation Filter with Channel and Spatial Reliability) tracking algorithm for robust object tracking
- **Automatic Zoom**: Dynamically zooms in on the tracked object to keep it prominently in frame
- **Smooth Follow**: Smoothly pans the camera to keep the tracked object centered
- **Interactive Selection**: Easy-to-use interface for selecting objects to track
- **Configurable Parameters**: Adjust zoom level and smoothing for different use cases
- **Multiple Input Sources**: Works with webcams, video files, and other video sources

## Installation

1. Install the required dependencies:

```bash
pip install -r requirements.txt
```

Or manually install:

```bash
pip install opencv-contrib-python>=4.5.0 numpy>=1.19.0
```

## Usage

### Basic Usage

Run with default webcam:

```bash
python obs_zoom_follow.py
```

### Advanced Usage

Specify video source:

```bash
# Use specific webcam (index 0, 1, 2, ...)
python obs_zoom_follow.py --source 0

# Use video file
python obs_zoom_follow.py --source path/to/video.mp4
```

Adjust zoom factor (1.0 to 5.0):

```bash
python obs_zoom_follow.py --zoom 3.0
```

Adjust camera smoothing (0.0 to 1.0, lower = smoother):

```bash
python obs_zoom_follow.py --smoothing 0.05
```

Combine options:

```bash
python obs_zoom_follow.py --source video.mp4 --zoom 2.5 --smoothing 0.15
```

## How It Works

1. **Object Selection**: When the application starts, it displays the first frame and allows you to select an object by drawing a bounding box around it.

2. **Tracking**: The CSRT tracker continuously tracks the selected object across frames, maintaining its position even with partial occlusions and appearance changes.

3. **Zoom and Follow**: 
   - The application calculates the center of the tracked object
   - It extracts a region of interest (ROI) around this center
   - The ROI is scaled up to create the zoom effect
   - Smooth interpolation prevents jerky camera movements

4. **Display**: The processed frame with zoom and follow effects is displayed in real-time with tracking information overlay.

## Controls

- **Initial Selection**: Draw a box around the object you want to track when prompted
- **'r' key**: Reselect object (pause tracking and choose a new object)
- **'q' key**: Quit the application

## Parameters

### --source
- **Type**: String
- **Default**: "0" (default webcam)
- **Description**: Video source - can be a camera index (0, 1, 2, ...) or path to a video file

### --zoom
- **Type**: Float
- **Default**: 2.0
- **Range**: 1.0 to 5.0
- **Description**: Zoom magnification factor. 1.0 means no zoom, 2.0 means 2x zoom, etc.

### --smoothing
- **Type**: Float
- **Default**: 0.1
- **Range**: 0.0 to 1.0
- **Description**: Camera movement smoothing factor. Lower values create smoother but slower camera movement. Higher values make the camera more responsive but potentially jerkier.

## Technical Details

### Tracking Algorithm

The application uses OpenCV's CSRT (Discriminative Correlation Filter with Channel and Spatial Reliability) tracker, which:
- Provides robust tracking with spatial reliability maps
- Handles partial occlusions well
- Works effectively with appearance changes
- Balances accuracy and speed for real-time applications

### Zoom Implementation

The zoom effect is achieved by:
1. Calculating a region of interest (ROI) centered on the tracked object
2. The ROI size is inversely proportional to the zoom factor
3. Resizing the ROI back to the original frame dimensions
4. This creates the appearance of zooming in on the object

### Follow Implementation

The follow (pan) effect uses:
- Exponential smoothing to prevent jerky movements
- Adaptive centering to keep the object in frame
- Boundary clamping to prevent going outside the original frame

## Use Cases

- **Live Streaming**: Automatically follow a presenter or performer
- **Sports Recording**: Track athletes during gameplay
- **Tutorial Videos**: Keep tools or demonstrations in focus
- **Security**: Monitor and follow moving objects of interest
- **Content Creation**: Create dynamic video content without manual camera operation

## Limitations

- Tracking may fail with extreme occlusions or if the object leaves the frame
- Performance depends on the complexity of the scene and object appearance
- Works best with objects that have distinctive features
- Very fast-moving objects may be challenging to track

## Tips for Best Results

1. **Good Lighting**: Ensure adequate lighting for better tracking accuracy
2. **Distinctive Objects**: Objects with clear edges and unique features track better
3. **Stable Background**: Cluttered or moving backgrounds can affect tracking
4. **Appropriate Zoom**: Start with moderate zoom (2.0-3.0) and adjust as needed
5. **Smoothing Adjustment**: Use lower smoothing values (0.05-0.1) for fast-moving objects, higher values (0.2-0.3) for slower, smoother movements

## Troubleshooting

**Problem**: Tracking is lost frequently
- **Solution**: Try selecting a more distinctive part of the object, or reduce the zoom factor

**Problem**: Camera movement is too jerky
- **Solution**: Decrease the smoothing parameter (e.g., from 0.1 to 0.05)

**Problem**: Camera is too slow to follow the object
- **Solution**: Increase the smoothing parameter (e.g., from 0.1 to 0.2)

**Problem**: Application won't start or crashes
- **Solution**: Ensure opencv-contrib-python is installed (not just opencv-python) as it includes the tracking algorithms

## Future Enhancements

Potential improvements for future versions:
- Multiple object tracking
- Face detection and automatic tracking
- Recording functionality with zoom and follow applied
- Adjustable zoom and smoothing during runtime
- Integration with streaming software like OBS Studio
- GPU acceleration for better performance

## License

This project is part of the Artificial Intelligence Projects repository and follows the same license.

## Contributing

Contributions are welcome! Feel free to submit issues or pull requests to improve the functionality.

## Author

Created as part of the Artificial Intelligence Projects collection.
