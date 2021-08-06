import ctypes
import os
import platform
from pathlib import Path

from color import Color
from keys import *

LOGI_LED_BITMAP_WIDTH = 21
LOGI_LED_BITMAP_HEIGHT = 6
LOGI_LED_BITMAP_BYTES_PER_KEY = 4

LOGI_LED_BITMAP_SIZE = (
    LOGI_LED_BITMAP_WIDTH * LOGI_LED_BITMAP_HEIGHT * LOGI_LED_BITMAP_BYTES_PER_KEY
)

LOGI_LED_DURATION_INFINITE = 0

LOGI_DEVICETYPE_MONOCHROME_ORD = 0
LOGI_DEVICETYPE_RGB_ORD = 1
LOGI_DEVICETYPE_PERKEY_RGB_ORD = 2

LOGI_DEVICETYPE_MONOCHROME = 1 << LOGI_DEVICETYPE_MONOCHROME_ORD
LOGI_DEVICETYPE_RGB = 1 << LOGI_DEVICETYPE_RGB_ORD
LOGI_DEVICETYPE_PERKEY_RGB = 1 << LOGI_DEVICETYPE_PERKEY_RGB_ORD

LOGI_DEVICETYPE_ALL = LOGI_DEVICETYPE_MONOCHROME | LOGI_DEVICETYPE_RGB | LOGI_DEVICETYPE_PERKEY_RGB


# Required Globals
_LOGI_SHARED_SDK_LED = ctypes.c_int(1)


class SDKNotFoundException(Exception):
    pass


def load_dll(path_dll=None):
    if not path_dll:
        bitness = "x86" if platform.architecture()[0] == "32bit" else "x64"
        subpath_dll = Path(f"/Logitech Gaming Software/SDK/LED/{bitness}/LogitechLed.dll")
        try:
            subpath_lgs = os.environ["ProgramW6432"]
        except KeyError:
            subpath_lgs = os.environ["ProgramFiles"]
        path_dll = Path(subpath_lgs) / subpath_dll
    if path_dll.exists():
        return ctypes.cdll.LoadLibrary(str(path_dll))
    else:
        raise SDKNotFoundException(f"The SDK DLL was not found at {path_dll}")


try:
    led_dll = load_dll()
except SDKNotFoundException as exception_sdk:
    led_dll = None


# Wrapped SDK Functions
def logi_led_init():
    """initializes the sdk for the current thread."""
    if led_dll:
        return bool(led_dll.LogiLedInit())
    else:
        return False


def logi_led_set_target_device(target_device):
    """sets the target device or device group that is affected by the subsequent lighting calls."""
    if led_dll:
        target_device = ctypes.c_int(target_device)
        return bool(led_dll.LogiLedSetTargetDevice(target_device))
    else:
        return False


def logi_led_save_current_lighting():
    """saves the current lighting that can be restored later."""
    if led_dll:
        return bool(led_dll.LogiLedSaveCurrentLighting())
    else:
        return False


def logi_led_restore_lighting():
    """restores the last saved lighting."""
    if led_dll:
        return bool(led_dll.LogiLedRestoreLighting())
    else:
        return False


def logi_led_set_lighting(red_percentage, green_percentage, blue_percentage):
    """sets the lighting to the color of the combined RGB percentages. note that RGB ranges from 0-255, but this function ranges from 0-100."""
    if led_dll:
        red_percentage = ctypes.c_int(red_percentage)
        green_percentage = ctypes.c_int(green_percentage)
        blue_percentage = ctypes.c_int(blue_percentage)
        return bool(led_dll.LogiLedSetLighting(red_percentage, green_percentage, blue_percentage))
    else:
        return False


def logi_led_flash_lighting(
    red_percentage, green_percentage, blue_percentage, ms_duration, ms_interval
):
    """flashes the lighting color of the combined RGB percentages over the specified millisecond duration and millisecond interval.
    specifying a duration of 0 will cause the effect to be infinite until reset. note that RGB ranges from 0-255, but this function ranges from 0-100."""
    if led_dll:
        red_percentage = ctypes.c_int(red_percentage)
        green_percentage = ctypes.c_int(green_percentage)
        blue_percentage = ctypes.c_int(blue_percentage)
        ms_duration = ctypes.c_int(ms_duration)
        ms_interval = ctypes.c_int(ms_interval)
        return bool(
            led_dll.LogiLedFlashLighting(
                red_percentage,
                green_percentage,
                blue_percentage,
                ms_duration,
                ms_interval,
            )
        )
    else:
        return False


def pulse_lighting(
    red_percentage, green_percentage, blue_percentage, ms_duration, ms_interval
):
    """pulses the lighting color of the combined RGB percentages over the specified millisecond duration and millisecond interval.
    specifying a duration of 0 will cause the effect to be infinite until reset. note that RGB ranges from 0-255, but this function ranges from 0-100."""
    if led_dll:
        red_percentage = ctypes.c_int(red_percentage)
        green_percentage = ctypes.c_int(green_percentage)
        blue_percentage = ctypes.c_int(blue_percentage)
        ms_duration = ctypes.c_int(ms_duration)
        ms_interval = ctypes.c_int(ms_interval)
        return bool(
            led_dll.LogiLedPulseLighting(
                red_percentage,
                green_percentage,
                blue_percentage,
                ms_duration,
                ms_interval,
            )
        )
    else:
        return False


def stop_effects():
    """stops the pulse and flash effects."""
    if led_dll:
        return bool(led_dll.LogiLedStopEffects())
    else:
        return False


def set_lighting_from_bitmap(bitmap):
    """sets the color of each key in a 21x6 rectangular area specified by the BGRA byte array bitmap. each element corresponds to the physical location of each key.
    note that the color bit order is BGRA rather than standard RGBA bit order. this function only applies to LOGI_DEVICETYPE_PERKEY_RGB devices."""
    if led_dll:
        bitmap = ctypes.c_char_p(bitmap)
        return bool(led_dll.LogiLedSetLightingFromBitmap(bitmap))
    else:
        return False


def set_lighting_for_key_with_scan_code(
    key_code, red_percentage, green_percentage, blue_percentage
):
    """sets the lighting to the color of the combined RGB percentages for the specified key code. note that RGB ranges from 0-255, but this function ranges from 0-100.
    this function only applies to LOGI_DEVICETYPE_PERKEY_RGB devices."""
    if led_dll:
        key_code = ctypes.c_int(key_code)
        red_percentage = ctypes.c_int(red_percentage)
        green_percentage = ctypes.c_int(green_percentage)
        blue_percentage = ctypes.c_int(blue_percentage)
        return bool(
            led_dll.LogiLedSetLightingForKeyWithScanCode(
                key_code, red_percentage, green_percentage, blue_percentage
            )
        )
    else:
        return False


def set_lighting_for_key_with_hid_code(
    key_code, red_percentage, green_percentage, blue_percentage
):
    """sets the lighting to the color of the combined RGB percentages for the specified key code. note that RGB ranges from 0-255, but this function ranges from 0-100.
    this function only applies to LOGI_DEVICETYPE_PERKEY_RGB devices."""
    if led_dll:
        key_code = ctypes.c_int(key_code)
        red_percentage = ctypes.c_int(red_percentage)
        green_percentage = ctypes.c_int(green_percentage)
        blue_percentage = ctypes.c_int(blue_percentage)
        return bool(
            led_dll.LogiLedSetLightingForKeyWithHidCode(
                key_code, red_percentage, green_percentage, blue_percentage
            )
        )
    else:
        return False


def set_lighting_for_key_with_quartz_code(
    key_code, red_percentage, green_percentage, blue_percentage
):
    """sets the lighting to the color of the combined RGB percentages for the specified key code. note that RGB ranges from 0-255, but this function ranges from 0-100.
    this function only applies to LOGI_DEVICETYPE_PERKEY_RGB devices."""
    if led_dll:
        key_code = ctypes.c_int(key_code)
        red_percentage = ctypes.c_int(red_percentage)
        green_percentage = ctypes.c_int(green_percentage)
        blue_percentage = ctypes.c_int(blue_percentage)
        return bool(
            led_dll.LogiLedSetLightingForKeyWithQuartzCode(
                key_code, red_percentage, green_percentage, blue_percentage
            )
        )
    else:
        return False


def set_lighting_for_key_with_key_name(
    key_name, red_percentage, green_percentage, blue_percentage
):
    """sets the lighting to the color of the combined RGB percentages for the specified key name. note that RGB ranges from 0-255, but this function ranges from 0-100.
    this function only applies to LOGI_DEVICETYPE_PERKEY_RGB devices."""
    if led_dll:
        key_name = ctypes.c_int(key_name)
        red_percentage = ctypes.c_int(red_percentage)
        green_percentage = ctypes.c_int(green_percentage)
        blue_percentage = ctypes.c_int(blue_percentage)
        return bool(
            led_dll.LogiLedSetLightingForKeyWithKeyName(
                key_name, red_percentage, green_percentage, blue_percentage
            )
        )
    else:
        return False


def save_lighting_for_key(key_name):
    """saves the current lighting for the specified key name that can be restored later. this function only applies to LOGI_DEVICETYPE_PERKEY_RGB devices."""
    if led_dll:
        key_name = ctypes.c_int(key_name)
        return bool(led_dll.LogiLedSaveLightingForKey(key_name))
    else:
        return False


def restore_lighting_for_key(key_name):
    """restores the last saved lighting for the specified key name. this function only applies to LOGI_DEVICETYPE_PERKEY_RGB devices."""
    if led_dll:
        key_name = ctypes.c_int(key_name)
        return bool(led_dll.LogiLedRestoreLightingForKey(key_name))
    else:
        return False


def flash_single_key(
    key_name,
    red_percentage,
    green_percentage,
    blue_percentage,
    ms_duration,
    ms_interval,
):
    """flashes the lighting color of the combined RGB percentages over the specified millisecond duration and millisecond interval for the specified key name.
    specifying a duration of 0 will cause the effect to be infinite until reset. note that RGB ranges from 0-255, but this function ranges from 0-100.
    this function only applies to LOGI_DEVICETYPE_PERKEY_RGB devices."""
    if led_dll:
        key_name = ctypes.c_int(key_name)
        red_percentage = ctypes.c_int(red_percentage)
        green_percentage = ctypes.c_int(green_percentage)
        blue_percentage = ctypes.c_int(blue_percentage)
        ms_duration = ctypes.c_int(ms_duration)
        ms_interval = ctypes.c_int(ms_interval)
        return bool(
            led_dll.LogiLedFlashSingleKey(
                key_name,
                red_percentage,
                green_percentage,
                blue_percentage,
                ms_duration,
                ms_interval,
            )
        )
    else:
        return False


def pulse_single_key(
    key_name,
    red_percentage_start,
    green_percentage_start,
    blue_percentage_start,
    ms_duration,
    is_infinite=False,
    red_percentage_end=0,
    green_percentage_end=0,
    blue_percentage_end=0,
):
    """pulses the lighting color of the combined RGB percentages over the specified millisecond duration for the specified key name.
    the color will gradually change from the starting color to the ending color. if no ending color is specified, the ending color will be black.
    the effect will stop after one interval unless is_infinite is set to True. note that RGB ranges from 0-255, but this function ranges from 0-100.
    this function only applies to LOGI_DEVICETYPE_PERKEY_RGB devices."""
    if led_dll:
        key_name = ctypes.c_int(key_name)
        red_percentage_start = ctypes.c_int(red_percentage_start)
        green_percentage_start = ctypes.c_int(green_percentage_start)
        blue_percentage_start = ctypes.c_int(blue_percentage_start)
        red_percentage_end = ctypes.c_int(red_percentage_end)
        green_percentage_end = ctypes.c_int(green_percentage_end)
        blue_percentage_end = ctypes.c_int(blue_percentage_end)
        ms_duration = ctypes.c_int(ms_duration)
        is_infinite = ctypes.c_bool(is_infinite)
        return bool(
            led_dll.LogiLedPulseSingleKey(
                key_name,
                red_percentage_start,
                green_percentage_start,
                blue_percentage_start,
                red_percentage_end,
                green_percentage_end,
                blue_percentage_end,
                ms_duration,
                is_infinite,
            )
        )
    else:
        return False


def stop_effects_on_key(key_name):
    """stops the pulse and flash effects on a single key."""
    if led_dll:
        key_name = ctypes.c_int(key_name)
        return bool(led_dll.LogiLedStopEffectsOnKey(key_name))
    else:
        return False


def shutdown():
    """shutdowns the SDK for the thread."""
    if led_dll:
        return bool(led_dll.LogiLedShutdown())
    else:
        return False


def get_config_option_number(key, default=0):
    """get the default value for the key as a number. if the call fails, the return value is None.

    for example, get the low health threshold:
     get_config_option_number('health/low_health_threshold', 20.0)"""
    if led_dll:
        key = ctypes.c_wchar_p(key)
        default = ctypes.c_double(default)
        if led_dll.LogiGetConfigOptionNumber(key, ctypes.pointer(default), _LOGI_SHARED_SDK_LED):
            return default.value
    return None


def get_config_option_bool(key, default=False):
    """get the default value for the key as a bool. if the call fails, the return value is None.

    for example, check if the effect is enabled:
     get_config_option_bool('health/pulse_on_low', True)"""
    if led_dll:
        key = ctypes.c_wchar_p(key)
        default = ctypes.c_bool(default)
        if led_dll.LogiGetConfigOptionBool(key, ctypes.pointer(default), _LOGI_SHARED_SDK_LED):
            return default.value
    return None


def get_config_option_color(key, *args):
    """get the default value for the key as a color. if the call fails, the return value is None.
     note this function can either be called with red_percentage, green_percentage, and blue_percentage or with the logi_led Color object.

    for example, get the low health color:
     get_config_option_color('health/pulse_color', 100, 0, 0)
     get_config_option_color('health/pulse_color', Color('red'))
     get_config_option_color('health/pulse_color', Color('#ff0000'))
     get_config_option_color('health/pulse_color', Color(255, 0, 0))"""
    if led_dll:
        key = ctypes.c_wchar_p(key)
        default = None
        red_percentage = 0
        green_percentage = 0
        blue_percentage = 0
        if isinstance(args[0], Color):
            default = args[0]
        else:
            red_percentage = args[0]
            green_percentage = args[1]
            blue_percentage = args[2]
        if default:
            red = ctypes.c_int(default.red)
            green = ctypes.c_int(default.green)
            blue = ctypes.c_int(default.blue)
        else:
            red = ctypes.c_int(int((red_percentage / 100.0) * 255))
            green = ctypes.c_int(int((green_percentage / 100.0) * 255))
            blue = ctypes.c_int(int((blue_percentage / 100.0) * 255))
        if led_dll.LogiGetConfigOptionColor(
            key,
            ctypes.pointer(red),
            ctypes.pointer(green),
            ctypes.pointer(blue),
            _LOGI_SHARED_SDK_LED,
        ):
            return Color(red.value, green.value, blue.value)
    return None


def get_config_option_key_input(key, default=""):
    """get the default value for the key as a key input. if the call fails, the return value is None.

    for example, get the primary ability key input:
     get_config_option_key_input('abilities/primary', 'A')"""
    if led_dll:
        key = ctypes.c_wchar_p(key)
        default_key = ctypes.create_string_buffer(256)
        default_key.value = default
        if led_dll.LogiGetConfigOptionKeyInput(key, default_key, _LOGI_SHARED_SDK_LED):
            return str(default_key.value)
    return None


def set_config_option_label(key, label):
    """set the label for a key.

    for example, label 'health/pulse_on_low' as 'Health - Pulse on Low':
     set_config_option_label('health', 'Health')
     set_config_option_label('health/pulse_on_low', 'Pulse on Low')"""
    if led_dll:
        key = ctypes.c_wchar_p(key)
        label = ctypes.c_wchar_p(label)
        return bool(led_dll.LogiSetConfigOptionLabel(key, label, _LOGI_SHARED_SDK_LED))
    else:
        return False
