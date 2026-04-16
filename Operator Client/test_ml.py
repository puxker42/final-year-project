import cv2
import numpy as np
import os
from ml_detector import MLDetector

def test():
    print("Testing MLDetector...")
    try:
        detector = MLDetector()
        print("Detector initialized.")
        
        # Create a blank frame
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        
        # Process the frame
        processed = detector.process_frame(frame)
        
        if processed is not None:
            print("Successfully processed a dummy frame.")
            print(f"Detector has_custom: {detector.has_custom}")
            print(f"Detector coco_model: {detector.coco_model is not None}")
        else:
            print("Failed to process frame (returned None).")
            
    except Exception as e:
        print(f"Error during testing: {e}")

if __name__ == "__main__":
    test()
