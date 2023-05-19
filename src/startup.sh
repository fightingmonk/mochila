#!/bin/sh

# Start Arangodb
ARANGO_NO_AUTH=true /entrypoint.sh arangod --database.directory /opt/data &

# Start curated ui
cd /opt/viewer && /sbin/tini -- solara run --host 0.0.0.0 --no-access-log /opt/viewer/viewer.py &

# Start jupyter notebook
/sbin/tini -- /usr/bin/jupyter notebook --ip=0.0.0.0 --port=8888 --no-browser --allow-root
