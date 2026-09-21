#!/bin/bash
# Usage: ./run.sh            (console)
#        ./run.sh web        (server-backed browser front-end)
cd "$(dirname "$0")"
if [ "$1" = "web" ]; then
    PYTHONPATH=src python3 -c "from tak.ui import UIType; from tidewater.game import Tidewater; Tidewater(UIType.WEB).play()"
else
    PYTHONPATH=src python3 -m tidewater
fi
