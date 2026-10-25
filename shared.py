from blocks import Style
from textwrap import wrap
from typing import assert_never

def format_text(text: str, cols: int, margin: int, style: Style = Style.BODY) -> list[str]:

    match style:
        case Style.HEADING:
            align = str.center

        case Style.SUBHEADING:
            align = str.center

        case Style.RIGHT_ALIGN:
            align = str.rjust
            
        case Style.BODY:
            align = str.ljust

        case Style.POETRY:
            align = str.ljust

        case Style.CENTER:
            align = str.center

        case _:
            assert_never(style)
    
    width = cols - margin*2
    
    textlines = text.split("\n")
    wrapped_lines: list[str] = []
    for line in textlines:
        wrapped_lines.extend(wrap(
            line,
            width = width,
            subsequent_indent="  " if (style == Style.POETRY) else "",
            break_long_words=(style != Style.POETRY),
            break_on_hyphens=(style != Style.POETRY)
        ) or [""])

    return [(" "*margin + align(wl, width)) for wl in wrapped_lines]