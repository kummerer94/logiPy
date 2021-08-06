import ctypes
import os
import platform
from enum import Enum, auto
from pathlib import Path
from typing import Union

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

        # It is best to use ProgramW6432: https://stackoverflow.com/a/51305013
        try:
            subpath_lgs = os.environ["ProgramW6432"]
        except KeyError:
            subpath_lgs = os.environ["ProgramFiles"]
        path_dll = Path(subpath_lgs) / subpath_dll
    else:
        path_dll = Path(path_dll)

    if path_dll.exists():
        return ctypes.cdll.LoadLibrary(str(path_dll))
    else:
        raise SDKNotFoundException(f"The SDK DLL was not found at {path_dll}")


try:
    led_dll = load_dll()
except SDKNotFoundException as exception_sdk:
    led_dll = None


class KeyType(Enum):
    scan = auto()
    hid = auto()
    quartz = auto()
    name = auto()


class LEDService:
    """Service implementation for the LED API."""

    dll: ctypes.CDLL

    def __init__(self, path_dll: Union[str, Path, None] = None) -> None:
        """Initializes the LED service and loads the necessary DLL.

        Parameters
        ----------
        path_dll : Union[str, Path], optional
            The path to the DLL, if None will try to find the DLL automatically.

        Raises
        ------
        SDKNotFoundException
            If the SDK DLL is not found.

        """
        self.dll = load_dll(path_dll=path_dll)

    def start(self) -> bool:
        """Initialize the LED API. This is a necessary step if you want to work with the API."""
        return bool(self.dll.LogiLedInit())

    def shutdown(self):
        """Shutdown the SDK for the thread."""
        return bool(self.led.LogiLedShutdown())

    def __enter__(self):
        """Context manager adaption."""
        self.start()

    def __exit__(self, type, value, traceback):
        """Context manager adaption."""
        self.shutdown()

    def set_target_device(self, target_device: int) -> bool:
        """Set the target device or device group that is affected by subsequent lighting calls.

        Parameters
        ----------
        target_device : int
            The target device or group.

        Returns
        -------
        bool
            Whether or not the device action worked.

        """
        target_device = ctypes.c_int(target_device)
        return bool(self.dll.LogiLedSetTargetDevice(target_device))

    def save_current_lighting(self) -> bool:
        """Save the current lighting that can be restored later."""
        return bool(self.dll.LogiLedSaveCurrentLighting())

    def restore_lighting(self) -> bool:
        """Restore the last saved lighting."""
        return bool(self.dll.LogiLedRestoreLighting())

    def flash_lighting(
        self, red: int, green: int, blue: int, duration: int, interval: int
    ) -> bool:
        """Flashes the lighing color of the combined RGB percentages over
        the specified millisecond duration and millisecond interval.
        Note that RGB ranges from 0-255, but this function ranges from 0-100.

        Parameters
        ----------
        red : int
            The red percentage, values from 0-100.
        green : int
            The green percentage, values from 0-100.
        blue : int
            The blue percentages, values from 0-100.
        duration : int
            The duration for the effect in ms, if 0 will go on until reset.
        interval : int
            The interval for the effect in ms.

        Returns
        -------
        bool
            Whether or not the flash instruction succeeded.

        """
        red = ctypes.c_int(red)
        green = ctypes.c_int(green)
        blue = ctypes.c_int(blue)
        duration = ctypes.c_int(duration)
        interval = ctypes.c_int(interval)
        return bool(self.dll.LogiLedFlashLighting(red, green, blue, duration, interval))

    def pulse_lighting(
        self, red: int, green: int, blue: int, duration: int, interval: int
    ) -> bool:
        """Pulses the lighting of the combined RGB percentages over the specified
        millisecond duration and interval.
        Note that RGB ranges from 0-255, but this function ranges from 0-100.

        Parameters
        ----------
        red : int
            The red percentages, values from 0-100.
        green : int
            The green percentages, values from 0-100.
        blue : int
            The blue percentages, values from 0-100.
        duration : int
            The duration for the effect in ms, if 0 will go on until reset.
        interval : int
            The interval for the effect in ms.

        Returns
        -------
        bool
            Whether or not the pulse instruction succeeded.
        """
        red = ctypes.c_int(red)
        green = ctypes.c_int(green)
        blue = ctypes.c_int(blue)
        duration = ctypes.c_int(duration)
        interval = ctypes.c_int(interval)
        return bool(self.dll.LogiLedPulseLighting(red, green, blue, duration, interval))

    def stop_effects(self) -> bool:
        """Stop all effects like pulse and flash."""
        return bool(self.dll.LogiLedStopEffects())

    def set_lighting_from_bitmap(self, bitmap: bytes) -> bool:
        """Sets the color of each key in a 21x6 rectangular area specified by the BGRA byte array bitmap.
        Each element corresponds to the physical location of each location of each key.
        Note that this function only applies to LOGI_DEVICETYPE_PERKEY_RGB devices.

        Parameters
        ----------
        bitmap : bytes
            The bitmap with the colors.

        Returns
        -------
        bool
            Whether or not the lighting action worked.

        """
        bitmap = ctypes.c_char_p(bitmap)
        return bool(self.dll.LogiLedSetLightingFromBitmap(bitmap))

    def set_lighting_for_key(
        self, key: int, key_type: KeyType, red: int, green: int, blue: int
    ) -> bool:
        """Sets the lighting to the color of the combined RGB percentages for the specified key code.
        Note that this function only applies to LOGI_DEVICETYPE_PERKEY_RGB devices.
        Note that RGB ranges from 0-255, but this function ranges from 0-100.

        Parameters
        ----------
        key : int
            The key.
        key_type : KeyType
            The type of the given key.
        red : int
            The red percentages, values from 0-100.
        green : int
            The green percentages, values from 0-100.
        blue : int
            The blue percentages, values from 0-100.

        Returns
        -------
        bool
            Whether or not the lighting action worked.

        """
        key = ctypes.c_int(key)
        red = ctypes.c_int(red)
        green = ctypes.c_int(green)
        blue = ctypes.c_int(blue)

        type_to_key = {
            KeyType.scan: self.dll.LogiLedSetLightingForKeyWithScanCode,
            KeyType.hid: self.dll.LogiLedSetLightingForKeyWithHidCode,
            KeyType.quartz: self.dll.LogiLedSetLightingForKeyWithQuartzCode,
            KeyType.name: self.dll.LogiLedLightingForKeyWithKeyName,
        }
        try:
            set_lighting = type_to_key[key_type]
        except KeyError:
            return False
        return bool(set_lighting(key, red, green, blue))

    def save_lighting_for_key(self, key_name: int) -> bool:
        """Saves the current lighting for the specified key.
        Note that this function only applies to LOGI_DEVICETYPE_PERKEY_RGB devices.

        Parameters
        ----------
        key_name : int
            The name of the key.

        Returns
        -------
        bool
            Whether or not the save succeeded.

        """
        key_name = ctypes.c_int(key_name)
        return bool(self.dll.LogiLedSaveLightingForKey(key_name))

    def restore_lighting_for_key(self, key_name: int) -> bool:
        """Restores the last saved lighting for the given key.
        Note that this function only applies to LOGI_DEVICETYPE_PERKEY_RGB devices.

        Parameters
        ----------
        key_name : int
            The name of the key.

        Returns
        -------
        bool
            Whether or not the restoring succeeded.

        """
        key_name = ctypes.c_int(key_name)
        return bool(self.dll.LogiLedRestoreLightingForKey(key_name))

    def flash_single_key(
        self, key_name: int, red: int, green: int, blue: int, duration: int, interval: int
    ) -> bool:
        """Flashes the lighting color of the combined RGB percentages over the specified millisecond
        duration and interval for the key with the given name.
        Note that this function only applies to LOGI_DEVICETYPE_PERKEY_RGB devices.
        Note that RGB ranges from 0-255, but this function ranges from 0-100.

        Parameters
        ----------
        key_name : int
            The name of the key.
        red : int
            The red percentages, values from 0-100.
        green : int
            The green percentages, values from 0-100.
        blue : int
            The blue percentages, values from 0-100.
        duration : int
            The duration for the effect in ms, if 0 will go on until reset.
        interval : int
            The interval for the effect in ms.

        Returns
        -------
        bool
            Whether or not the flash action succeeded.

        """
        key_name = ctypes.c_int(key_name)
        red = ctypes.c_int(red)
        green = ctypes.c_int(green)
        blue = ctypes.c_int(blue)
        duration = ctypes.c_int(duration)
        interval = ctypes.c_int(interval)
        return bool(self.dll.LogiLedFlashSingleKey(key_name, red, green, blue, duration, interval))

    def pulse_single_key(
        self,
        key_name: int,
        red_start: int,
        green_start: int,
        blue_start: int,
        duration: int,
        is_infinite: bool = False,
        red_end: int = 0,
        green_end: int = 0,
        blue_end: int = 0,
    ) -> bool:
        """Pulses the lighting color of the combined RGB percentages over the specified millisecond
        duration for the key with the given name. The color will gradually change from the starting color
        to the ending color. If no ending color is specified, the ending color will be black.
        The effect will stop after one interval unless is_infinite is set to True.

        Note that this function only applies to LOGI_DEVICETYPE_PERKEY_RGB devices.
        Note that RGB ranges from 0-255, but this function ranges from 0-100.

        Parameters
        ----------
        key_name : int
            The name of the key.
        red_start : int
            The starting red percentage, values from 0-100.
        green_start : int
            The starting green percentage, values from 0-100.
        blue_start : int
            The starting blue percentage, values from 0-100.
        duration : int
            The duration for the effect in ms, if 0 will go on until reset.
        is_infinite : bool, optional
            Set this to True if you want the pulse to go on. By default False.
        red_end : int
            The ending red percentage, values from 0-100. By default 0.
        green_end : int
            The ending green percentage, values from 0-100. By default 0.
        blue_end : int
            The ending blue percentage, values from 0-100. By default 0.

        Returns
        -------
        bool
            Whether or not the pulse action succeeded.

        """
        key_name = ctypes.c_int(key_name)
        red_start = ctypes.c_int(red_start)
        green_start = ctypes.c_int(green_start)
        blue_start = ctypes.c_int(blue_start)
        red_end = ctypes.c_int(red_end)
        green_end = ctypes.c_int(green_end)
        blue_end = ctypes.c_int(blue_end)
        duration = ctypes.c_int(duration)
        is_infinite = ctypes.c_bool(is_infinite)
        return bool(
            self.dll.LogiLedPulseSingleKey(
                key_name,
                red_start,
                green_start,
                blue_start,
                red_end,
                green_end,
                blue_end,
                duration,
                is_infinite,
            )
        )

    def stop_effects_on_key(self, key_name: int) -> bool:
        """Stop all effects on the given key.

        Parameters
        ----------
        key_name : int
            The key name.

        Returns
        -------
        bool
            Whether or not the stop action succeeded.

        """
        key_name = ctypes.c_int(key_name)
        return bool(self.dll.LogiLedStopEffectsOnKey(key_name))


def logi_led_get_config_option_number(key, default=0):
    """get the default value for the key as a number. if the call fails, the return value is None.

    for example, get the low health threshold:
     logi_led_get_config_option_number('health/low_health_threshold', 20.0)"""
    if led_dll:
        key = ctypes.c_wchar_p(key)
        default = ctypes.c_double(default)
        if led_dll.LogiGetConfigOptionNumber(key, ctypes.pointer(default), _LOGI_SHARED_SDK_LED):
            return default.value
    return None


def logi_led_get_config_option_bool(key, default=False):
    """get the default value for the key as a bool. if the call fails, the return value is None.

    for example, check if the effect is enabled:
     logi_led_get_config_option_bool('health/pulse_on_low', True)"""
    if led_dll:
        key = ctypes.c_wchar_p(key)
        default = ctypes.c_bool(default)
        if led_dll.LogiGetConfigOptionBool(key, ctypes.pointer(default), _LOGI_SHARED_SDK_LED):
            return default.value
    return None


def logi_led_get_config_option_color(key, *args):
    """get the default value for the key as a color. if the call fails, the return value is None.
     note this function can either be called with red_percentage, green_percentage, and blue_percentage or with the logi_led Color object.

    for example, get the low health color:
     logi_led_get_config_option_color('health/pulse_color', 100, 0, 0)
     logi_led_get_config_option_color('health/pulse_color', Color('red'))
     logi_led_get_config_option_color('health/pulse_color', Color('#ff0000'))
     logi_led_get_config_option_color('health/pulse_color', Color(255, 0, 0))"""
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


def logi_led_get_config_option_key_input(key, default=""):
    """get the default value for the key as a key input. if the call fails, the return value is None.

    for example, get the primary ability key input:
     logi_led_get_config_option_key_input('abilities/primary', 'A')"""
    if led_dll:
        key = ctypes.c_wchar_p(key)
        default_key = ctypes.create_string_buffer(256)
        default_key.value = default
        if led_dll.LogiGetConfigOptionKeyInput(key, default_key, _LOGI_SHARED_SDK_LED):
            return str(default_key.value)
    return None


def logi_led_set_config_option_label(key, label):
    """set the label for a key.

    for example, label 'health/pulse_on_low' as 'Health - Pulse on Low':
     logi_led_set_config_option_label('health', 'Health')
     logi_led_set_config_option_label('health/pulse_on_low', 'Pulse on Low')"""
    if led_dll:
        key = ctypes.c_wchar_p(key)
        label = ctypes.c_wchar_p(label)
        return bool(led_dll.LogiSetConfigOptionLabel(key, label, _LOGI_SHARED_SDK_LED))
    else:
        return False
