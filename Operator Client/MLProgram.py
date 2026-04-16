import cv2
import os
from ml_detector import MLDetector

# Initialize the detector (Loads models once)
detector = MLDetector()

# Start webcam or video source
# cap = cv2.VideoCapture("video.mp4") # for video
cap = cv2.VideoCapture(0) # for webcam

print("Detection started with custom colors. Press 'q' to quit.")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Use the centralized detector for consistent colors and logic
    final_frame = detector.process_frame(frame)

    if final_frame is not None:
        cv2.imshow("S.C.O.U.T. AI Detection", final_frame)

    # Break loop on 'q' key
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

