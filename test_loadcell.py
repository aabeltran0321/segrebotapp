import time
import sys
from hx711 import HX711  

# Define GPIO Pins
DT = 5   # Data Pin (DOUT)
SCK = 6  # Clock Pin (SCK)

hx = HX711(DT, SCK)
hx.set_reading_format("MSB", "MSB")  # Adjust if necessary

# Set reference unit (calibrate later)
hx.set_reference_unit(1)  
hx.reset()
hx.tare()  # Reset the scale to zero

print("Place weight on the load cell...")

try:
    while True:
        weight = hx.get_weight(5)  # Get average of 5 readings
        print(f"Weight: {weight:.2f} g")
        hx.power_down()
        hx.power_up()
        time.sleep(1)

except KeyboardInterrupt:
    print("Exiting...")
    hx.power_down()
    sys.exit()
