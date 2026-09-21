# Tidewater

*A day in a fishing village that will not end.*

You wake on the docks at eight with a rod beside you. At nine in the evening a storm comes in off the water. At eleven the harbour bell rings — a bell that, Sam will tell you, has had no rope on it for thirty years — and you wake on the docks at eight.

Everything resets but what you know. What you know is the only way out.

Tidewater is a time-loop text adventure set in [FishE](https://github.com/Stephenson-Software/FishE)'s village, built on [tak](https://github.com/Stephenson-Software/tak), the text-adventure kit extracted from it.

## Play

**In your browser** — the game runs in your tab, saves live in your browser:

```bash
pip install -r requirements.txt
python3 web/build_zip.py     # once, and after any src/ change
python3 web/serve.py         # then open http://127.0.0.1:8080
```

**In a terminal:**

```bash
pip install -r requirements.txt
./run.sh                     # or: PYTHONPATH=src python3 -m tidewater
```

**As a server** (the browser is a terminal for a game running on your machine; everyone who opens the page shares it): `./run.sh web`, then open `http://127.0.0.1:8000`. `TIDEWATER_WEB_HOST`/`TIDEWATER_WEB_PORT` move either server.

**Docker:** `docker build -t tidewater . && docker run -p 8080:8080 tidewater` serves the browser build.

## How it works

The day is fifteen hours long and every action costs one. Five places — the docks, Gilbert's shop, home, the tavern, the bank — and four villagers who keep hours. Talk to people. Some of what they say is a **fact**, and facts survive the night: they appear in your journal and they open new questions on other villagers' menus. There is one trail to the bell, four facts long, and the whole of it can be walked in a single day once you know the way. It cannot be walked in the first.

The state is in two tiers, which is the whole design:

| | Holds | On the bell |
|---|---|---|
| `MetaState` | loops, facts, unlocks, endings | kept |
| `LoopState` | the hour, where you are, what you carry, what happened today | thrown away |

The day is seeded, so the sea gives up the same fish to the same casts in every loop. A player who changes nothing sees nothing change.

## Saves

Numbered slots under `data/` (or `TIDEWATER_SAVE_DIR`), one `save.json` each, validated against `schemas/save.json` on every load and save. A save that can't be read is listed as damaged, never overwritten, and copied aside if you open it anyway.

## Usage reporting

Off until a program key is issued. When it is, Tidewater will send one `startup` event and one `save-loaded` event (program name and version only) to [trace](https://github.com/Stephenson-Software/trace); `TIDEWATER_USAGE_REPORTING_ENABLED=false`, `TRACE_USAGE_REPORTING=off` or `DO_NOT_TRACK=1` turns it off, and the browser build never reports.

## Development

```bash
pip install pytest pytest-cov -r requirements.txt
./test.sh
```

`tests/test_game.py` plays the whole solution through a scripted front-end; if a menu label moves or a gate breaks, that test says which.

## License

[Stephenson-NC](LICENSE) — non-commercial use.
