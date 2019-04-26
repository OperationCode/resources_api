#!/usr/bin/env bash

function isDryRun {
  if [ "$DRYRUN" = "1" ]; then
    return 0
  else
    return 1
  fi
}

function runCommand {
  if isDryRun; then
    echo $1;
  else
    eval $1
    return $?
  fi
}
