class Color():
    """
    A little class for colorizing text
    """
    WHITE = 0
    BLACK = 1
    BLUE = 2
    GREEN = 3
    LIGHT_RED = 4
    BROWN = 5
    PURPLE = 6
    ORANGE = 7
    YELLOW = 8
    LIGHT_GREEN = 9
    CYAN = 10
    LIGHT_CYAN = 11
    LIGHT_BLUE = 12
    PINK = 13
    GRAY = 14
    LIGHT_GRAY = 15

    def __init__(self, text, color):
        """
        Colorized text for IRC.
        - `text` is anything that can be turned into a string
        - `color` is a color code, for example Color.BLUE
        """
        self.text = text
        self.color = color

    def __str__(self):
        return (
            "{:c}{:d}{:c}{text}{:c}{:c}"
            .format(3, self.color, 2, self.text, 2, 3)
        )


CONFIG = {
    "user": Color.CYAN,
    "project": Color.PINK,
    "branch": Color.LIGHT_RED,
    "url": Color.BLUE,
    "tag_name": Color.LIGHT_RED,
}
