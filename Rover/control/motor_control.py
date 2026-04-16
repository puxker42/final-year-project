import RPi.GPIO as GPIO

class MotorController:
    def __init__(self, in1=17, in2=18, in3=22, in4=23, mode=GPIO.BCM):
        self.IN1 = in1 # Left motor(s) forward pin
        self.IN2 = in2 # Left motor(s) backward pin
        self.IN3 = in3 # Right motor(s) forward pin
        self.IN4 = in4 # Right motor(s) backward pin
    
        GPIO.setmode(mode)

        GPIO.setup(self.IN1, GPIO.OUT)
        GPIO.setup(self.IN2, GPIO.OUT)
        GPIO.setup(self.IN3, GPIO.OUT)
        GPIO.setup(self.IN4, GPIO.OUT)

        self.stop()  # Ensure motors are stopped at startup

    # ---------------- BASIC MOVEMENTS ----------------

    def stop(self):
        GPIO.output(self.IN1, 0)
        GPIO.output(self.IN2, 0)
        GPIO.output(self.IN3, 0)
        GPIO.output(self.IN4, 0)

    def forward(self):
        GPIO.output(self.IN1, 1)
        GPIO.output(self.IN2, 0)
        GPIO.output(self.IN3, 0)
        GPIO.output(self.IN4, 1)

    def backward(self):
        GPIO.output(self.IN1, 0)
        GPIO.output(self.IN2, 1)
        GPIO.output(self.IN3, 1)
        GPIO.output(self.IN4, 0)

    def left(self):
        # Differential turn: Left side backward, Right side forward
        GPIO.output(self.IN1, 1)
        GPIO.output(self.IN2, 0)
        GPIO.output(self.IN3, 1)
        GPIO.output(self.IN4, 0)

    def right(self):
        # Differential turn: Left side forward, Right side backward
        GPIO.output(self.IN1, 0)
        GPIO.output(self.IN2, 1)
        GPIO.output(self.IN3, 0)
        GPIO.output(self.IN4, 1)

    # ---------------- COMMAND INTERFACE ----------------

    def process_command(self, cmd: str):
        cmd = cmd.strip().upper()

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
        else:
            raise ValueError(f"Invalid command: {cmd}")

    # ---------------- CLEANUP ----------------

    def cleanup(self):
        self.stop()
        GPIO.cleanup()
