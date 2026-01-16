#!/usr/bin/env python3
"""
Test script for OBS Zoom and Follow functionality.
This creates a synthetic video with a moving object to test tracking.
"""

import cv2
import numpy as np
import os
import sys
import tempfile


def create_test_video(output_path, duration=10, fps=30):
    """
    Create a test video with a moving colored ball.
    
    Args:
        output_path: Path to save the test video
        duration: Duration of video in seconds
        fps: Frames per second
    """
    width, height = 640, 480
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
    
    total_frames = duration * fps
    ball_radius = 30
    
    print(f"Creating test video: {output_path}")
    print(f"Duration: {duration}s, FPS: {fps}, Total frames: {total_frames}")
    
    for frame_num in range(total_frames):
        # Create background
        frame = np.ones((height, width, 3), dtype=np.uint8) * 50
        
        # Add some random noise/texture to background
        noise = np.random.randint(0, 30, (height, width, 3), dtype=np.uint8)
        frame = cv2.add(frame, noise)
        
        # Calculate ball position (moving in a circular pattern)
        t = frame_num / total_frames * 4 * np.pi  # 2 full circles
        center_x = int(width / 2 + 150 * np.cos(t))
        center_y = int(height / 2 + 100 * np.sin(t))
        
        # Draw the moving ball
        cv2.circle(frame, (center_x, center_y), ball_radius, (0, 255, 0), -1)
        
        # Add frame number for reference
        cv2.putText(frame, f"Frame: {frame_num}", (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        out.write(frame)
    
    out.release()
    print(f"Test video created successfully: {output_path}")
    return output_path


def test_tracker_basic():
    """Test basic tracker functionality."""
    print("\nTest 1: Basic Tracker Initialization")
    print("=" * 50)
    
    # Import the tracker
    from obs_zoom_follow import ObjectTracker
    
    # Test initialization
    tracker = ObjectTracker(zoom_factor=2.0, smoothing=0.1)
    assert tracker.zoom_factor == 2.0, "Zoom factor not set correctly"
    assert tracker.smoothing == 0.1, "Smoothing not set correctly"
    assert not tracker.tracking_active, "Tracker should not be active initially"
    print("✓ Tracker initialized correctly")
    
    # Test zoom factor clamping
    tracker_min = ObjectTracker(zoom_factor=0.5, smoothing=0.1)
    assert tracker_min.zoom_factor == 1.0, "Zoom factor should be clamped to minimum 1.0"
    print("✓ Zoom factor minimum clamping works")
    
    tracker_max = ObjectTracker(zoom_factor=10.0, smoothing=0.1)
    assert tracker_max.zoom_factor == 5.0, "Zoom factor should be clamped to maximum 5.0"
    print("✓ Zoom factor maximum clamping works")
    
    # Test smoothing clamping
    tracker_smooth_min = ObjectTracker(zoom_factor=2.0, smoothing=-0.5)
    assert tracker_smooth_min.smoothing == 0.0, "Smoothing should be clamped to minimum 0.0"
    print("✓ Smoothing minimum clamping works")
    
    tracker_smooth_max = ObjectTracker(zoom_factor=2.0, smoothing=2.0)
    assert tracker_smooth_max.smoothing == 1.0, "Smoothing should be clamped to maximum 1.0"
    print("✓ Smoothing maximum clamping works")
    
    print("\n✓ All basic tracker tests passed!")


def test_zoom_follow_with_video():
    """Test tracking with a synthetic video."""
    print("\nTest 2: Tracking with Synthetic Video")
    print("=" * 50)
    
    # Create test video in temp directory
    test_video_path = os.path.join(tempfile.gettempdir(), "test_tracking_video.mp4")
    create_test_video(test_video_path, duration=5, fps=30)
    
    # Import the tracker
    from obs_zoom_follow import ObjectTracker
    
    # Open the test video
    cap = cv2.VideoCapture(test_video_path)
    assert cap.isOpened(), "Failed to open test video"
    print("✓ Test video opened successfully")
    
    # Read first frame
    ret, frame = cap.read()
    assert ret, "Failed to read first frame"
    print("✓ First frame read successfully")
    
    # Initialize tracker with a manual ROI (around the ball's starting position)
    tracker = ObjectTracker(zoom_factor=2.0, smoothing=0.1)
    height, width = frame.shape[:2]
    
    # Ball starts at center-right, so we'll select that area
    roi = (width // 2 + 120, height // 2 - 40, 80, 80)
    tracker.tracker = cv2.TrackerCSRT_create()
    tracker.tracker.init(frame, roi)
    tracker.tracking_active = True
    tracker.current_center = np.array([roi[0] + roi[2] / 2, roi[1] + roi[3] / 2])
    tracker.target_center = tracker.current_center.copy()
    print("✓ Tracker initialized with ROI")
    
    # Process a few frames
    frames_processed = 0
    successful_tracks = 0
    
    for i in range(50):  # Process 50 frames
        ret, frame = cap.read()
        if not ret:
            break
        
        frames_processed += 1
        success, bbox = tracker.update(frame)
        
        if success:
            successful_tracks += 1
            # Apply zoom and follow
            zoomed_frame = tracker.apply_zoom_and_follow(frame)
            assert zoomed_frame is not None, "Zoom and follow returned None"
            assert zoomed_frame.shape == frame.shape, "Zoomed frame has wrong shape"
    
    cap.release()
    
    print(f"✓ Processed {frames_processed} frames")
    print(f"✓ Successful tracking: {successful_tracks}/{frames_processed} frames")
    
    # We expect at least 80% successful tracking on this simple synthetic video
    success_rate = successful_tracks / frames_processed if frames_processed > 0 else 0
    assert success_rate > 0.8, f"Tracking success rate too low: {success_rate:.2%}"
    print(f"✓ Tracking success rate: {success_rate:.2%}")
    
    # Clean up
    if os.path.exists(test_video_path):
        os.remove(test_video_path)
        print("✓ Test video cleaned up")
    
    print("\n✓ All video tracking tests passed!")


def test_zoom_application():
    """Test zoom and follow transformation."""
    print("\nTest 3: Zoom and Follow Transformation")
    print("=" * 50)
    
    from obs_zoom_follow import ObjectTracker
    
    # Create a test frame
    test_frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
    
    # Initialize tracker
    tracker = ObjectTracker(zoom_factor=2.0, smoothing=0.1)
    tracker.tracking_active = True
    tracker.current_center = np.array([320.0, 240.0])  # Center of frame
    
    # Apply zoom and follow
    zoomed = tracker.apply_zoom_and_follow(test_frame)
    
    assert zoomed is not None, "Zoom returned None"
    assert zoomed.shape == test_frame.shape, "Zoomed frame has wrong dimensions"
    print("✓ Zoom and follow applied successfully")
    
    # Test with object at edge
    tracker.current_center = np.array([50.0, 50.0])  # Near corner
    zoomed_edge = tracker.apply_zoom_and_follow(test_frame)
    assert zoomed_edge is not None, "Zoom at edge returned None"
    assert zoomed_edge.shape == test_frame.shape, "Zoomed frame at edge has wrong dimensions"
    print("✓ Zoom and follow works at frame edges")
    
    # Test with no tracking active
    tracker.tracking_active = False
    no_zoom = tracker.apply_zoom_and_follow(test_frame)
    assert np.array_equal(no_zoom, test_frame), "Should return original frame when not tracking"
    print("✓ Returns original frame when tracking inactive")
    
    print("\n✓ All zoom transformation tests passed!")


def main():
    """Run all tests."""
    print("\n" + "=" * 50)
    print("OBS Zoom and Follow - Test Suite")
    print("=" * 50)
    
    try:
        test_tracker_basic()
        test_zoom_follow_with_video()
        test_zoom_application()
        
        print("\n" + "=" * 50)
        print("All tests passed successfully! ✓")
        print("=" * 50)
        return 0
        
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        return 1
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
