import socket
import threading
import time

ROBOT_IP = "10.42.0.1"   # 🔴 CHANGE THIS to your Pi IP
ROBOT_PORT = 9000

HEARTBEAT_INTERVAL = 0.5  # seconds

running = True


def heartbeat_thread(sock):
    """Continuously send heartbeat while running"""
    global running
    while running:
        try:
            sock.sendall(b"HEARTBEAT\n")
            time.sleep(HEARTBEAT_INTERVAL)
        except:
            print("[OPERATOR] Heartbeat failed")
            break


def receiver_thread(sock):
    """Receive ACKs from robot"""
    global running
    while running:
        try:
            data = sock.recv(1024)
            if not data:
                print("[OPERATOR] Connection closed by robot")
                running = False
                break
            print("[ROBOT]", data.decode().strip())
        except:
            break


def main():
    global running

    print("[OPERATOR] Connecting to robot...")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((ROBOT_IP, ROBOT_PORT))
    print("[OPERATOR] Connected")

    # Start heartbeat sender
    threading.Thread(target=heartbeat_thread, args=(sock,), daemon=True).start()

    # Start ACK receiver
    threading.Thread(target=receiver_thread, args=(sock,), daemon=True).start()

    print("Type commands:")
    print("  f  -> forward")
    print("  s  -> stop")
    print("  q  -> quit")

    while running:
        cmd = input("> ").strip().lower()

        if cmd == "f":
            sock.sendall(b"CMD:FWD\n")

        elif cmd == "s":
            sock.sendall(b"CMD:STOP\n")

        elif cmd == "q":
            print("[OPERATOR] Exiting")
            running = False
            break

    sock.close()


if __name__ == "__main__":
    main()
    