import RPi.GPIO as GPIO

class MetalDetector:
    def __init__(self, d0_pin=26, mode=GPIO.BCM):
        self.d0_pin = d0_pin
        GPIO.setmode(mode)
        # Active-low: sensor pulls D0 LOW when metal is detected
        # pull_up_down=GPIO.PUD_UP enables the internal pull-up resistor
        GPIO.setup(self.d0_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    def detect_metal(self):
        # Active-low: return True when pin is LOW (metal detected)
        return GPIO.input(self.d0_pin) == GPIO.LOW

    def cleanup(self):
        pass
