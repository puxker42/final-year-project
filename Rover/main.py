import threading
import time

from state_machine import StateMachine, RobotState
from comm.comm_thread import CommThread
from camera.camera_thread import CameraThread

# --------------------------------------------------
# Hardware Initialization
# --------------------------------------------------
state_machine = StateMachine()
state_machine.set_state(RobotState.IDLE)

from control.motor_control import MotorController
try:
    motor_controller = MotorController()
except Exception as e:
    print(f"[MAIN] FATAL: Motor controller failed to initialize: {e}")
    raise  # Motors are critical — cannot run without them

from safety.metaldetectorthread import MetalDetectorThread
from safety.gassensorthread import GasSensorThread
from control.obstacle_avoidance import Ultrasonic_sensor

try:
    metal_sensor = MetalDetectorThread()
    metal_sensor.start_monitoring()
except Exception as e:
    print(f"[MAIN] WARNING: Metal detector failed to initialize: {e}")
    metal_sensor = None

try:
    gas_sensor = GasSensorThread()
    gas_sensor.start_monitoring()
except Exception as e:
    print(f"[MAIN] WARNING: Gas sensor failed to initialize: {e}")
    gas_sensor = None

try:
    ultrasonic_sensor = Ultrasonic_sensor()
    ultrasonic_sensor.start_monitoring(threshold_cm=20.0)
except Exception as e:
    print(f"[MAIN] WARNING: Ultrasonic sensor failed to initialize: {e}")
    ultrasonic_sensor = None

# --------------------------------------------------
# REAL COMMUNICATION THREAD
# --------------------------------------------------
comm = CommThread(state_machine, motor_controller, metal_sensor, gas_sensor, ultrasonic_sensor)

def comm_runner():
    comm.run()

# --------------------------------------------------
# REAL VIDEO STREAM THREAD (USB CAMERA)
# --------------------------------------------------
camera = CameraThread()

def camera_runner():
    camera.run()

# --------------------------------------------------
# Thread Creation
# --------------------------------------------------
threads = [
    threading.Thread(target=camera_runner, daemon=True),
    threading.Thread(target=comm_runner, daemon=True),
]

# --------------------------------------------------
# Start Threads
# --------------------------------------------------
for t in threads:
    t.start()

print("[SYSTEM] All threads started successfully")

# --------------------------------------------------
# Keep Main Process Alive
# --------------------------------------------------
while True:
    time.sleep(5)