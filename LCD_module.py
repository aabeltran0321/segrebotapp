
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