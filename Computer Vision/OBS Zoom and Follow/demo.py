#!/usr/bin/env python3
"""
Demo script that creates a synthetic video and runs the tracker on it.
This allows testing the OBS Zoom and Follow without needing a webcam.
"""

import cv2
import numpy as np
import subprocess
import os
import sys


def create_demo_video(output_path="demo_video.mp4", duration=15, fps=30):
    """
    Create a demonstration video with multiple moving objects.
    
    Args:
        output_path: Path to save the demo video
        duration: Duration of video in seconds
        fps: Frames per second
    """
    width, height = 1280, 720
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
    
    total_frames = duration * fps
    
    print(f"Creating demo video: {output_path}")
    print(f"Configuration: {width}x{height}, {fps} FPS, {duration}s")
    
    for frame_num in range(total_frames):
        # Create background with gradient
        frame = np.zeros((height, width, 3), dtype=np.uint8)
        for y in range(height):
            frame[y, :] = [30 + y // 10, 40 + y // 15, 50 + y // 20]
        
        # Add some texture
        noise = np.random.randint(0, 20, (height, width, 3), dtype=np.uint8)
        frame = cv2.add(frame, noise)
        
        # Progress through the animation
        progress = frame_num / total_frames
        
        # Moving ball (main object to track)
        t = progress * 3 * np.pi
        ball_x = int(width * 0.3 + width * 0.4 * np.cos(t))
        ball_y = int(height * 0.5 + height * 0.3 * np.sin(t))
        cv2.circle(frame, (ball_x, ball_y), 40, (0, 255, 0), -1)
        cv2.circle(frame, (ball_x, ball_y), 40, (255, 255, 255), 2)
        
        # Add some distractor objects
        # Small moving dot
        dot_x = int(width * 0.7 + 100 * np.sin(progress * 5 * np.pi))
        dot_y = int(height * 0.3)
        cv2.circle(frame, (dot_x, dot_y), 15, (0, 100, 255), -1)
        
        # Moving rectangle
        rect_x = int(width * 0.2 + width * 0.3 * progress)
        rect_y = int(height * 0.7)
        cv2.rectangle(frame, (rect_x - 30, rect_y - 20), (rect_x + 30, rect_y + 20), (255, 0, 255), -1)
        
        # Add instructional text
        cv2.putText(frame, "Demo Video - Track the GREEN BALL", (20, 40),
                   cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 255), 2)
        cv2.putText(frame, f"Frame: {frame_num}/{total_frames}", (20, height - 20),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        
        out.write(frame)
        
        # Progress indicator
        if frame_num % 30 == 0:
            print(f"  Progress: {progress * 100:.1f}%")
    
    out.release()
    print(f"✓ Demo video created: {output_path}")
    print(f"\nInstructions:")
    print(f"  1. The application will start and show the first frame")
    print(f"  2. Draw a box around the GREEN BALL")
    print(f"  3. Watch as the camera automatically zooms and follows the ball")
    print(f"  4. Press 'q' to quit, 'r' to reselect the object\n")
    return output_path


def main():
    """Run the demo."""
    print("=" * 60)
    print("OBS Zoom and Follow - DEMO")
    print("=" * 60)
    print()
    
    # Check if demo video exists, create if not
    demo_video = "demo_video.mp4"
    if not os.path.exists(demo_video):
        create_demo_video(demo_video)
    else:
        print(f"Using existing demo video: {demo_video}")
        print("(Delete demo_video.mp4 to regenerate)")
        print()
    
    # Run the tracker on the demo video
    print("Starting OBS Zoom and Follow tracker...")
    print("=" * 60)
    
    try:
        # Run with moderate zoom and smoothing for good visual effect
        result = subprocess.run([
            sys.executable,
            "obs_zoom_follow.py",
            "--source", demo_video,
            "--zoom", "2.5",
            "--smoothing", "0.15"
        ])
        return result.returncode
    except KeyboardInterrupt:
        print("\nDemo interrupted by user")
        return 0
    except Exception as e:
        print(f"\nError running demo: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
