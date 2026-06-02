# AgraNetra - Surveillance Rover

AgraNetra is a comprehensive surveillance rover system designed for remote monitoring, threat detection, and environment sensing. The project consists of a hardware rover equipped with various sensors and a camera, along with a remote operator client that provides a web-based user interface with real-time machine learning (ML) object detection capabilities.

## Features

* **Real-time Video Streaming:** Live camera feed from the rover transmitted to the operator client.
* **ML Object Detection:** Integrates YOLOv8 for real-time object detection on the live video stream.
* **Teleoperation:** Remote control of the rover's movements via a web interface or terminal commands.
* **Environment Sensing:**
  * **Gas Sensor:** Detects hazardous gases in the environment.
  * **Metal Detector:** Identifies metallic objects on the ground.
  * **Ultrasonic Sensor:** Provides obstacle avoidance to prevent collisions.
* **Safety & State Management:** Robust state machine architecture ensuring reliable operation and fail-safes.

## System Architecture

The project is split into two primary components:

### 1. Rover (`/Rover`)
The software running on the physical rover (e.g., a Raspberry Pi).
* `main.py`: The entry point that initializes all hardware components and threads.
* `camera/`: Handles video capture from a USB camera and streams it over the network.
* `comm/`: Manages socket-based communication with the operator client.
* `control/`: Motor controllers and ultrasonic sensor-based obstacle avoidance.
* `safety/`: Gas sensor and metal detector monitoring threads.
* `state_machine.py`: Manages the operational state of the rover (Idle, Moving, Alert, etc.).

### 2. Operator Client (`/Operator Client`)
The control center software running on the operator's machine.
* `ui_server.py`: A Flask web server providing the main user interface.
* `ml_detector.py` / `ml_client.py`: Handles processing the incoming video feed through a YOLOv8 neural network.
* `robot_client.py`: Connects to the rover to send movement commands and receive telemetry/ACKs.
* `video_client.py`: Receives and decodes the video stream from the rover.

## Setup & Installation

### Prerequisites
* Python 3.x
* OpenCV (`cv2`)
* Flask
* Ultralytics (for YOLOv8)
* PyTorch

### Hardware Setup
It is highly recommended to use a **Raspberry Pi 4 Model B (or higher)** for the onboard computer, as running the video streaming thread, communication thread, and multiple sensor threads simultaneously requires sufficient processing power and memory.

#### Pin Configuration (GPIO / BCM)

| Component | Sensor/Module Pin | Raspberry Pi GPIO (BCM) |
| :--- | :--- | :--- |
| **Motor Controller** | IN1 | GPIO 17 |
| | IN2 | GPIO 18 |
| | IN3 | GPIO 22 |
| | IN4 | GPIO 23 |
| | Destroy/Enable | GPIO 21 |
| **Ultrasonic Sensor** | TRIG | GPIO 24 |
| | ECHO | GPIO 25 |
| **Metal Detector** | D0 | GPIO 26 |
| **Gas Sensor** | D0 | GPIO 27 |

*Note: The code uses BCM numbering (`GPIO.setmode(GPIO.BCM)`). Ensure you use a Raspberry Pi pinout diagram to match BCM numbers to the physical pins.*

### Rover Software Setup
1. **Enable Wi-Fi Hotspot on Raspberry Pi:**
   To allow the Operator Client to connect directly to the rover without an external router, configure the Raspberry Pi to act as a Wi-Fi hotspot. On modern Raspberry Pi OS (using NetworkManager), you can enable it using the following command:
   ```bash
   sudo nmcli dev wifi hotspot ifname wlan0 ssid AgraNetra_Rover password your_secure_password
   ```
   *(Note: The Rover IP when acting as a hotspot is typically `10.42.0.1`, which is the default IP configured in the Operator Client.)*
2. Transfer the `Rover` directory to the Raspberry Pi.
3. Install dependencies (e.g., `RPi.GPIO` for pin control).
4. Connect the USB camera, motors, and sensors to the GPIO pins according to the table above.
5. Run the rover software:
   ```bash
   cd Rover
   python main.py
   ```

### Operator Client Setup
1. Ensure you have the `yolov8n.pt` weights file in the `Operator Client` directory.
2. Install the required Python packages:
   ```bash
   cd "Operator Client"
   pip install -r requirements.txt
   ```
3. Run the Flask UI Server:
   ```bash
   python ui_server.py
   ```
4. Open a web browser and navigate to `http://localhost:8080` (or the IP address of the operator machine) to access the AgraNetra UI.

## Usage
* Once the UI is running and connected to the rover (default IP `10.42.0.1`), the video feed will display with ML bounding boxes.
* Use the web interface controls to navigate the rover.
* Sensor alerts (Gas/Metal) and obstacle warnings will be processed by the rover and reflected in its behavior.

## Technologies Used
* **Python:** Core programming language.
* **OpenCV:** Image processing and streaming.
* **Flask:** Web server framework for the UI.
* **YOLOv8 (Ultralytics):** Machine learning model for object detection.
* **Sockets:** TCP/UDP networking for low-latency communication.
