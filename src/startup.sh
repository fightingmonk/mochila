#!/bin/sh

ARANGO_NO_AUTH=true /entrypoint.sh arangod --database.directory /opt/data &

/sbin/tini -- /usr/bin/jupyter notebook --ip=0.0.0.0 --port=8888 --no-browser --allow-root
