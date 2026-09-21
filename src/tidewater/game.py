# @author Daniel McCoy Stephenson
"""The game: a save slot, the two tiers of state, the scenes, and the loop
that runs them. Front-end agnostic - see tak.ui."""

import json
import os
import shutil
from datetime import datetime

from jsonschema.exceptions import ValidationError

from tak import Prompt
from tak.saves import (
    SaveFileManager,
    chooseSlot,
    syncBrowserSaves,
    validateAgainstSchema,
)
from tak.ui import UIType, createUserInterface

from tidewater import loop as loopEngine
from tidewater import progression, scenes, usageReporting
from tidewater.config import Config
from tidewater.header import buildHeader
from tidewater.state import (
    SAVE_FILENAME,
    SCHEMA_PATH,
    LoopState,
    MetaState,
    fromSaveDict,
    toSaveDict,
)
from tidewater.trace_client import TraceClient

TITLE = "Tidewater"
TAGLINE = "a day in a fishing village that will not end"
ENV_PREFIX = "TIDEWATER"
OPENING_PROMPT = (
    "There's a rod beside you and the whole day ahead. What would you like to do?"
)

# Which front-end the game runs. The rest of the game is front-end agnostic.
INTERFACE_TYPE = UIType.CONSOLE


def describeSlot(metadata):
    """The save menu's summary of a slot: "Loop 3, 4 known"."""
    if metadata.get("loopBroken"):
        return "loop broken, %d known" % metadata.get("known", 0)
    return "Loop %d, %d known" % (metadata.get("loops", 1), metadata.get("known", 0))


def slotMetadata(slotPath, data):
    meta = data.get("meta", {})
    return {
        "loops": meta.get("loops", 1),
        "known": len(meta.get("facts", [])),
        "loopBroken": meta.get("loopBroken", False),
    }


# @author Daniel McCoy Stephenson
class Tidewater:
    def __init__(self, interfaceType=INTERFACE_TYPE):
        self.running = True
        self.usageReporting = TraceClient.disabled()
        self.config = Config()
        self.usageReporting = usageReporting.start(self.config)
        self.saveFileManager = SaveFileManager(
            self.config.dataDirectory,
            primaryFile=SAVE_FILENAME,
            readMetadata=slotMetadata,
        )
        self.failedLoad = None

        self.meta = MetaState()
        self.loop = LoopState()
        self.prompt = Prompt(OPENING_PROMPT)
        self.ui = createUserInterface(
            interfaceType,
            self.prompt,
            lambda: buildHeader(self),
            title=TITLE,
            tagline=TAGLINE,
            envPrefix=ENV_PREFIX,
        )

        chosen = chooseSlot(
            self.ui, self.saveFileManager, TITLE + " - Save Files", describeSlot
        )
        if chosen is None:
            # Ending the run rather than the process, so the front-end still
            # gets its cleanup() - play() does nothing but that.
            self.running = False
            return

        self.usageReporting.report("save-loaded", tags=usageReporting.versionTags())

        kind, _ = chosen
        savePath = self.saveFileManager.get_save_path(SAVE_FILENAME)
        if kind == "load" and os.path.exists(savePath):
            self.load(savePath)
            if self.failedLoad:
                self._preserveDamagedSave(savePath)
            elif self.meta.loops > 1 or self.meta.loopBroken:
                self.prompt.text = "The docks again. What would you like to do?"
        # A loaded save may predate an unlock, or have earned one since.
        progression.catchUp(self.meta)
        self.scenes = scenes.build(self)

    # --- the loop's hooks -------------------------------------------------
    def learn(self, factId):
        """Promote something to knowledge. Returns True if it was new."""
        if self.meta.learn(factId):
            self.loop.newFacts.append(factId)
            return True
        return False

    def advance(self, hours=1):
        """Move the clock and tell the player whatever happened."""
        outcome = loopEngine.advance(self, hours)
        if outcome.lines:
            self.ui.showDialogue("\n\n".join(outcome.lines))
        if outcome.reset:
            self.prompt.text = "The docks again. What would you like to do?"
            if outcome.ending:
                self.prompt.text = "A new day. What would you like to do?"
        return outcome

    # --- play -------------------------------------------------------------
    def play(self):
        try:
            if self.running:
                self._runGameLoop()
        finally:
            self.ui.cleanup()
            self.usageReporting.close()

    def _runGameLoop(self):
        while self.running:
            unlock = progression.getNextUnlock(self.meta)
            if unlock is not None:
                self.ui.showDialogue("[%s]" % unlock["announcement"])
            current = self.loop.location
            if current not in self.scenes:
                current = self.loop.location = "docks"
            nextScene = self.scenes[current].run()
            self.save()
            if nextScene == scenes.QUIT:
                self.running = False

    # --- persistence ------------------------------------------------------
    def save(self):
        data = toSaveDict(self.meta, self.loop)
        validateAgainstSchema(data, SCHEMA_PATH)
        path = self.saveFileManager.get_save_path(SAVE_FILENAME)
        with open(path, "w", encoding="utf-8") as saveFile:
            json.dump(data, saveFile, indent=2)
        syncBrowserSaves()

    def load(self, path):
        try:
            with open(path, "r", encoding="utf-8") as saveFile:
                data = json.load(saveFile)
            validateAgainstSchema(data, SCHEMA_PATH)
            self.meta, self.loop = fromSaveDict(data)
        except (ValueError, ValidationError, OSError, KeyError, TypeError) as error:
            # A failed load leaves fresh objects in place of the player's run,
            # and save() writes them back after the very next action - so the
            # bytes that failed are copied aside before play() is reached.
            self.failedLoad = "%s: %s" % (os.path.basename(path), error)
            self.meta, self.loop = MetaState(), LoopState()

    def _preserveDamagedSave(self, path):
        stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        backup = "%s.damaged-%s" % (path, stamp)
        try:
            shutil.copy2(path, backup)
            where = "A copy was kept at %s." % backup
        except OSError:
            where = "It could not be copied aside."
        self.ui.showDialogue(
            "This save could not be read (%s). You'll start a fresh game in "
            "this slot. %s" % (self.failedLoad, where)
        )
