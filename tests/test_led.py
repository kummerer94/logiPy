import time

import pytest

# TODO: Change this later to use the installed library
from src.logiledpy import led, keys


@pytest.fixture
def led_service():
    with led.LEDService() as service:
        service.set_target_device(led.LOGI_DEVICETYPE_ALL)
        yield service


def test_flash_lighting(led_service):
    led_service.pulse_single_key(keys.A, 100, 100, 100, 500, 0, 0, 0)
    time.sleep(1)
