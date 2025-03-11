import RPi.GPIO as GPIO
import time
import serial

# Setup GPIO mode
GPIO.setmode(GPIO.BCM)

# Define sensor pins
TRIG = 23  # Trigger -> GPIO 23 (Pin 16)
ECHO = 24  # Echo -> GPIO 24 (Pin 18)

# Setup GPIO pins
GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)

# Define GSM serial communication
ser = serial.Serial("/dev/serial0", 9600, timeout=1)  # Serial communication with GSM
time.sleep(2)  # Wait for GSM module to be ready

# Distance threshold (Bin full at 10 cm)
THRESHOLD_DISTANCE = 50
DETECTION_TIME = 10  # Seconds before sending SMS

def measure_distance():
    GPIO.output(TRIG, True)
    time.sleep(0.00001)
    GPIO.output(TRIG, False)

    start_time, stop_time = 0, 0
    timeout = time.time() + 2  # Set a 2-second timeout

    while GPIO.input(ECHO) == 0:
        start_time = time.time()
        if time.time() > timeout:
            print("⚠️ ECHO not responding")
            return None

    while GPIO.input(ECHO) == 1:
        stop_time = time.time()
        if time.time() > timeout:
            print("⚠️ No response from sensor")
            return None

    elapsed_time = stop_time - start_time
    distance = (elapsed_time * 34300) / 2  # Convert time to cm
    return round(distance, 2)

def send_sms():
    phone_number = "+639688604302"  # 🔴 Change this to the recipient's number
    message = " Bin is full! Please empty it."

    print("📡 Sending SMS...")

    ser.write(b'AT+CMGF=1\r')  # Set SMS mode
    time.sleep(1)
    ser.write(b'AT+CMGS="' + phone_number.encode() + b'"\r')
    time.sleep(1)
    ser.write(message.encode() + b"\x1A")  # Send message
    time.sleep(3)

    print("✅ SMS sent!")

# Monitor the bin status
print("📡 Monitoring bin status...")

try:
    bin_full_time = None  # Start time when bin is detected as full

    while True:
        distance = measure_distance()

        if distance and distance < THRESHOLD_DISTANCE:
            print(f"⚠️ Bin is full! Distance: {distance} cm")

            if bin_full_time is None:
                bin_full_time = time.time()  # Start detection timer

            elif time.time() - bin_full_time >= DETECTION_TIME:
                send_sms()  # Send SMS alert
                bin_full_time = None  # Reset timer

        else:
            bin_full_time = None  # Reset if bin is not full
            print(f"✅ Bin not full. Distance: {distance} cm")

        time.sleep(1)

except KeyboardInterrupt:
    print("\n⛔ Stopping...")
    GPIO.cleanup()
