import struct
from typing import Tuple


class Color:
    """An RGBA color object that can be created using RGB, RGBA, color name, or a hex_code."""

    red: int
    green: int
    blue: int
    alpha: int

    def __init__(self, red: int, green: int, blue: int, alpha: int = 255) -> None:
        self.red = red
        self.green = green
        self.blue = blue
        self.alpha = alpha

    def from_color_name(cls, color: str) -> "Color":
        colors = {
            "red": Color(255, 0, 0),
            "orange": Color(255, 165, 0),
            "yellow": Color(255, 255, 0),
            "green": Color(0, 255, 0),
            "blue": Color(0, 0, 255),
            "indigo": Color(75, 0, 130),
            "violet": Color(238, 130, 238),
            "cyan": Color(0, 220, 255),
            "pink": Color(255, 0, 255),
            "purple": Color(128, 0, 255),
            "white": Color(255, 255, 255),
            "black": Color(0, 0, 0),
        }
        if color not in colors:
            raise KeyError(f"Color {color} not found.")
        return colors.get(color)

    @classmethod
    def from_hex(cls, hex: str, alpha: int = 255) -> "Color":
        hex = hex.replace("#", "")
        red, green, blue = struct.unpack("BBB", hex.decode("hex"))
        return Color(red, green, blue, alpha)

    @property
    def hex_code(self) -> str:
        hex_code = struct.pack("BBB", *(self.red, self.green, self.blue)).encode("hex")
        return f"#{hex_code}"

    @property
    def rgb(self) -> Tuple[int, int, int]:
        return (self.red, self.green, self.blue)

    @property
    def rgb_percent(self):
        return (int(p / 255.0) * 100 for p in self.rgb)
