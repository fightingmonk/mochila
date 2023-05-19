#!/bin/sh
SCRIPT=$(readlink -f "$0")
ROOT=$(dirname "$SCRIPT")
DATA="$ROOT/data"
mkdir -p "$DATA"

MOCHILA_VERSION=$(cat VERSION)

echo "Running mochila:$MOCHILA_VERSION with data stored in $DATA"

docker run -d -p 8888:8888 -p 8765:8765 -p 8529:8529 \
    --mount type=bind,source="$DATA",target=/opt/data \
    --name mochila \
    "mochila:$MOCHILA_VERSION"
