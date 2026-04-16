import RPi.GPIO as GPIO
import time

# --- PINS CONFIGURATION ---
TRIG = 24
ECHO = 25

def setup_sensor():
    """Initializes the GPIO pins for the HC-SR04 sensor."""
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(TRIG, GPIO.OUT)
    GPIO.setup(ECHO, GPIO.IN)
    GPIO.output(TRIG, False)
    print("Waiting for sensor to settle...")
    time.sleep(2)

def get_distance():
    """Measures the distance from the ultrasonic sensor."""
    # Ensure trigger is low
    GPIO.output(TRIG, False)
    time.sleep(0.01) # Short delay for stability

    # Send 10us pulse to trigger
    GPIO.output(TRIG, True)
    time.sleep(0.00001)
    GPIO.output(TRIG, False)

    # Listen for Echo pulse
    pulse_start = time.time()
    pulse_end = time.time()

    # Wait for echo to go high (start of pulse)
    timeout = time.time() + 1.0 # 1 second timeout
    while GPIO.input(ECHO) == 0:
        pulse_start = time.time()
        if pulse_start > timeout:
            return -1 # Timeout error

    # Wait for echo to go low (end of pulse)
    timeout = time.time() + 1.0
    while GPIO.input(ECHO) == 1:
        pulse_end = time.time()
        if pulse_end > timeout:
            return -1 # Timeout error

    # Pulse duration is the travel time (there and back)
    pulse_duration = pulse_end - pulse_start

    # Distance = (Speed of sound * time) / 2
    # Speed of sound is approx 34300 cm/s
    distance = pulse_duration * 17150
    distance = round(distance, 2)

    return distance

if __name__ == "__main__":
    try:
        setup_sensor()
        print("Starting Distance Measurement... Press Ctrl+C to stop.")
        
        while True:
            dist = get_distance()
            if dist == -1:
                print("Error: Sensor Timeout")
            else:
                print(f"Distance: {dist} cm")
            
            time.sleep(0.5) # Wait half a second before next reading

    except KeyboardInterrupt:
        print("\nMeasurement stopped by User")
    except Exception as e:
        print(f"\nAn error occurred: {e}")
    finally:
        GPIO.cleanup()
        print("GPIO Cleanup completed.")
