#!/bin/sh

# Make sure script is run as root.
if [ "$(id -u)" != "0" ]; then
  echo "Must be run as root with sudo! Try: sudo ./enable.sh"
  exit 1
fi

# enable and start video_looper service
systemctl enable video_looper
systemctl start video_looper 