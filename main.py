from config import *
from tflite_images_detection import detection_process, framers
from camera_module import camera_select,cv2
from scheduler import Scheduler
from weight_display import read_weight, lcd
from ultrasonic_test import measure_distance, THRESHOLD_DISTANCE, DETECTION_TIME, send_sms
import time
import requests
import random
import string

def generate_code(length=6):
    """Generate a random alphanumeric string."""
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

def send_request(points):
    code1 = generate_code()
    """Send a POST request with a generated code and input points."""
    url = "https://bigboysautomation.pythonanywhere.com/segrebot/rewards"
    data = {
        "code": code1,
        "points": points
    }

    response = requests.post(url, json=data)
    return response.status_code, response.json(), code1 

cap = camera_select(cam_source)
sch1 = Scheduler(1000)
sch2 = Scheduler(2000)
counter = 0
running = False


while running:
    #camera process
    lcd.lcd_clear()
    lcd.lcd_display_string("Welcome!", 1)
    lcd.lcd_display_string(f"", 2)
    while True:
        try:
            ret, frame = cap.read()
        except:
            frame = cap.capture_array()
        if sch1.Event():
            frame, boxes, classes, scores=detection_process(frame)
            frame, className = framers(frame, boxes,classes,scores)

            if className:
                print(className)
                break

        cv2.imshow("frame", frame)
        cv2.waitKey(1)

    lcd.lcd_clear()
    lcd.lcd_display_string("Classification:", 1)
    lcd.lcd_display_string(f"{className}", 2)


    cv2.imshow("frame", frame)
    cv2.waitKey(3000)
    cv2.destroyAllWindows()

    # weight process
    official_weight = 0

    while official_weight == 0 :
        official_weight = read_weight()

    stats, response, code1 = send_request(official_weight*points_per_gram)

    lcd.lcd_clear()
    lcd.lcd_display_string(f"Weight: {official_weight:.2f} g", 1)
    lcd.lcd_display_string(f"Code: {code1}", 2)
    
    time.sleep(5)

    #servo motor


    #trash height
    bin_full_time = None  # Start time when bin is detected as full
    count = 0
    lcd.lcd_clear()
    lcd.lcd_display_string("Checking Trash Height", 1)
    lcd.lcd_display_string(f"{className}", 2)
    while True:
        distance = measure_distance()

        if distance and distance < THRESHOLD_DISTANCE:
            print(f"⚠️ Bin is full! Distance: {distance} cm")

            

            if bin_full_time is None:
                bin_full_time = time.time()  # Start detection timer

            elif time.time() - bin_full_time >= DETECTION_TIME:
                send_sms()  # Send SMS alert
                bin_full_time = None  # Reset timer
                lcd.lcd_clear()
                lcd.lcd_display_string("Bin is full!", 1)
                lcd.lcd_display_string(f"{className}", 2)
                break

        else:
            bin_full_time = None  # Reset if bin is not full
            print(f"✅ Bin not full. Distance: {distance} cm")

            count +=1

            if count ==5:
                count = 0
                lcd.lcd_clear()
                lcd.lcd_display_string("Bin is not full!", 1)
                lcd.lcd_display_string(f"{distance} cm", 2)
                break

        time.sleep(1)


        

