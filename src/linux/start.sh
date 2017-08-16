#!/bin/bash

DIR="$(dirname "$(dirname "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)")")"
sed "s|%INSTALL_DIR%|${DIR}|g" "$1" > temp
sudo cp temp "/lib/systemd/system/$2"
sudo systemctl enable $2
sudo systemctl start $2
rm temp
