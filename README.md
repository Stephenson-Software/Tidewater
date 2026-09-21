# Tidewater

*A day in a fishing village that will not end.*

You wake on the docks at eight with a rod beside you. At nine in the evening a storm comes in off the water. At eleven the harbour bell rings — a bell that, Sam will tell you, has had no rope on it for thirty years — and you wake on the docks at eight.

Everything resets but what you know. What you know is the only way out.

Tidewater is a time-loop text adventure set in [FishE](https://github.com/Stephenson-Software/FishE)'s village, built on [tak](https://github.com/Stephenson-Software/tak), the text-adventure kit extracted from it.

## Play

`pip install -r requirements.txt` needs `git` on your PATH: the kit is installed from its GitHub tag.

**In your browser** — the game runs in your tab, saves live in your browser:

```bash
pip install -r requirements.txt
python3 web/build_zip.py     # once, and after any src/ change or tak upgrade
python3 web/serve.py         # then open http://127.0.0.1:8080
```

**In a terminal:**

```bash
pip install -r requirements.txt
./run.sh                     # or: PYTHONPATH=src python3 -m tidewater
```

**As a server** (the browser is a terminal for a game running on your machine; everyone who opens the page shares it): `./run.sh web`, then open `http://127.0.0.1:8000`. `TIDEWATER_WEB_HOST`/`TIDEWATER_WEB_PORT` move either server.

**Docker:** `docker build -t tidewater . && docker run -p 8080:8080 tidewater` serves the browser build.

## The story

A stranger, a village, one repeating day, and a thirty-year-old night nobody finished. The game tells it in pieces; the journal's "What is happening to you" page assembles the pieces you have found, in plain words. The whole of it, spoilers included, is in [docs/STORY.md](docs/STORY.md).

## How it works

The day is fifteen hours long and every action costs one. Seven places — the docks, Gilbert's shop, home, the tavern, the bank, the lighthouse on the point, the churchyard above the village — and six villagers who keep hours. Talk to people. Some of what they say is a **fact**, and facts survive the night: they appear in your journal and they open new questions on other villagers' menus. Facts also point at each other, Outer Wilds fashion: under each one the journal lists where it leads that you haven't been, without ever naming what is there. There are fifteen facts and two ways out — and a third way that is both. The trail to the bell is four facts long; the trail to the light — the lamp on the point, which went dark the night the Marigold was lost, and can be made to hold through the storm at nine — is five. Either can be walked in a single day once you know the way, and neither can be walked in the first. Each ending answers the questions the village has been refusing to: who cut the rope, and why a bell with no rope rings at eleven — Ada tells you in the lamp room, or Tom tells you in the tower. Each also tells you, plainly, that only half of that old night is mended. Do both in one day — the lamp lit before nine, the rope hung, the bell rung at eleven with the beam on the water — and the night is closed for good.

Some of what people ask you is a **choice**, not a question, and the village holds you to it — for a day. Tell Margaret that Tom should see the ledger and she walks it across the road at closing; hurry Ada through the story of that night and she says nothing more until the bell. *Margaret will remember that.* Ask Gilbert for the lamp oil one way and he slams the can down; ask the other and he fills it himself — and what he is doing when the light holds is different too. The reset forgets it; that is the loop.

The state is in two tiers, which is the whole design:

| | Holds | On the bell |
|---|---|---|
| `MetaState` | loops, facts, unlocks, endings | kept |
| `LoopState` | the hour, where you are, what you carry, what happened today (its `flags`, every one named in `flags.py`) | thrown away |

An ending is a row in `loop.py`'s `ENDINGS` table — an hour, a flag, a handler — and the clock consults the table each hour. The light fires at nine and the bell at eleven, so a player who has done both leaves by the light.

The day is seeded, so the sea gives up the same fish to the same casts in every loop. A player who changes nothing sees nothing change.

## Saves

Numbered slots under `data/` (or `TIDEWATER_SAVE_DIR`), one `save.json` each, validated against `schemas/save.json` on every load and save. A save that can't be read is listed as damaged, never overwritten, and copied aside if you open it anyway.

## Usage reporting

Tidewater reports one `startup` event and one `save-loaded` event (program name and version only) to `trace.danielstephenson.dev`, on by default, and prints a one-line notice the first time an install does so. `TIDEWATER_USAGE_REPORTING_ENABLED=false`, `TRACE_USAGE_REPORTING=off` or `DO_NOT_TRACK=1` turns it off, the browser build never reports, and what is collected and why is written up in the [trace client's README](https://github.com/Stephenson-Software/trace-client-python#turning-it-off).

## Development

```bash
pip install pytest pytest-cov -r requirements.txt
./test.sh
```

`tests/test_game.py` plays the whole solution through a scripted front-end; if a menu label moves or a gate breaks, that test says which.

## License
This project is licensed under the **Stephenson Software Non-Commercial License (Stephenson-NC)**.  
© 2026 Daniel McCoy Stephenson. All rights reserved.  

You may use, modify, and share this software for **non-commercial purposes only**.  
Commercial use is prohibited without explicit written permission from the copyright holder.  

Full license text: [Stephenson-NC License](https://github.com/Stephenson-Software/stephenson-nc-license) (also in [LICENSE](LICENSE))  
SPDX Identifier: `Stephenson-NC`
