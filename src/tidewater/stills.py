# @author Daniel McCoy Stephenson
"""The picture above each place's menu in the browser (RFC 0025).

art/stills.json names one still per place and its alt text; the PNGs are in
pictures/ and ride inside game.zip. Both paths are relative to where the game
runs, like schemas/. A game started anywhere the manifest cannot be read
(an installed copy run from another directory, say) simply shows no
pictures - and the console never shows them at all."""

import json
import os

MANIFEST_PATH = os.path.join("art", "stills.json")


def load(path=MANIFEST_PATH):
    """{place: alt text} for every still the manifest names, or {}."""
    try:
        with open(path, encoding="utf-8") as manifest:
            stills = json.load(manifest)["stills"]
    except (OSError, ValueError, KeyError, TypeError):
        return {}
    return {
        place: entry["alt"]
        for place, entry in stills.items()
        if isinstance(entry, dict) and entry.get("alt")
    }


def show(ui, place, alts):
    """Put this place's still above the screens that follow, or clear it
    for a page that is not a place (the journal, the last page)."""
    if place in alts:
        ui.setPicture(place, alts[place])
    else:
        ui.setPicture(None)
