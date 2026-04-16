from flask import Flask, render_template, Response, jsonify
import cv2
import threading
import time

from robot_client import RobotClient
from video_client import VideoClient
from ml_detector import MLDetector

ROBOT_IP = "10.42.0.1"

app = Flask(__name__)

# Robot control client
robot = RobotClient(ROBOT_IP)

# Video client
video = VideoClient(ROBOT_IP)

# ML Detector Placeholder
detector = None
processed_frame = None

def initialize_services():
    global detector
    print("[UI SERVER] Initializing services in background...")
    
    # Connect to Robot (non-blocking)
    try:
        print(f"[UI SERVER] Connecting to robot at {ROBOT_IP}...")
        robot.connect()
    except Exception as e:
        print(f"[UI SERVER] Robot connection failed: {e}")

    # Start Video
    try:
        print(f"[UI SERVER] Starting video stream...")
        video.start()
    except Exception as e:
        print(f"[UI SERVER] Video start failed: {e}")

    # Load ML Detector (slowest part)
    print("[UI SERVER] Loading ML models...")
    detector = MLDetector()
    print("[UI SERVER] ML Models loaded.")

def detection_loop():
    global processed_frame
    print("[UI SERVER] Detection loop active (Full Capacity)")
    while True:
        if detector is not None and video.latest_frame is not None:
            # Run detection at maximum speed
            processed_frame = detector.process_frame(video.latest_frame)

# Start background initialization
threading.Thread(target=initialize_services, daemon=True).start()
threading.Thread(target=detection_loop, daemon=True).start()

def generate_video():
    while True:
        # Check for frame source availability
        frame_to_serve = processed_frame if processed_frame is not None else video.latest_frame
        
        if frame_to_serve is None:
            # Check if we are still connecting
            msg = "CONNECTING TO ROVER..."
            placeholder = 255 * (cv2.imread("static/loading.png") if False else 0) # Placeholder logic
            # Just send an empty frame or wait
            time.sleep(0.1)
            continue

        ret, buffer = cv2.imencode('.jpg', frame_to_serve)
        frame = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' +
               frame + b'\r\n')

        
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video')
def video_feed():
    return Response(generate_video(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route("/status")
def status():
    return jsonify(
        connected=robot.running,
        last_ack=robot.last_ack
    )

@app.route("/cmd/<cmd>")
def send_cmd(cmd):
    robot.send_cmd(cmd)
    return jsonify(status="sent")

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080, threaded=True)