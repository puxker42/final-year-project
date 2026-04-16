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
            except:
                self.running = False

    def _receiver(self):
        while self.running:
            try:
                data = self.sock.recv(1024)
                if not data:
                    self.running = False
                    break

                msg = data.decode().strip()
                self.last_ack = msg

                if msg.startswith("STATUS:"):
                    self.robot_state = msg.split(":", 1)[1]

            except:
                self.running = False
                break

    def send_cmd(self, cmd):
        if self.running:
            self.sock.sendall(f"CMD:{cmd}\n".encode())