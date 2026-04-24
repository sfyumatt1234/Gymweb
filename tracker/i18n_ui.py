"""Bilingual UI helpers: English + Traditional Chinese (並列顯示)."""

from __future__ import annotations

from django.utils.html import escape
from django.utils.safestring import SafeString, mark_safe


def bilingual_line(en: str, zh_tw: str) -> SafeString:
    """Return safe HTML: English line + Traditional Chinese line."""
    return mark_safe(
        '<span class="bilingual">'
        f'<span class="en-line">{escape(en)}</span>'
        f'<span class="zh-line">{escape(zh_tw)}</span>'
        "</span>"
    )
