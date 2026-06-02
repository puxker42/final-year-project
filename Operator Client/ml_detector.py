import cv2
from ultralytics import YOLO
import os

class MLDetector:
    def __init__(self):
        # Get the directory of the current script
        SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

        # Load models using absolute paths
        custom_model_path = os.path.join(SCRIPT_DIR, "runs", "detect", "train8", "weights", "best.pt")
        coco_model_path = os.path.join(SCRIPT_DIR, "yolov8n.pt")
        
        print(f"[ML] Loading models...")
        
        # Custom model (Gun/Knife)
        self.has_custom = False
        if os.path.exists(custom_model_path):
            try:
                self.custom_model = YOLO(custom_model_path)
                self.has_custom = True
                print(f"[ML] Custom model loaded from {custom_model_path}")
            except Exception as e:
                print(f"[ML] Failed to load custom model: {e}")
        else:
            print(f"[ML] Custom model not found at {custom_model_path}")

        # COCO model (Human/Cell phone)
        try:
            self.coco_model = YOLO(coco_model_path)
            print(f"[ML] COCO model loaded from {coco_model_path}")
        except Exception as e:
            print(f"[ML] Failed to load COCO model: {e}")
            self.coco_model = None

        self.HUMAN_CLASS_ID = 0
        self.CELL_PHONE_CLASS_ID = 67

    def process_frame(self, frame):
        if frame is None:
            return None
            
        final_frame = frame.copy()

        # ---------- CUSTOM MODEL: Gun / Knife ----------
        if self.has_custom:
            try:
                # Running at full resolution (no imgsz limit)
                custom_results = self.custom_model(frame, stream=True, verbose=False)
                for res in custom_results:
                    for box in res.boxes:
                        cls = int(box.cls[0])
                        conf = float(box.conf[0])
                        x1, y1, x2, y2 = map(int, box.xyxy[0])
                    
                        if conf > 0.4: 
                            if cls == 0: # Gun
                                label, color = "Gun", (0, 0, 255) # Red
                            else: # Knife
                                label, color = "Knife", (0, 165, 255) # Orange (BGR: 0, 165, 255)
                            
                            cv2.rectangle(final_frame, (x1, y1), (x2, y2), color, 2)
                            cv2.putText(final_frame, f"{label} {conf:.2f}",
                                        (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX,
                                        0.6, color, 2)
            except Exception:
                pass

        # ---------- COCO MODEL: Human / Cell phone ----------
        if self.coco_model:
            try:
                # Running at full resolution (no imgsz limit)
                coco_results = self.coco_model(frame, stream=True, verbose=False)
                for res in coco_results:
                    for box in res.boxes:
                        cls = int(box.cls[0])
                        conf = float(box.conf[0])
                        x1, y1, x2, y2 = map(int, box.xyxy[0])

                        if cls in [self.HUMAN_CLASS_ID, self.CELL_PHONE_CLASS_ID] and conf > 0.4:
                            if cls == self.HUMAN_CLASS_ID:
                                label, color = "Human", (0, 255, 255) # Yellow (BGR: 0, 255, 255)
                            else:
                                label, color = "Cell Phone", (255, 0, 0) # Blue (BGR: 255, 0, 0)
                            
                            cv2.rectangle(final_frame, (x1, y1), (x2, y2), color, 2)
                            cv2.putText(final_frame, f"{label} {conf:.2f}",
                                        (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX,
                                        0.6, color, 2)
            except Exception:
                pass

        return final_frame


