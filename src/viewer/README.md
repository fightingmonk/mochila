# Mochila viewer

`viewer` is a web app that renders the curated Mochila UI.

It's written in [Solara](https://solara.dev).

`viewer` is packaged into the Mochila container and launched on boot, listening to port 8765.

## Running locally

```sh
pip install -r requirements.txt
solara run viewer.py
```

Python dependencies can be a bear. The happy path is a container:

```sh
./build.sh
docker run -p 8765:8765 -p 8529:8529 --name mochila-dev -v $(pwd):/opt/viewer -it mochila:0.1 --entrypoint=/bin/bash
```

Then, in the container:

```sh
cd /opt/viewer
pip install -r requirements.txt
solara run --host 0.0.0.0 viewer.py
```
