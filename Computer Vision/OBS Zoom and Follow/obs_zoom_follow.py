#!/usr/bin/env python3
"""
OBS Zoom and Follow - Object Tracking with Dynamic Zoom and Pan
This script tracks objects in video streams and automatically zooms and follows them.
"""

import cv2
import numpy as np
import argparse
import sys


class ObjectTracker:
    """Handles object detection and tracking with zoom and follow capabilities."""
    
    def __init__(self, zoom_factor=2.0, smoothing=0.1):
        """
        Initialize the object tracker.
        
        Args:
            zoom_factor (float): Zoom magnification factor (1.0 = no zoom, 2.0 = 2x zoom)
            smoothing (float): Smoothing factor for camera movement (0.0-1.0)
        """
        self.zoom_factor = max(1.0, min(5.0, zoom_factor))
        self.smoothing = max(0.0, min(1.0, smoothing))
        self.tracker = None
        self.tracking_active = False
        self.current_center = None
        self.target_center = None
        
    def select_roi(self, frame):
        """
        Allow user to select a region of interest to track.
        
        Args:
            frame: Input video frame
            
        Returns:
            bool: True if ROI was selected successfully
        """
        roi = cv2.selectROI("Select Object to Track", frame, fromCenter=False, showCrosshair=True)
        cv2.destroyWindow("Select Object to Track")
        
        if roi[2] > 0 and roi[3] > 0:
            # Initialize tracker with selected ROI
            self.tracker = cv2.TrackerCSRT_create()
            self.tracker.init(frame, roi)
            self.tracking_active = True
            
            # Initialize center position
            self.current_center = np.array([
                roi[0] + roi[2] / 2,
                roi[1] + roi[3] / 2
            ])
            self.target_center = self.current_center.copy()
            return True
        return False
    
    def update(self, frame):
        """
        Update tracker and get current object position.
        
        Args:
            frame: Current video frame
            
        Returns:
            tuple: (success, bounding_box) where bounding_box is (x, y, w, h)
        """
        if not self.tracking_active or self.tracker is None:
            return False, None
        
        success, bbox = self.tracker.update(frame)
        
        if success:
            # Update target center based on tracked object
            self.target_center = np.array([
                bbox[0] + bbox[2] / 2,
                bbox[1] + bbox[3] / 2
            ])
            
            # Smooth the camera movement
            if self.current_center is not None:
                self.current_center = (
                    self.smoothing * self.target_center + 
                    (1 - self.smoothing) * self.current_center
                )
            else:
                self.current_center = self.target_center.copy()
        
        return success, bbox
    
    def apply_zoom_and_follow(self, frame):
        """
        Apply zoom and follow effect to keep tracked object centered.
        
        Args:
            frame: Input video frame
            
        Returns:
            numpy.ndarray: Transformed frame with zoom and follow applied
        """
        if not self.tracking_active or self.current_center is None:
            return frame
        
        height, width = frame.shape[:2]
        
        # Calculate the region to extract (zoomed region centered on object)
        roi_width = int(width / self.zoom_factor)
        roi_height = int(height / self.zoom_factor)
        
        # Calculate top-left corner of ROI, centered on tracked object
        x1 = int(self.current_center[0] - roi_width / 2)
        y1 = int(self.current_center[1] - roi_height / 2)
        
        # Clamp to frame boundaries
        x1 = max(0, min(x1, width - roi_width))
        y1 = max(0, min(y1, height - roi_height))
        
        x2 = x1 + roi_width
        y2 = y1 + roi_height
        
        # Extract and resize the ROI to original frame size
        roi = frame[y1:y2, x1:x2]
        zoomed = cv2.resize(roi, (width, height), interpolation=cv2.INTER_LINEAR)
        
        return zoomed
    
    def draw_tracking_info(self, frame, bbox):
        """
        Draw tracking information on the frame.
        
        Args:
            frame: Frame to draw on
            bbox: Bounding box (x, y, w, h) or None
        """
        height, width = frame.shape[:2]
        
        if bbox is not None:
            # Draw bounding box
            x, y, w, h = [int(v) for v in bbox]
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            
            # Draw center crosshair
            center_x = x + w // 2
            center_y = y + h // 2
            cv2.drawMarker(frame, (center_x, center_y), (0, 255, 0), 
                          cv2.MARKER_CROSS, 20, 2)
        
        # Draw info text
        cv2.putText(frame, f"Zoom: {self.zoom_factor:.1f}x", (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.putText(frame, "Press 'q' to quit, 'r' to reselect", (10, height - 10),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        return frame


def main():
    """Main function to run the OBS Zoom and Follow tracker."""
    parser = argparse.ArgumentParser(
        description="OBS Zoom and Follow - Track objects with automatic zoom and pan"
    )
    parser.add_argument(
        "--source",
        type=str,
        default="0",
        help="Video source: camera index (0, 1, ...) or video file path"
    )
    parser.add_argument(
        "--zoom",
        type=float,
        default=2.0,
        help="Zoom factor (1.0-5.0, default: 2.0)"
    )
    parser.add_argument(
        "--smoothing",
        type=float,
        default=0.1,
        help="Camera movement smoothing (0.0-1.0, default: 0.1)"
    )
    
    args = parser.parse_args()
    
    # Open video source
    try:
        source = int(args.source)
    except ValueError:
        source = args.source
    
    cap = cv2.VideoCapture(source)
    
    if not cap.isOpened():
        print(f"Error: Could not open video source '{args.source}'")
        return 1
    
    # Initialize tracker
    tracker = ObjectTracker(zoom_factor=args.zoom, smoothing=args.smoothing)
    
    print("OBS Zoom and Follow - Object Tracker")
    print("====================================")
    print("Instructions:")
    print("  - A window will open showing the video feed")
    print("  - Select an object to track by drawing a box around it")
    print("  - Press 'q' to quit")
    print("  - Press 'r' to reselect object")
    print()
    
    # Read first frame and select object
    ret, frame = cap.read()
    if not ret:
        print("Error: Could not read from video source")
        cap.release()
        return 1
    
    if not tracker.select_roi(frame):
        print("No object selected. Exiting.")
        cap.release()
        return 1
    
    print("Tracking started! Press 'q' to quit.")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            print("End of video or error reading frame")
            break
        
        # Update tracker
        success, bbox = tracker.update(frame)
        
        if success:
            # Apply zoom and follow effect
            processed_frame = tracker.apply_zoom_and_follow(frame)
            
            # Draw tracking info on the zoomed frame
            # Note: bbox coordinates are from original frame, need adjustment
            if bbox is not None:
                # Adjust bbox coordinates for display on zoomed frame
                h, w = frame.shape[:2]
                roi_w = int(w / tracker.zoom_factor)
                roi_h = int(h / tracker.zoom_factor)
                
                x1 = int(tracker.current_center[0] - roi_w / 2)
                y1 = int(tracker.current_center[1] - roi_h / 2)
                
                # Transform bbox to zoomed coordinate system
                adjusted_bbox = (
                    (bbox[0] - x1) * tracker.zoom_factor,
                    (bbox[1] - y1) * tracker.zoom_factor,
                    bbox[2] * tracker.zoom_factor,
                    bbox[3] * tracker.zoom_factor
                )
                
                processed_frame = tracker.draw_tracking_info(processed_frame, adjusted_bbox)
            else:
                processed_frame = tracker.draw_tracking_info(processed_frame, None)
        else:
            # Tracking failed
            processed_frame = frame.copy()
            cv2.putText(processed_frame, "Tracking Lost! Press 'r' to reselect", 
                       (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            tracker.tracking_active = False
        
        # Display result
        cv2.imshow("OBS Zoom and Follow", processed_frame)
        
        # Handle key presses
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('r'):
            # Reselect object
            ret, frame = cap.read()
            if ret:
                if tracker.select_roi(frame):
                    print("New object selected!")
                else:
                    print("No object selected, continuing...")
    
    # Cleanup
    cap.release()
    cv2.destroyAllWindows()
    return 0


if __name__ == "__main__":
    sys.exit(main())
