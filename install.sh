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
apt update && apt -y install python3 python3-pip python3-pygame supervisor omxplayer ntfs-3g exfat-fuse

if [ "$*" != "no_hello_video" ]
then
	echo "Installing hello_video..."
	echo "========================="
	apt -y install git build-essential python3-dev
	git clone https://github.com/adafruit/pi_hello_video
	cd pi_hello_video
	./rebuild.sh
	cd hello_video
	make install
	cd ../..
	rm -rf pi_hello_video
else
    echo "hello_video was not installed"
    echo "=========================="
fi

echo "Installing video_looper program..."
echo "=================================="

# change the directoy to the script location
cd "$(dirname "$0")"

mkdir -p /mnt/usbdrive0 # This is very important if you put your system in readonly after
mkdir -p /home/pi/video # create default video directory
chown pi:pi /home/pi/video

pip3 install setuptools
python3 setup.py install --force

cp ./assets/video_looper.ini /boot/video_looper.ini

echo "Configuring video_looper to run on start..."
echo "==========================================="

cp ./assets/video_looper.conf /etc/supervisor/conf.d/

service supervisor restart

echo "Do you want to install a splash screen and hide the default raspberry boot info? (y/n)"
read install_splash
if [ "$install_splash" = "y" ] || [ "$install_splash" = "Y" ]; then
	echo "Installing splash screen..."
	echo "==========================="

	apt install -y fbi

	echo '##videolooper settings' >> /boot/config.txt
	echo 'disable_splash=1' >> /boot/config.txt
	echo 'avoid_warnings=1' >> /boot/config.txt
	sed -i -e 's/rootwait/rootwait quiet splash loglevel=0 consoleblank=0 logo.nologo vt.global_cursor_default=0 plymouth.ignore-serial-consoles /' /boot/cmdline.txt
	sed -i  '/exit 0/i\#Suppress Kernel Messages\ndmesg --console-off\n' /etc/rc.local
	touch ~/.hushlogin
	systemctl disable getty@tty1

	cp ./assets/loader.png /home/pi/loader.png
	chown pi:pi /home/pi/loader.png
	cp ./assets/splashscreen.service /etc/systemd/system/splashscreen.service
	systemctl enable splashscreen

else
	echo "Skipping splash screen installation."
	echo "===================================="
fi

echo "Finished!"
