#!/bin/sh

# Make sure script is run as root.
if [ "$(id -u)" != "0" ]; then
  echo "Must be run as root with sudo! Try: sudo ./reload.sh"
  exit 1
fi

# reload settings by restarting the video_looper
supervisorctl restart video_looper