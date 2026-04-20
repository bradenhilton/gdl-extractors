#!/usr/bin/env sh
set -eu

MAX_ATTEMPTS=3
DELAY=10

if [ "$#" -lt 1 ]; then
    printf '%s\n' "Usage: retry.sh <command...>"
    exit 2
fi

attempt=1

while :; do
    printf 'Attempt %d/%d: ' "$attempt" "$MAX_ATTEMPTS"
    printf '%s\n' "$*"

    if "$@"; then
        printf '%s\n' "Command succeeded"
        exit 0
    fi

    if [ "$attempt" -ge "$MAX_ATTEMPTS" ]; then
        printf '%s\n' "All attempts failed"
        exit 1
    fi

    printf 'Retrying in %d seconds...\n' "$DELAY"
    sleep "$DELAY"

    attempt=$((attempt + 1))
done
