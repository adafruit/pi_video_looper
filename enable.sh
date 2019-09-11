#!/bin/sh

# Make sure script is run as root.
if [ "$(id -u)" != "0" ]; then
  echo "Must be run as root with sudo! Try: sudo ./enable.sh"
  exit 1
fi

# Disable any supervisor process that start video looper.
mv /etc/supervisor/conf.d/video_looper.conf.disabled /etc/supervisor/conf.d/video_looper.conf
supervisorctl reload
