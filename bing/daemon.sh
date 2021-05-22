#!/usr/bin/env sh

set -eu

cd "$(dirname "$0")" || exit 1


while true
do
  ./bing.py "$@"
  sleep 3600
done
