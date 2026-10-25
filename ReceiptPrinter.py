# Gather data from various sources across the internet to be printed onto a receipt for some breakfast reading

# TODO:
# Add https://api.edinburghfestivalcity.com/ results?
# Carbon intensity API?
# Worldometer? https://worldometer.readthedocs.io/en/latest/
# Use RSS feeds for news, and other things too?
# Get lat,long from postcode
# Choose local news feed from postcode

from escpos.escpos import Escpos
from escpos.printer import Network
from config import load_config
from blocks import TextBlock, ImageBlock, Style, Section
from typing import assert_never
from content import gather_sections
from shared import format_text

PRINTER_IP = "192.168.1.165"
PRINTER_TYPE = "TM-T88IV"
FONT = "a"
MARGIN = 2


def print_text(printer: Escpos, text: str, style: Style = Style.BODY, margin: int = MARGIN) -> None:

    # Margin must be at least 1 to avoid case where the printer auto-newlines when line is full
    if margin < 1:
        raise ValueError(f"Margin must be at least 1, got {margin}")

    match style:
        case Style.HEADING:
            printer.set(bold=True)

        case Style.SUBHEADING:
            printer.set(bold=False)

        case Style.RIGHT_ALIGN:
            printer.set(bold=False)
            
        case Style.BODY:
            printer.set(bold=False)

        case Style.POETRY:
            printer.set(bold=False)

        case Style.CENTER:
            printer.set(bold=False)

        case _:
            assert_never(style)
    
    cols = printer.profile.get_columns(font=FONT)

    formatted_lines = format_text(text, cols, margin, style)

    for line in formatted_lines:
        printer.text(line)
        printer.ln()


def print_section(printer: Escpos, section: Section, margin: int = MARGIN) -> None:
    for block in section:
        match block:
            case TextBlock():
                printer.set(align="left")
                print_text(printer, block.text, block.style, margin)

            case ImageBlock():
                printer.set(align="center")
                printer.image(block.image)

            case _:
                assert_never(block)


def main() -> None:

    cfg = load_config()

    # Try to connect and set the font - will raise if printer offline, avoiding API calls
    printer = Network(PRINTER_IP, profile=PRINTER_TYPE)
    printer.set(font=FONT)
    
    sections = gather_sections(cfg)

    for section in sections:
        print_section(printer, section)
        printer.ln(2)

    # Finalise
    printer.cut()


if __name__ == "__main__":
    main()
