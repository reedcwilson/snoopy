#!/usr/bin/env bash

launchd_path="${HOME}/Library/LaunchAgents"
plist_filename='com.reedcwilson.collector.plist'
runtime_config_file="${launchd_path}/${plist_filename}"

temp_file="${plist_filename}.temp"
launchctl unload ${runtime_config_file} || true
sed -e "s|%INSTALL_DIR%|$(pwd)|g" ${plist_filename} > ${temp_file}
cp ${temp_file} ${runtime_config_file}
launchctl load ${runtime_config_file}