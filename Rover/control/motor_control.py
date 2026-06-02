import RPi.GPIO as GPIO

class MotorController:
    def __init__(self, in1=17, in2=18, in3=22, in4=23, destroy_pin=21):
        self.in1 = in1
        self.in2 = in2
        self.in3 = in3
        self.in4 = in4
        self.destroy_pin = destroy_pin

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.in1, GPIO.OUT)
        GPIO.setup(self.in2, GPIO.OUT)
        GPIO.setup(self.in3, GPIO.OUT)
        GPIO.setup(self.in4, GPIO.OUT)
        GPIO.setup(self.destroy_pin, GPIO.OUT)

        self.stop()  # Ensure motors are stopped at startup
        GPIO.output(self.destroy_pin, GPIO.LOW)

    # ---------------- BASIC MOVEMENTS ----------------

    def stop(self):
        GPIO.output(self.in1, GPIO.LOW)
        GPIO.output(self.in2, GPIO.LOW)
        GPIO.output(self.in3, GPIO.LOW)
        GPIO.output(self.in4, GPIO.LOW)

    def backward(self):
        print("[MOTOR] BACKWARD execution started")
        GPIO.output(self.in1, GPIO.HIGH)
        GPIO.output(self.in2, GPIO.LOW)
        GPIO.output(self.in3, GPIO.LOW)
        GPIO.output(self.in4, GPIO.HIGH)

    def forward(self):
        GPIO.output(self.in1, GPIO.LOW)
        GPIO.output(self.in2, GPIO.HIGH)
        GPIO.output(self.in3, GPIO.HIGH)
        GPIO.output(self.in4, GPIO.LOW)

    def right(self):
        # Differential turn: Left side backward, Right side forward
        GPIO.output(self.in1, GPIO.HIGH)
        GPIO.output(self.in2, GPIO.LOW)
        GPIO.output(self.in3, GPIO.HIGH)
        GPIO.output(self.in4, GPIO.LOW)

    def left(self):
        print("[MOTOR] LEFT execution started")
        # Differential turn: Left side forward, Right side backward
        GPIO.output(self.in1, GPIO.LOW)
        GPIO.output(self.in2, GPIO.HIGH)
        GPIO.output(self.in3, GPIO.LOW)
        GPIO.output(self.in4, GPIO.HIGH)

    # ---------------- COMMAND INTERFACE ----------------

    def process_command(self, cmd: str):
        cmd = cmd.strip().upper()
        print(f"[MOTOR] Processing command: {cmd}")

        if cmd == "FWD":
            self.forward()
        elif cmd == "BACK":
            self.backward()
        elif cmd == "LEFT":
            self.left()
        elif cmd == "RIGHT":
            self.right()
        elif cmd == "STOP":
            self.stop()
        elif cmd == "DESTROY":
            self.destroy()
        else:
            raise ValueError(f"Invalid command: {cmd}")

    def destroy(self):
        self.stop()
        GPIO.output(self.destroy_pin, GPIO.HIGH)

    # ---------------- CLEANUP ----------------

    def cleanup(self):
        self.stop()
        # GPIO.cleanup() should typically be handled by the main program
