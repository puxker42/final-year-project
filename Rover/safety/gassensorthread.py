''' check whether the gas is leaked or not '''
''' if gas detected then send that info to the operator '''
import threading
import time
import RPi.GPIO as GPIO
from .gassensor import GasSensor

class GasSensorThread:
    def __init__(self, d0_pin=27, mode=GPIO.BCM):
        self.gas_sensor = GasSensor(d0_pin=d0_pin, mode=mode)
        self.gas_flag = threading.Event()
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
            if self.gas_sensor.detect_gas():
                self.gas_flag.set()  # Gas detected
                print("Gas detected! 🚨")
            else:
                self.gas_flag.clear()  # No gas detected
            
            time.sleep(interval)

    def stop_monitoring(self):
        """Stops the background monitoring thread."""
        self._running = False
        if self._monitor_thread is not None:
            self._monitor_thread.join(timeout=2.0)  # Don't hang forever

    def cleanup(self):
        """Clean up the gas sensor."""
        """Clean up only the gas pins don't interfere between other sensors"""
        self.stop_monitoring() 
        self.gas_sensor.cleanup()