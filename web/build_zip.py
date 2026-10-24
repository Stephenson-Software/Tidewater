#!/usr/bin/env python3
# @author Daniel McCoy Stephenson
"""Build web/game.zip - the bundle the browser's Pyodide Worker downloads.

    python3 web/build_zip.py

Puts src/, schemas/ and pictures/ in, plus version.txt, art/stills.json and the Worker's entry point,
and the tak package itself (see tak.web.bundle)."""
import os

from tak.web.bundle import build

REPOSITORY_ROOT = os.path.normpath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
)

if __name__ == "__main__":
    build(
        REPOSITORY_ROOT,
        # pictures/ holds the location stills (RFC 0025); art/stills.json
        # names them and carries their alt text. The scene files they were
        # rendered from stay out of the bundle.
        sourceDirectories=("src", "schemas", "pictures"),
        extraFiles=("version.txt", "web/pyodide_main.py", "art/stills.json"),
    )
