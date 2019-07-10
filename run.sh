#!/usr/bin/env bash

source ~/env3/bin/activate

export FLASK_ENV=development
export FLASK_APP=run.py

flask run --port 5000 --host 0.0.0.0
