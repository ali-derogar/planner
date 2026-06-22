from functools import lru_cache

from arabic_reshaper import reshape
from bidi.algorithm import get_display


@lru_cache(maxsize=512)
def fa(text: str) -> str:
    """Shape and order Persian/Arabic text for correct RTL display."""
    if not text:
        return text
    return get_display(reshape(str(text)))
