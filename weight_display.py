import I2C_LCD_driver
import time
from hx711 import HX711
import RPi.GPIO as GPIO
from scheduler import Scheduler

# Setup GPIO
GPIO.setwarnings(False)
GPIO.cleanup()

# Initialize LCD
lcd = I2C_LCD_driver.lcd()

# Initialize HX711 with the correct pins
hx = HX711(dout=5, pd_sck=6)  # Change GPIO pins if needed

# **Step 1: Calibration (Find the right reference unit)**
hx.set_reference_unit(200)  # Change this value after calibration
hx.reset()
hx.tare()  # Set zero weight before measurement

sch1 = Scheduler(1000)
counter = 0
def read_weight():
    """ Reads weight from HX711 and updates the LCD """
    lcd.lcd_clear()
    lcd.lcd_display_string("Measuring...", 1)
    time.sleep(1)

    try:
        while True:
            if sch1.Event():
                weight = hx.get_weight(5)  # Read weight (average 5 readings)
                if weight < 0:
                    weight = 0  # Prevent negative values

                lcd.lcd_clear()
                lcd.lcd_display_string("Weight:", 1)
                lcd.lcd_display_string(f"{weight:.2f} g", 2)
                counter +=1

                if counter == 5:
                    return weight
            

    except:
        pass

    return 0
        
if __name__ == "__main__":
    # Run function
    read_weight()
