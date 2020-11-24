from enum import Enum
from html.parser import HTMLParser
import re

# Map an align flag to the label index
LABEL_MAP = [
    # 0  1  2  3  4  5  6  7  8  9 10 11   // align flags
    [0, 6, 2, 8, 9, 11, 3, 5, 1, 4, 7, 10],  # 0 = no centering
    [1, 7, -1, -1, 9, 11, 4, -1, -1, -1, -1, 10],  # 1 = center x
    [3, -1, 5, -1, 9, 11, -1, -1, 4, -1, -1, 10],  # 2 = center y
    [4, -1, -1, -1, 9, 11, -1, -1, -1, -1, -1, 10],  # 3 = center x & y
    [0, 6, 2, 8, 10, -1, 3, 5, 1, 4, 7, -1],  # 4 = center front (default)
    [1, 7, -1, -1, 10, -1, 4, -1, -1, -1, -1, -1],  # 5 = center front & x
    [3, -1, 5, -1, 10, -1, -1, -1, 4, -1, -1, -1],  # 6 = center front & y
    [4, -1, -1, -1, 10, -1, -1, -1, -1, -1, -1, -1],  # 7 = center front & x & y
]


def get_value(obj: dict, key: str, default=None):
    """Try to get a value from the given dict"""
    return obj[key] if key in obj else default


def fix_color(color: str, fallback: str):
    """Fix the given color string"""
    if color is not None and re.fullmatch(r"#[a-fA-F0-9]{3,6}", color):
        return color.upper()

    return fallback.upper()


class Profile(Enum):
    """A standard keycap profile"""
    DCS = "DCS"
    DSA = "DSA"
    SA = "SA"
    DSS = "DSS"


class ProfileRow(Enum):
    """A keycap profile row"""
    ONE = "1"
    TWO = "2"
    THREE = "3"
    FOUR = "4"
    FIVE = "5"
    HOMING = "D"
    SPACE = "SPACE"
    NONE = ""


PROFILE_MAP = {
    "DCS": Profile.DCS,
    "DSA": Profile.DSA,
    "SA": Profile.SA,
}

ROW_MAP = {
    "R1": ProfileRow.ONE,
    "R2": ProfileRow.TWO,
    "R3": ProfileRow.THREE,
    "R4": ProfileRow.FOUR,
    "R5": ProfileRow.FIVE,
    "SPACE": ProfileRow.SPACE,
}


class KeySegment(Enum):
    TL = "TL"
    TM = "TM"
    TR = "TR"

    ML = "ML"
    MM = "MM"
    MR = "MR"

    BL = "BL"
    BM = "BM"
    BR = "BR"

    SWITCH = "switch"
    LED = "led"


class KeyBase:
    """Common elements of key classes"""
    def __init__(self, is_decal: bool, color: str, x: float, y: float, width: float, height: float, profile: Profile = None, profile_str: str = None, homing: bool = None):
        self.is_decal = is_decal
        self.color = fix_color(color, "#cccccc")
        self.width = width
        self.height = height
        self.x = x
        self.y = y
        if profile is not None:
            self.profile = profile
        elif profile_str is not None and homing is not None:
            self.__parse_profile(profile_str, homing)
        else:
            raise ValueError("Either profile or profile_str AND homing must be supplied")

    def __parse_profile(self, profile_string: str, homing: bool):
        """Parse the given profile string"""
        parsed_profile = profile_string.split(" ")
        if parsed_profile[0] in PROFILE_MAP:
            self.profile = PROFILE_MAP[parsed_profile[0]]
        else:
            self.profile = Profile.DCS

        # currently only SA supports homing
        if homing and self.profile is Profile.SA:
            self.profile_row = ProfileRow.HOMING
        elif self.profile is Profile.DSA:
            self.profile_row = ProfileRow.NONE
        elif self.profile is Profile.DCS and self.height > 1:
            self.profile_row = ProfileRow.NONE
        elif len(parsed_profile) > 1 and parsed_profile[1] in ROW_MAP:
            self.profile_row = ROW_MAP[parsed_profile[1]]
        else:
            self.profile_row = ProfileRow.NONE

        # currently only SA supports SPACE
        if self.profile_row is ProfileRow.SPACE and self.profile is not Profile.SA:
            self.profile_row = ProfileRow.NONE

        # Defaults for unsculpted keys
        if self.profile_row is ProfileRow.NONE:
            if self.profile is Profile.DCS:
                self.profile_row = ProfileRow.ONE
            elif self.profile is Profile.SA:
                self.profile_row = ProfileRow.THREE

        # SA R5 doesn't exist
        if self.profile_row is ProfileRow.FIVE and self.profile is Profile.SA:
            self.profile_row = ProfileRow.FOUR

    def segment_location(self, segment: KeySegment):
        """Given a key segment, return its position for this key"""
        x = self.x * -1
        center_x = x - self.width / 2
        center_y = self.y + self.height / 2

        if segment is KeySegment.TL:
            return x - 0.5, self.y + 0.5
        elif segment is KeySegment.TM:
            return center_x, self.y + 0.5
        elif segment is KeySegment.TR:
            return x - self.width + 0.5, self.y + 0.5
        elif segment is KeySegment.ML:
            return x - 0.5, center_y
        elif segment is KeySegment.MM:
            return center_x, center_y
        elif segment is KeySegment.MR:
            return x - self.width + 0.5, center_y
        elif segment is KeySegment.BL:
            return x - 0.5, self.y + 0.5 + self.height - 1
        elif segment is KeySegment.BM:
            return center_x, self.y + self.height - 0.5
        elif segment is KeySegment.BR:
            return x - self.width + 0.5, self.y + self.height - 0.5
        elif segment is KeySegment.SWITCH:
            return center_x, center_y
        elif segment is KeySegment.LED:
            return center_x, center_y

    def segment_dimensions(self, segment: KeySegment):
        """Given a key segment, return its dimensions for this key

           If the segment doesn't need to be resized in any direction, that direction will be `None`
        """
        overlap = 0.2 if self.profile is Profile.DSA else 0.0

        w = None
        h = None

        if segment is KeySegment.TM or segment is KeySegment.MM or segment is KeySegment.BM:
            w = self.width - 1 + overlap if self.width - 1 + overlap > 0 else overlap
        if segment is KeySegment.ML or segment is KeySegment.MM or segment is KeySegment.MR:
            h = self.height - 1 + overlap

        return w, h

    def segment_name(self, segment: KeySegment):
        """Given a key segment, return its name for this key"""
        raise NotImplementedError()


class Key(KeyBase):
    def __init__(self, label: str, x: int, y: int, row: int, column: int, props: dict):
        """Construct a new Key object"""
        super().__init__(
            is_decal=props["d"],
            color=props["c"],
            width=props["w"],
            height=props["h"],
            x=x + props["rx"],
            y=y,
            profile_str=props["p"],
            homing="n" in props
        )
        self.rotation = props["r"]
        self.rx = props["rx"]
        self.ry = props["ry"]
        self.row = row
        self.column = column
        label = re.sub(r'<span class=[\"\']cd[\'\"]>([^<]*)</span>', lambda m: m[1], label)
        self._parse_labels(label, props)

        if len(label) == 0 and self.width < 4.5:
            self.name = "Blank"
        elif len(label) == 0 and self.width >= 4.5:
            self.name = "Space"
        else:
            self.name = HTMLParser().unescape(label.replace("\n", " "))
            self.name = re.sub(r"\s+", " ", self.name)
            self.name = re.sub(r"<i class='(fa|kb) (fa|kb)-([a-zA-Z0-9\-]+)'><\/i>", lambda m: m[3], self.name)

        if "x2" in props or "y2" in props or "w2" in props or "h2" in props:
            self.outcrop = Outcrop(self.x, self.y, self.profile, self.is_decal, props)
        else:
            self.outcrop = None

    def _parse_font_sizes(self, primary_size, secondary_size, individual_sizes, align):
        """Helper to parse font sizes for labels"""
        sizes = [primary_size] + [secondary_size] * 11
        if individual_sizes:
            for pos, size in enumerate(individual_sizes):
                if size == 0:
                    sizes[LABEL_MAP[align][pos]] = primary_size
                else:
                    sizes[LABEL_MAP[align][pos]] = size

        return sizes

    def _parse_text(self, raw_labels, align):
        """Helper to parse labels based on alignment"""
        labels = ["", "", "", "", "", "", "", "", "", "", "", ""]
        for pos, label in enumerate(raw_labels):
            labels[LABEL_MAP[align][pos]] = label

        return labels

    def _parse_colors(self, raw_colors, align):
        """Parse label colors"""
        colors = raw_colors.split('\n')

        if len(colors) > 1:
            label_colors = [None] * 12
            for pos, color in enumerate(colors):
                if color is not None and len(color) > 0:
                    label_colors[LABEL_MAP[align][pos]] = color
        else:
            label_colors = [colors[0]] * 12

        return label_colors

    def _parse_labels(self, label: str, props: dict):
        """Helper to parse all label attributes"""
        label_texts = self._parse_text(label.split('\n'), props["a"])
        label_colors = self._parse_colors(props["t"], props["a"])
        label_sizes = self._parse_font_sizes(
            props["f"],
            props["f2"] if "f2" in props else props["f"],
            props["fa"],
            props["a"]
        )

        assert(len(label_texts) == len(label_sizes) == len(label_colors) == 12)

        self.labels = [Label(label_texts[idx], label_colors[idx],
                             label_sizes[idx]) for idx in range(12)]

    def segment_name(self, segment):
        if segment is KeySegment.SWITCH:
            return "switch"
        elif segment is KeySegment.LED:
            return "led"
        elif self.outcrop:
            return self.profile.value + segment.value + 'F'
        else:
            return self.profile.value + self.profile_row.value + segment.value


class Outcrop(KeyBase):
    def __init__(self, x: int, y: int, profile: Profile, is_decal: bool, props: dict):
        super().__init__(
            is_decal=is_decal,
            color=props["c"],
            x=get_value(props, "x2", 0) + x,
            y=get_value(props, "y2", 0) + y,
            width=get_value(props, "w2", 1),
            height=get_value(props, "h2", 1),
            profile=profile
        )
        self.is_stepped = "l" in props and props["l"]

    def segment_name(self, segment: KeySegment):
        return self.profile.value + segment.value + ('S' if self.is_stepped else 'F')


class Label:
    def __init__(self, text: str, color: str, size: int):
        self.text = re.sub("<br ?/?>", "\n", HTMLParser().unescape(text))
        self.color = fix_color(color, "#111111")
        self.size = size
