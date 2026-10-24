# Defines the structure of 'blocks' of formatted text

from enum import Enum
from dataclasses import dataclass

class Style(Enum):
    HEADING = 1
    SUBHEADING = 2
    RIGHT_ALIGN = 3
    BODY = 4

@dataclass(frozen=True)
class Block:
    text: str
    style: Style = Style.BODY


if __name__ == "__main__":
    b = Block("abc")
    print(b)
