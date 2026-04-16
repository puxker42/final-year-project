import socket
import time
from control.motor_control import MotorController
from state_machine import RobotState

HEARTBEAT_TIMEOUT = 2.0  # seconds

class CommThread:
    def __init__(self, state_machine, motor_controller, host="0.0.0.0", port=9000):
        self.state_machine = state_machine
        self.motor_controller = motor_controller
        self.host = host
        self.port = port
        self.last_heartbeat = time.time()
        self.running = True

    def start_server(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.host, self.port))
        self.sock.listen(1)

        print("[COMM] Waiting for operator...")
        self.conn, self.addr = self.sock.accept()
        self.conn.settimeout(0.2)
        print(f"[COMM] Operator connected from {self.addr}")

        self.state_machine.set_state(RobotState.IDLE)

    def send_ack(self, msg):
        try:
            self.conn.sendall(msg.encode())
        except:
            pass

    def handle_message(self, msg):
        msg = msg.strip()

        if msg == "HEARTBEAT":
            self.last_heartbeat = time.time()
            self.send_ack("ACK:HB\n")

            if self.state_machine.get_state() == RobotState.COMM_LOST:
                self.state_machine.set_state(RobotState.IDLE)

        elif msg.startswith("CMD:"):
            self.last_heartbeat = time.time() # Any command counts as heartbeat
            cmd = msg.split(":")[1]
            print(f"[COMM] Recv Command: {cmd}")
            self.send_ack("ACK:CMD\n")
            self.motor_controller.process_command(cmd)
            self.state_machine.set_state(RobotState.MANUAL_CONTROL)

        elif msg == "STATUS?":
            state = self.state_machine.get_state().name
            self.send_ack(f"STATUS:{state}\n")

    def check_heartbeat(self):
        if time.time() - self.last_heartbeat > HEARTBEAT_TIMEOUT:
            current_state = self.state_machine.get_state()
            if current_state != RobotState.COMM_LOST:
                print("[COMM] Heartbeat lost! Stopping motors...")
                self.motor_controller.stop()
                self.state_machine.set_state(RobotState.COMM_LOST)

    def run(self):
        self.start_server()

        while self.running:
            try:
                data = self.conn.recv(1024)
                if not data:
                    raise ConnectionError

                messages = data.decode().splitlines()
                for msg in messages:
                    if msg.strip():
                        self.handle_message(msg)

            except socket.timeout:
                pass
            except Exception as e:
                print(f"[COMM] Connection error: {e}")
                self.state_machine.set_state(RobotState.COMM_LOST)
                time.sleep(2)
                try:
                    self.start_server()
                except:
                    pass

            self.check_heartbeat()
            time.sleep(0.05)