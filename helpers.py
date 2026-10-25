# Helper functions shared by ReceiptPrinter.py and ReceiptConsole.py

from datetime import datetime
from collections.abc import Callable
from typing import Any
from blocks import Block, TextBlock


def ordinal(n: int) -> str:
    if 11 <= (n % 100) <= 13:
        suffix = 'th'
    else:
        suffix = ['th', 'st', 'nd', 'rd', 'th'][min(n % 10, 4)]
    return str(n) + suffix

def get_today_string() -> str:
    # "Monday 1st January 2026"
    today = datetime.now()
    return today.strftime(f"%A {ordinal(today.day)} %B %Y")

def safe_call(func: Callable[..., list[Block]], *args: Any, **kwargs: Any) -> list[Block]:
    """
    Call a function and return a default value if it raises an exception.

    Args:
        func: The function to invoke.
        *args: Positional arguments passed to the function.
        **kwargs: Keyword arguments passed to the function.

    Returns:
        list[Block]: The function's return value if successful,
                     otherwise [TextBlock("Not available")].
    """
    try:
        return func(*args, **kwargs)
    except Exception as e:
        print(e)
        return [TextBlock("Not available")]
