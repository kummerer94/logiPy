import ctypes
import os
import platform
from enum import Enum, auto
from pathlib import Path
from typing import Optional, Union

from .color import Color
from .keys import *

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


class KeyType(Enum):
    scan = auto()
    hid = auto()
    quartz = auto()
    name = auto()


class LEDService:
    """Service implementation for the LED API."""

    dll: ctypes.CDLL
    use_legacy_dll: bool = True

    def __init__(
        self, path_dll: Union[str, Path, None] = None, use_legacy_dll: bool = True
    ) -> None:
        """Initializes the LED service and loads the necessary DLL.

        Parameters
        ----------
        path_dll : Union[str, Path], optional
            The path to the DLL, if None will try to find the DLL automatically.
        use_legacy_dll : bool, optional
            Use the legacy DLL included in the Logitech G Hub.

        Raises
        ------
        SDKNotFoundException
            If the SDK DLL is not found.

        """
        self.dll = self.load_dll(path_dll=path_dll)
        self.use_legacy_dll = use_legacy_dll

    def start(self) -> bool:
        """Initialize the LED API. This is a necessary step if you want to work with the API."""
        return bool(self.dll.LogiLedInit())

    def shutdown(self):
        """Shutdown the SDK for the thread."""
        return bool(self.dll.LogiLedShutdown())

    def __enter__(self) -> "LEDService":
        """Context manager adaption."""
        self.start()
        return self

    def __exit__(self, type, value, traceback) -> None:
        """Context manager adaption."""
        self.shutdown()

    def load_dll(self, path_dll: Optional[Union[str, Path]] = None) -> ctypes.CDLL:
        """Load the DLL."""
        if not path_dll:
            bitness = "x86" if platform.architecture()[0] == "32bit" else "x64"
            if self.use_legacy_dll:
                subpath_dll = f"LGHUB/sdk_legacy_led_{bitness}.dll"
            else:
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

    def get_config_option_number(self, key: str, default: int = 0) -> Optional[float]:
        """Get the default value for the configuration key as a float.
        If the call fails, the return value is None.

        Parameters
        ----------
        key : str
            The configuration key, like 'health/low_health_threshold'.
        default : int, optional
            The default value for the configuration, by default 0.

        Returns
        -------
        Optional[float]
            The value for the configuration key or if the call fails None.

        """
        key = ctypes.c_wchar_p(key)
        default = ctypes.c_couble(default)
        if self.dll.LogiGetConfigOptionNumber(key, ctypes.pointer(default), _LOGI_SHARED_SDK_LED):
            return default.value
        return None

    def get_config_option_bool(self, key: str, default: bool = False) -> Optional[bool]:
        """Get the default value for the configuration key as a bool.
        If the call fails, the return value is None.

        Parameters
        ----------
        key : str
            The configuration key, like 'health/pulse_on_low'.
        default : bool, optional
            The default value for the configuration, by default False

        Returns
        -------
        Optional[bool]
            The value for the configuration key or if the call fails None.

        """
        key = ctypes.c_wchar_p(key)
        default = ctypes.c_bool(default)
        if self.dll.LogiGetConfigOptionBool(key, ctypes.pointer(default), _LOGI_SHARED_SDK_LED):
            return default.value
        return None

    def get_config_option_color(self, key: str, *args) -> Optional[Color]:
        """Get the default value for the configuration key as a color.
        If the call fails, the return value is None.
        Note: you can either call this function with rgb percentage values or with a Color object.

        Parameters
        ----------
        key : str
            The configuration key.

        Returns
        -------
        Optional[Color]
            The color for the configuration key or if the call fails None.

        """
        key = ctypes.c_wchar_p(key)
        default = None
        red, green, blue = 0, 0, 0
        if isinstance(args[0], Color):
            default = args[0]
            red = ctypes.c_int(default.red)
            green = ctypes.c_int(default.green)
            blue = ctypes.c_int(default.blue)
        else:
            red_pct, green_pct, blue_pct = args[0], args[1], args[2]
            red = ctypes.c_int(int((red_pct / 100) * 255))
            green = ctypes.c_int(int((green_pct / 100) * 255))
            blue = ctypes.c_int(int((blue_pct / 100) * 255))

        if self.dll.LogiGetConfigOptionColor(
            key,
            ctypes.pointer(red),
            ctypes.pointer(green),
            ctypes.pointer(blue),
            _LOGI_SHARED_SDK_LED,
        ):
            return Color(red.value, green.value, blue.value)
        return None

    def get_config_option_key_input(self, key: str, default: str = "") -> Optional[str]:
        """Get the default value for the key as a input key.
        If the call fails, the return value is None.

        Parameters
        ----------
        key : str
            The configuration key, e.g. 'abilities/primary'.
        default : str, optional
            The default value for this configuration key, by default "".

        Returns
        -------
        Optional[str]
            The value for the configuration key or if the call fails None.

        Examples
        --------
        self.get_config_option_key_input('abilities/primary', 'A')

        """
        key = ctypes.c_wchar_p(key)
        default_key = ctypes.create_string_buffer(256)
        default_key.value = default
        if self.dll.LogiGetConfigOptionKeyInput(key, default_key, _LOGI_SHARED_SDK_LED):
            return str(default_key.value)
        return None

    def set_config_option_label(self, key: str, label: str) -> bool:
        """Set the label for a configuration key.

        Parameters
        ----------
        key : str
            The configuration key.
        label : str
            The configuration label.

        Returns
        -------
        bool
            Whether or not the configuration setting succeeded.

        Examples
        --------
        self.set_config_option_label('health', 'Health')
        self.set_config_option_label('health/pulse_on_low', 'Pulse on Low')

        """
        key = ctypes.c_wchar_p(key)
        label = ctypes.c_wchar_p(label)
        return bool(self.dll.LogiSetConfigOptionLabel(key, label, _LOGI_SHARED_SDK_LED))
