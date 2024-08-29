#!/bin/bash

export PYTHONPATH=$PWD/simple-search/:$PYTHONPATH
export FLASK_APP=simple-search/server/server.py
flask run --host=0.0.0.0 --port 8820
