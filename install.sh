#!/bin/sh

# Error out if anything fails.
set -e

# Make sure script is run as root.
if [ "$(id -u)" != "0" ]; then
  echo "Must be run as root with sudo! Try: sudo ./install.sh"
  exit 1
fi

echo "Installing dependencies..."
echo "=========================="
apt update && apt -y git install build-essential python3-dev python3 python3-pip python3-pygame supervisor omxplayer

echo "Installing hello_video..."
echo "========================="
git clone https://github.com/adafruit/pi_hello_video.git
cd pi_hello_video
./rebuild.sh
cd hello_video
make install
cd ../..
rm -rf pi_hello_video

echo "Installing video_looper program..."
echo "=================================="
mkdir -p /mnt/usbdrive0 # This is very important if you put your system in readonly after
pip3 install setuptools
python3 setup.py install --force
cp video_looper.ini /boot/video_looper.ini

echo "Configuring video_looper to run on start..."
echo "==========================================="
cp video_looper.conf /etc/supervisor/conf.d/
service supervisor restart

echo "Finished!"
