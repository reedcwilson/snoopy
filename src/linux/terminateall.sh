#!/usr/bin/env bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

${DIR}/stop.sh snoopy.service &
${DIR}/stop.sh sidecar.service &
