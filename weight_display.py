import I2C_LCD_driver
import time
from hx711 import HX711
import RPi.GPIO as GPIO

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

def read_weight():
    """ Reads weight from HX711 and updates the LCD """
    lcd.lcd_clear()
    lcd.lcd_display_string("Measuring...", 1)
    time.sleep(1)

    try:
        while True:
            weight = hx.get_weight(5)  # Read weight (average 5 readings)
            if weight < 0:
                weight = 0  # Prevent negative values

            lcd.lcd_clear()
            lcd.lcd_display_string("Weight:", 1)
            lcd.lcd_display_string(f"{weight:.2f} g", 2)
            time.sleep(1)

    except KeyboardInterrupt:
        print("\nExiting... Cleaning up GPIO.")
        GPIO.cleanup()  # Release GPIO pins properly
        lcd.lcd_clear()
        lcd.lcd_display_string("Goodbye!", 1)
        time.sleep(2)
        lcd.lcd_clear()

# Run function
read_weight()
