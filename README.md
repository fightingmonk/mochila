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

