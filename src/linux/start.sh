#!/bin/sh

sudo cp $1 /lib/systemd/system/
sudo systemctl enable $2
sudo systemctl start $2
