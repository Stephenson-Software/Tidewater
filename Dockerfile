FROM python:3.12-slim

WORKDIR /app

# This image does not run the game - the browser does. web/serve.py only hands
# out the page, the tak assets, and the game bundle; Pyodide then runs the
# Python game in the player's own tab, with that tab's IndexedDB holding the
# saves. No save directory, no volume: every visitor gets their own game.
#
# tak is installed here for two reasons: web/serve.py imports it, and
# web/build_zip.py copies the installed package into the bundle so the browser
# gets exactly the version this image was built with.
COPY requirements.txt ./
RUN apt-get update && apt-get install -y --no-install-recommends git \
    && pip install --no-cache-dir -r requirements.txt \
    && apt-get purge -y git && apt-get autoremove -y && rm -rf /var/lib/apt/lists/*

COPY src/ ./src/
COPY web/ ./web/
COPY schemas/ ./schemas/
COPY version.txt ./

# Bundle the game for the browser to download. Built here rather than checked
# in so the bundle can never be a stale copy of src/.
RUN python3 web/build_zip.py

RUN useradd --system --no-create-home tidewater
USER tidewater

# web/serve.py defaults to 127.0.0.1 (unreachable from outside its own network
# namespace), so 0.0.0.0 is required for a reverse proxy in another container
# to reach it.
ENV TIDEWATER_WEB_HOST=0.0.0.0
ENV TIDEWATER_WEB_PORT=8080
ENV PYTHONUNBUFFERED=1

EXPOSE 8080
CMD ["python3", "web/serve.py"]
