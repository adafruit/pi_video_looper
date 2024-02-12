#!/bin/bash

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

# Error out if anything fails.
set -e

# Extra steps for DietPi installations
if id "pi" >/dev/null 2>&1; then
	echo "pi user exists"
else
    echo "Creating pi user"
	sudo useradd -m -u 1000 -G adm,audio,video,sudo,adm pi
	sudo mkdir -p /run/user/1000
	sudo chmod 700 /run/user/1000
fi

# old version cleanup
sudo supervisorctl stop video_looper &>/dev/null
sudo rm /etc/supervisor/conf.d/video_looper.conf &>/dev/null

echo "Installing dependencies..."
echo "=========================="
sudo apt update && sudo apt -y install python3 python3-pip python3-pygame omxplayer ntfs-3g exfat-fuse python3-wheel libsdl2-ttf-2.0-0 libsdl2-image-2.0-0

if [ "$*" != "no_hello_video" ]
then
	echo "Installing hello_video..."
	echo "========================="
	cd $SCRIPT_DIR
	sudo apt -y install git build-essential python3-dev
	git clone https://github.com/adafruit/pi_hello_video
	cd pi_hello_video
	./rebuild.sh
	cd hello_video
	sudo make install
	cd ../..
	rm -rf pi_hello_video
else
    echo "hello_video was not installed"
    echo "=========================="
fi

echo "Installing video_looper program..."
echo "=================================="

sudo mkdir -p /mnt/usbdrive0 # This is very important if you put your system in readonly after
sudo mkdir -p /home/pi/video # create default video directory
sudo chown pi:root /home/pi/video

sudo -u pi /usr/bin/python3 -m pip install --user --upgrade pip
sudo -u pi /usr/bin/python3 -m pip install --user $SCRIPT_DIR

sudo cp $SCRIPT_DIR/assets/video_looper.ini /boot/video_looper.ini

echo "Configuring video_looper to run on start..."
echo "==========================================="

sudo cp $SCRIPT_DIR/assets/video_looper.service /etc/systemd/system/video_looper.service
sudo chmod 644 /etc/systemd/system/video_looper.service

sudo systemctl daemon-reload
sudo systemctl enable video_looper
sudo systemctl start video_looper
sleep 1
sudo systemctl status video_looper

echo "Finished!"
