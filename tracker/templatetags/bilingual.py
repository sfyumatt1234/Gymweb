"""Template tags: {% t "English" "繁體中文" %}."""

from __future__ import annotations

from django import template

from tracker.i18n_ui import bilingual_line

register = template.Library()


@register.simple_tag
def t(en: str, zh_tw: str) -> str:
    """Render English + Traditional Chinese on two lines."""
    return bilingual_line(en, zh_tw)
