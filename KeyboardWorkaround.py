"""
DearPyGui 1.11.1 has a bug regarding input_text and extend latin characters.
hoffstadt/dearpygui Issue #1564

This is a temporary workaround for _some_ languages.
Currennt workaround works for: Czech
"""

letter_workaround = {
    "ì":"ě",
    "":"š",
    "è":"č",
    "ø":"ř",
    "":"ž",
    "ù":"ů",
    "Ì":"Ě",
    "":"Š",
    "È":"Č",
    "Ø":"Ř",
    "":"Ž",
    "":"ť",
    "":"Ť",
    "Ï":"ď",
    "¾":"ľ",
    "¼":"Ľ",
    "ò":"ň",
    "Ò":"Ň",
    "Ù":"Ů"
}