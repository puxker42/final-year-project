import RPi.GPIO as GPIO
import threading
import time

class Ultrasonic_sensor:
    """
    A completely independent class to interface with an HC-SR04 Ultrasonic sensor.
    Uses RPi.GPIO for hardware interaction.
    """
    def __init__(self, trig_pin=24, echo_pin=25, max_distance=4.0):
        self.trig_pin = trig_pin
        self.echo_pin = echo_pin
        self.max_distance = max_distance

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.trig_pin, GPIO.OUT)
        GPIO.setup(self.echo_pin, GPIO.IN)
        GPIO.output(self.trig_pin, False)

        # Thread-safe boolean flag for obstacle detection
        self.obstacle_flag = threading.Event()
        self.last_distance = -1.0

        # Variables for the background monitoring thread
        self._running = False
        self._monitor_thread = None

    def get_distance(self):
        """
        Returns the distance in centimetres.
        Returns -1.0 if the reading is out of range or sensor times out.
        """
        try:
            # Send 10us pulse
            GPIO.output(self.trig_pin, True)
            time.sleep(0.00001)
            GPIO.output(self.trig_pin, False)

            pulse_start = time.time()
            pulse_end = time.time()
            timeout = pulse_start + 0.05 # 50ms timeout

            while GPIO.input(self.echo_pin) == 0:
                pulse_start = time.time()
                if pulse_start > timeout: return -1.0

            while GPIO.input(self.echo_pin) == 1:
                pulse_end = time.time()
                if pulse_end > timeout: return -1.0

            pulse_duration = pulse_end - pulse_start
            distance = pulse_duration * 17150
            distance = round(distance, 2)
            
            if distance > self.max_distance * 100:
                return -1.0
                
            return distance
        except Exception:
            return -1.0

    def start_monitoring(self, threshold_cm=20.0, check_interval=0.1):
        """
        Starts a background thread that continuously checks the distance.
        Changes the state of `obstacle_flag` automatically without blocking the main program.
        """
        if not self._running:
            self._running = True
            self._monitor_thread = threading.Thread(
                target=self._monitor_loop,
                args=(threshold_cm, check_interval),
                daemon=True  # Daemon thread dies when the main program exits
            )
            self._monitor_thread.start()

    def _monitor_loop(self, threshold_cm, interval):
        """Internal loop running in a separate thread. Modifies the flag state."""
        while self._running:
            dist = self.get_distance()
            self.last_distance = dist

            # If distance is valid and below our safety threshold -> Set the flag (True)
            if dist != -1.0 and dist <= threshold_cm:
                self.obstacle_flag.set()
            # Otherwise -> Clear the flag (False)
            else:
                self.obstacle_flag.clear()

            time.sleep(interval)

    def stop_monitoring(self):
        """Stops the background monitoring thread."""
        self._running = False
        if self._monitor_thread is not None:
            self._monitor_thread.join(timeout=2.0)  # Don't hang forever if thread is stuck

    def cleanup(self):
        """
        Clean up ONLY the sensor, keeping independence so we don't accidentally
        interfere with motor pins.
        """
        self.stop_monitoring()


if __name__ == "__main__":
    # Standalone testing block
    sensor = Ultrasonic_sensor(trig_pin=24, echo_pin=25)

    print("Starting background sensor monitoring... (Threshold: 15cm)")
    sensor.start_monitoring(threshold_cm=15.0, check_interval=0.1)

    try:
        while True:
            if sensor.obstacle_flag.is_set():
                print(f"🚨 OBSTACLE! Distance: {sensor.last_distance}cm — STOP MOTORS 🚨")
            else:
                print(f"Path clear. Distance: {sensor.last_distance}cm")

            time.sleep(0.5)
    except KeyboardInterrupt:
        print("\nMeasurement stopped by operator.")
    finally:
        sensor.cleanup()
