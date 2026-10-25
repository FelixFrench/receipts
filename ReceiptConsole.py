# Gather data from various sources across the internet to be printed onto a receipt for some breakfast reading

# TODO:
# Add https://api.edinburghfestivalcity.com/ results?
# Carbon intensity API?
# Worldometer? https://worldometer.readthedocs.io/en/latest/
# Sort news

from time import sleep
from config import load_config
from blocks import TextBlock, ImageBlock, Style, Section
from typing import assert_never
from content import gather_sections
from shared import format_text

RECEIPT_WIDTH = 42
MARGIN = 2

def print_text(text: str, style: Style = Style.BODY, margin: int = MARGIN) -> None:

    formatted_lines = format_text(text, RECEIPT_WIDTH, margin, style)

    if style == Style.HEADING:
        print("\033[1m", end='')

    for line in formatted_lines:
        print(line)
        sleep(0.02)

    if style == Style.HEADING:
        print("\033[0m", end='')


def print_section(section: Section, margin: int = MARGIN) -> None:
    for block in section:
        match block:
            case TextBlock():
                print_text(block.text, block.style, margin)

            case ImageBlock():
                print_text("<image>", Style.CENTER)

            case _:
                assert_never(block)
    
    print("\n")


def main() -> None:

    cfg = load_config()

    sections = gather_sections(cfg, verbose=True)

    print("\n\n")

    for section in sections:
        print_section(section)

if __name__ == "__main__":
    main()
