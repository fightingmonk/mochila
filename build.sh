#!/bin/sh

MOCHILA_VERSION=$(cat VERSION)

docker build -t "mochila:$MOCHILA_VERSION" .
