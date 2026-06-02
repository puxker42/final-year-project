import cv2
import socket
import struct
import pickle
import threading
import time

class CameraThread:
    def __init__(self, port=8001):
        self.port = port
        self.running = True
        self.client_socket = None
        self._server_socket = None  # Keep reference to close it properly

    def start_server(self):
        # Close any previous server socket before rebinding
        if self._server_socket:
            try:
                self._server_socket.close()
            except Exception:
                pass
            self._server_socket = None

        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # SO_REUSEADDR allows immediate rebind after disconnect (critical for reconnection)
        self._server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._server_socket.bind(('0.0.0.0', self.port))
        self._server_socket.listen(1)
        print(f"[CAMERA] Server listening on port {self.port}")

        self.client_socket, addr = self._server_socket.accept()
        print(f"[CAMERA] Client connected from {addr}")

    def run(self):
        while self.running:
            try:
                self.start_server()
                cap = cv2.VideoCapture(0)
                
                if not cap.isOpened():
                     print("[CAMERA] Error: Could not open camera")
                     time.sleep(2)
                     continue

                print("[CAMERA] Camera opened successfully")

                while self.running and self.client_socket:
                    ret, frame = cap.read()
                    if not ret:
                        print("[CAMERA] Failed to grab frame")
                        break

                    # Resize to reduce bandwidth
                    frame = cv2.resize(frame, (640, 480))
                    
                    # Compress frame
                    ret, buffer = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 50])
                    data = pickle.dumps(buffer)

                    # Send message length first
                    # Use !L for Network Byte Order (Big Endian) 4-byte unsigned long
                    # consistently across platforms (Win/Linux 32/64)
                    message_size = struct.pack("!L", len(data))

                    try:
                        self.client_socket.sendall(message_size + data)
                    except (ConnectionResetError, BrokenPipeError, OSError):
                        print("[CAMERA] Connection lost")
                        break
                
                cap.release()
                if self.client_socket:
                    self.client_socket.close()
                    self.client_socket = None

            except Exception as e:
                print(f"[CAMERA] Error: {e}")
                time.sleep(1)
