import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))


# LED snippets
##############

# Set all device lighting to red
from logiledpy import led
import time
import ctypes

print("Setting all device lighting to red...")
led.logi_led_init()
time.sleep(1)  # Give the SDK a second to initialize
led.logi_led_set_lighting(100, 0, 0)
input("Press enter to shutdown SDK...")
led.logi_led_shutdown()

# If you prefer the c/c++ style you can use the DLL directly
print("Setting all device lighting to green...")
led.led_dll.LogiLedInit()
time.sleep(1)  # Give the SDK a second to initialize
led.led_dll.LogiLedSetLighting(ctypes.c_int(0), ctypes.c_int(100), ctypes.c_int(0))
input("Press enter to shutdown SDK...")
led.led_dll.LogiLedShutdown()
