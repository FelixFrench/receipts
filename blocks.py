# Defines the structure of 'blocks' of formatted text

from enum import Enum
from dataclasses import dataclass
from PIL import Image

class Style(Enum):
    HEADING = 1
    SUBHEADING = 2
    RIGHT_ALIGN = 3
    BODY = 4

@dataclass(frozen=True)
class TextBlock:
    text: str
    style: Style = Style.BODY

@dataclass(frozen=True)
class ImageBlock:
    image: Image.Image

type Block = TextBlock | ImageBlock

type Section = list[Block]


if __name__ == "__main__":
    b = TextBlock("abc")
    print(b)
