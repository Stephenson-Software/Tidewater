# @author Daniel McCoy Stephenson
"""Pyodide entry point - runs inside the Web Worker once game.zip is unpacked.

By the time this file is exec()'d, tak's game-worker.js has already put
/game/src on sys.path (the bundle carries the tak package there too),
chdir'd to /game so schemas/save.json resolves, created the save directory,
restored it from IndexedDB, pointed TIDEWATER_SAVE_DIR at it, and installed
the JavaScript globals the Pyodide front-end needs.
"""

from tak.ui import UIType
from tidewater.game import Tidewater


def main():
    Tidewater(interfaceType=UIType.PYODIDE).play()


main()
