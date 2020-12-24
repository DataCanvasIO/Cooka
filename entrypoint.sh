#!/bin/bash

echo "NOTEBOOK_PORTAL=$NOTEBOOK_PORTAL"

COOKA_DATA_HOME=/root/cooka
mkdir -p $COOKA_DATA_HOME

# 1. start notebook
nohup  jupyter-lab --ip=0.0.0.0 --no-browser --allow-root --NotebookApp.token=  $COOKA_DATA_HOME  >/root/notebook.log 2>&1 &

# 2. start cooka server
mkdir -p /root/.config/cooka
echo "c.CookaApp.notebook_portal = \"$NOTEBOOK_PORTAL\"" > /root/.config/cooka/cooka.py

cooka server
