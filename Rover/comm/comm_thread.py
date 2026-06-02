import socket
import time
from state_machine import RobotState

HEARTBEAT_TIMEOUT = 2.0  # seconds

class CommThread:
    def __init__(self, state_machine, motor_controller, metal_sensor=None, gas_sensor=None, ultrasonic_sensor=None, host="0.0.0.0", port=9000):
        self.state_machine = state_machine
        self.motor_controller = motor_controller
        self.metal_sensor = metal_sensor
        self.gas_sensor = gas_sensor
        self.ultrasonic_sensor = ultrasonic_sensor
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
        except Exception as e:
            print(f"[COMM] Failed to send ack: {e}")

    def handle_message(self, msg):
        msg = msg.strip()

        if msg == "HEARTBEAT":
            self.last_heartbeat = time.time()
            self.send_ack("ACK:HB\n")

            m = 1 if self.metal_sensor and self.metal_sensor.metal_flag.is_set() else 0
            g = 1 if self.gas_sensor and self.gas_sensor.gas_flag.is_set() else 0
            u = self.ultrasonic_sensor.last_distance if self.ultrasonic_sensor else -1.0
            self.send_ack(f"SENSORS:{m},{g},{u}\n")

            if self.state_machine.get_state() == RobotState.COMM_LOST:
                self.state_machine.set_state(RobotState.IDLE)

        elif msg.startswith("CMD:"):
            self.last_heartbeat = time.time() # Any command counts as heartbeat
            cmd = msg.split(":", 1)[1]   # maxsplit=1 so values with ':' are safe
            print(f"[COMM] Recv Command: {cmd}")
            self.send_ack("ACK:CMD\n")
            try:
                self.motor_controller.process_command(cmd)
            except ValueError as e:
                print(f"[COMM] Unknown command ignored: {e}")
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
                self.motor_controller.stop()  # Safety: stop motors immediately on any disconnect
                self.state_machine.set_state(RobotState.COMM_LOST)
                # Close the old listening socket before rebinding to avoid 'Address already in use'
                try:
                    self.conn.close()
                except Exception:
                    pass
                try:
                    self.sock.close()
                except Exception:
                    pass
                time.sleep(2)
                try:
                    self.start_server()
                except Exception as reconnect_err:
                    print(f"[COMM] Reconnect failed: {reconnect_err}")
                    time.sleep(3)  # Back-off before retry loop
                    continue       # Skip heartbeat check — conn may not be valid yet

            self.check_heartbeat()
            time.sleep(0.05)