import socket
import threading
import time

class RobotClient:
    def __init__(self, ip, port=9000):
        self.ip = ip
        self.port = port
        self.sock = None
        self.running = False
        self.last_ack = "DISCONNECTED"
        self.robot_state = "UNKNOWN"
        self.sensors = {"metal": False, "gas": False, "obstacle_dist": -1.0}
    def connect(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.ip, self.port))
        self.running = True

        threading.Thread(target=self._heartbeat, daemon=True).start()
        threading.Thread(target=self._receiver, daemon=True).start()

    def _heartbeat(self):
        while self.running:
            try:
                self.sock.sendall(b"HEARTBEAT\n")
                time.sleep(0.5)
            except Exception as e:
                print(f"[ROBOT_CLIENT] Heartbeat failed: {e}")
                self.running = False

    def _receiver(self):
        while self.running:
            try:
                data = self.sock.recv(1024)
                if not data:
                    self.running = False
                    break

                # TCP may bundle multiple messages in one recv() — split by newline
                for line in data.decode().splitlines():
                    msg = line.strip()
                    if not msg:
                        continue

                    self.last_ack = msg

                    if msg.startswith("STATUS:"):
                        self.robot_state = msg.split(":", 1)[1]
                    elif msg.startswith("SENSORS:"):
                        parts = msg.split(":", 1)[1].split(",")
                        if len(parts) == 3:
                            self.sensors["metal"] = parts[0] == "1"
                            self.sensors["gas"] = parts[1] == "1"
                            try:
                                self.sensors["obstacle_dist"] = float(parts[2])
                            except ValueError:
                                self.sensors["obstacle_dist"] = -1.0

            except Exception as e:
                print(f"[ROBOT_CLIENT] Receiver error: {e}")
                self.running = False
                break

    def send_cmd(self, cmd):
        if self.running:
            try:
                self.sock.sendall(f"CMD:{cmd}\n".encode())
            except Exception as e:
                print(f"[ROBOT_CLIENT] Failed to send command '{cmd}': {e}")
                self.running = False