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
apt-get update
apt-get -y install build-essential python-dev python-pip python-pygame supervisor git

echo "Installing omxplayer..."
echo "======================="
if [ -f "omxplayer-dist.tgz" ]; then
  rm omxplayer-dist.tgz
fi
wget https://github.com/adafruit/omxplayer/releases/download/2%2F10%2F2015/omxplayer-dist.tgz
tar xvfz omxplayer-dist.tgz -C /

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
python setup.py install --force
cp video_looper.ini /boot/video_looper.ini

echo "Configuring video_looper to run on start..."
echo "==========================================="
cp video_looper.conf /etc/supervisor/conf.d/
service supervisor restart

echo "Finished!"
