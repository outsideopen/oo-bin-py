#!/usr/bin/env bash

if [[ $(uname -r) =~ "microsoft-standard" ]]; then
  PLATFORM=windows
elif [[ $(uname -s) =~ "Linux" ]]; then
  PLATFORM=linux
elif [[ $(uname -s) =~ "Darwin" ]]; then
  PLATFORM=mac
fi

if pytest -s tests/manual_tests/; then
  SUCCESS=true
else
  SUCCESS=false
fi

echo "{\"platform\": \"$PLATFORM\", \"success\":\"$SUCCESS\"}" | gh workflow run manual_tests.yml --json --ref $(git rev-parse --abbrev-ref HEAD)

