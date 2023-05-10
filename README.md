# Mochila

**A backpack for your DORA metrics**

Mochila collects SDLC events from your dev and devops toolchain, normalizes and correlates them, and computes DORA metrics for you.

What sets Mochila apart is the option to pop the hood and directly query your SDLC events without needing a data team.

## Up and running

Run Mochila in easy mode with Docker.

```sh
git clone https://github.com/fightingmonk/mochila.git
# build the `mochila` docker image
./build.sh
# run the `mochila` container locally
./run.sh

# Explore DORA metrics for a sample app
open http://localhost:8888/notebooks/Sample.ipynb
```

## Developing integrations

Mochila knows how to fetch SDLC events from various data sources like GitHub, CircleCI, etc.

Integration adapters are found in [src/integrations/](./src/integrations/).
The adapters are written in python3; the only non-standard requirement is `python-arango` for writing events to the Mochila database.

### Running integrations manually

If you want to develop or run integrations outside of the `mochila` container,
install the python dependencies and get API tokens for the services you will to pull from.

Integrations typically take a `-t YOUR_TOKEN` command-line parameter or read from a service-specific environment variable.
Here is the GitHub integration as an example:

```sh
cd src/integrations
pip3 install -r requirements.txt
GITHUB_TOKEN="YOUR-GITHUB-PERSONAL-ACCESS-TOKEN" ./github.py ORG_NAME REPO_NAME
./github.py [-t YOUR-GITHUB-PERSONAL-ACCESS-TOKEN] ORG_NAME REPO_NAME
```
