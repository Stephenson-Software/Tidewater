#!/usr/bin/env python3
# @author Daniel McCoy Stephenson
"""Serve the browser build: python3 web/serve.py, then open the URL printed.

Hands out web/index.html, web/game.zip and the tak assets at /tak/, with the
COOP/COEP headers the Pyodide front-end needs. It never runs the game; the
player's browser does. TIDEWATER_WEB_HOST / TIDEWATER_WEB_PORT move it."""
import os

from tak.web.serve import main

REPOSITORY_ROOT = os.path.normpath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
)

if __name__ == "__main__":
    main(REPOSITORY_ROOT, title="Tidewater", envPrefix="TIDEWATER")
