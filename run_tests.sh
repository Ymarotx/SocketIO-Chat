#!/bin/bash

echo 'Starting app...'
uvicorn main:app --reload &
APP_PID=$!

sleep 2

echo 'Starting tests...'
pytest -q --disable-warnings tests/

echo 'Stopping app...'
kill $APP_PID

echo 'Script finished.'

