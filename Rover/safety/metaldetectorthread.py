import threading
import time
import RPi.GPIO as GPIO
from .metaldetector import MetalDetector

class MetalDetectorThread:
    def __init__(self, d0_pin=26, mode=GPIO.BCM):  # Default pin 26 for metal detector
        self.metal_detector = MetalDetector(d0_pin=d0_pin, mode=mode)
        self.metal_flag = threading.Event()
        self._running = False
        self._monitor_thread = None
        
    def start_monitoring(self, check_interval=0.1):
        """Starts a background thread that continuously checks the gas sensor."""
        if not self._running:
            self._running = True
            self._monitor_thread = threading.Thread(
                target=self._monitor_loop,
                args=(check_interval,),
                daemon=True  # Daemon thread dies when the main program exits
            )
            self._monitor_thread.start()

    def _monitor_loop(self, interval):
        """Internal loop running in a separate thread. Modifies the flag state."""
        while self._running:
            if self.metal_detector.detect_metal():
                self.metal_flag.set()  # Gas detected
                print("Metal detected! 🚨")
            else:
                self.metal_flag.clear()  # No gas detected
            
            time.sleep(interval)
            
    def stop_monitoring(self):
        """Stops the background monitoring thread."""
        self._running = False
        if self._monitor_thread is not None:
            self._monitor_thread.join(timeout=2.0)  # Don't hang forever

    def cleanup(self):
        """Clean up only the metal detector pins, don't interfere with other sensors."""
        self.stop_monitoring()
        self.metal_detector.cleanup()