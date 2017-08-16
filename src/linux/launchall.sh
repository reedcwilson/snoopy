#!/usr/bin/env bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

${DIR}/start.sh ./config/snoopy.service snoopy.service
${DIR}/start.sh ./config/sidecar.service sidecar.service
