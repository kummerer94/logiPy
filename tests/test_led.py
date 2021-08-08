import time

import pytest
import ctypes

# TODO: Change this later to use the installed library
from src.logiledpy import led, keys
from src.logiledpy.led import DeviceType


@pytest.fixture
def led_service():
    with led.LEDService(wait_for_sdk_initialization=False) as service:
        yield service


example_color = (157, 0, 79)


def set_example_scene(led_service):
    for c in "example":
        led_service.set_lighting_for_key(keys.key(c), led.KeyType.name, *example_color)
        time.sleep(0.05)


def test_loading_dll():
    service = led.LEDService()
    assert isinstance(service.dll, ctypes.CDLL)


@pytest.mark.parametrize(
    "target", [DeviceType.monochrome, DeviceType.rgb, DeviceType.perkey_rgb, DeviceType.all]
)
def test_setting_target_device(led_service, target):
    assert led_service.set_target_device(target)
    assert led_service.pulse_single_key(keys.A, 100, 100, 100, 500, 0, 0, 0)
