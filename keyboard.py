from .key import Key


class Keyboard:
    def __init__(self):
        self.__color = "#EEEEEE"
        self.__led_color = None
        self.led_brightness = 1
        self.stem_color = [0, 0.7, 1, 1]
        self.css = None
        self.name = "Keyboard"

        self.__keys = []
        self.__switch_type = None

    def add_key(self, key: Key):
        self.__keys.append(key)

    @property
    def key_count(self):
        return len(self.__keys)

    @property
    def color(self):
        return self.__color

    @color.setter
    def color(self, c: str):
        self.__color = c.upper()

    @property
    def led_color(self):
        return self.__led_color

    @led_color.setter
    def led_color(self, c: str):
        self.__led_color = c.upper()

    @property
    def switch_type(self):
        return self.__switch_type

    @switch_type.setter
    def switch_type(self, switch_type: str):
        self.__switch_type = switch_type
        if self.__switch_type == "MX1A-11xx" or self.__switch_type == "KS-3-Black":
            self.stem_color = [0, 0, 0, 1]
        elif self.__switch_type == "MX1A-A1xx":
            self.stem_color = [1, 1, 1, 1]
        elif self.__switch_type == "MX1A-C1xx" or self.__switch_type == "KS-3-White":
            self.stem_color = [1, 1, 1, 0.8]
        elif self.__switch_type == "MX1A-E1xx":
            self.stem_color = [0, 0.7, 1, 1]
        elif self.__switch_type == "MX1A-F1xx" or self.__switch_type == "KS-3-Green":
            self.stem_color = [0, 0.6, 0.25, 1]
        elif self.__switch_type == "MX1A-G1xx" or self.__switch_type == "KS-3-Tea":
            self.stem_color = [0.6, 0.3, 0, 1]
        elif self.__switch_type == "MX1A-L1xx" or self.__switch_type == "KS-3-Red":
            self.stem_color = [1, 0, 0, 1]

    def __iter__(self):
        return iter(self.__keys)
