import os

import pytest

from tak import Prompt
from tak.ui import BaseUserInterface

REPOSITORY_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))


@pytest.fixture(autouse=True)
def isolatedRun(monkeypatch, tmp_path):
    """Every test runs from the repository root (the schema path is
    cwd-relative, as it is under Pyodide), saves into its own directory, and
    never reports usage to the real trace service."""
    monkeypatch.chdir(REPOSITORY_ROOT)
    monkeypatch.setenv("TIDEWATER_SAVE_DIR", str(tmp_path / "saves"))
    monkeypatch.setenv("TIDEWATER_USAGE_REPORTING_ENABLED", "false")
    monkeypatch.delenv("TRACE_USAGE_REPORTING", raising=False)
    monkeypatch.delenv("DO_NOT_TRACK", raising=False)


class ScriptedUI(BaseUserInterface):
    """A front-end driven by a script of menu labels.

    Each entry in the script is matched against the labels of the menu
    being shown (substring, first match wins); a label that is not on the
    menu fails the test with the menu printed, which is what makes a
    playthrough test readable when it breaks. Dialogues are recorded."""

    def __init__(self, script, header=None):
        super().__init__(Prompt(), header)
        self.script = list(script)
        self.menus = []
        self.headers = []
        self.dialogues = []
        self.cleanedUp = False

    def lotsOfSpace(self):
        pass

    def divider(self):
        pass

    def showOptions(self, descriptor, optionList, unavailableOptions=None):
        reasons = self.unavailableReasons(optionList, unavailableOptions)
        # Read the header the way a real front-end would, so the provider
        # runs on every menu and a typo in it fails the playthrough.
        self.headers.append(self.header())
        self.menus.append(
            (descriptor, list(optionList), reasons, self.currentPrompt.text)
        )
        if not self.script:
            raise AssertionError(
                "script ran out at menu %r: %r" % (descriptor, optionList)
            )
        wanted = self.script.pop(0)
        for index, label in enumerate(optionList):
            if wanted in label:
                if reasons[index] is not None:
                    raise AssertionError(
                        "%r is unavailable on menu %r (%s)"
                        % (label, descriptor, reasons[index])
                    )
                return str(index + 1)
        raise AssertionError(
            "%r is not on menu %r: %r" % (wanted, descriptor, optionList)
        )

    def showDialogue(self, text):
        self.dialogues.append(text)
        self.currentPrompt.reset()

    def promptForText(self, promptText):
        return self.script.pop(0)

    def timedKeyPress(self, message):
        return 0.0

    def cleanup(self):
        self.cleanedUp = True

    def saw(self, fragment):
        return any(fragment in text for text in self.dialogues)


class FakeGame:
    """Just enough of Tidewater for the engine and villagers: state, a
    prompt, learn() and a UI."""

    def __init__(self, ui=None):
        from tidewater.state import LoopState, MetaState

        self.meta = MetaState()
        self.loop = LoopState()
        self.prompt = Prompt()
        self.ui = ui if ui is not None else ScriptedUI([])

    def learn(self, factId):
        if self.meta.learn(factId):
            self.loop.newFacts.append(factId)
            return True
        return False

    def advance(self, hours=1):
        from tidewater import loop as loopEngine

        outcome = loopEngine.advance(self, hours)
        if outcome.lines:
            self.ui.showDialogue("\n\n".join(outcome.lines))
        return outcome
