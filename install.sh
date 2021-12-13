#!/bin/sh

# Make sure script is run as root.
if [ "$(id -u)" != "0" ]; then
  echo "Must be run as root with sudo! Try: sudo ./install.sh"
  exit 1
fi

echo "Configuring device tree overlays..."
echo "==================================="

# VLC requires "fake" KMS overlay to work in Bullseye.
# Check /boot/config.txt for vc4-fkms-v3d overlay present and active.
# If so, nothing to do here, module's already configured.
PROMPT_FOR_REBOOT=0
grep '^dtoverlay=vc4-fkms-v3d' /boot/config.txt >/dev/null
if [ $? -ne 0 ]; then
  # fkms overlay not present, or is commented out. Check if vc4-kms-v3d
  # (no 'f') is present and active. That's normally the default.
  grep '^dtoverlay=vc4-kms-v3d' /boot/config.txt >/dev/null
  if [ $? -eq 0 ]; then
    # It IS present. Comment out that line, and insert the 'fkms' item
    # on the next line.
    sed -i "s/^dtoverlay=vc4-kms-v3d/#&\ndtoverlay=vc4-fkms-v3d/g" /boot/config.txt >/dev/null
  else
    # It's NOT present. Silently append 'fkms' overlay to end of file.
    echo dtoverlay=vc4-fkms-v3d | sudo tee -a /boot/config.txt >/dev/null
  fi
  # Any change or addition of overlay will require a reboot when done.
  PROMPT_FOR_REBOOT=1
fi

# Error out if anything fails. Must be set AFTER grep calls above.
set -e

echo "Updating system..."
echo "=================="
apt update && apt upgrade -y

echo "Installing dependencies..."
echo "=========================="
apt -y install python3 python3-pip python3-pygame supervisor ntfs-3g exfat-fuse vlc

echo "Installing video_looper program..."
echo "=================================="

# change the directoy to the script location
cd "$(dirname "$0")"

mkdir -p /mnt/usbdrive0 # This is very important if you put your system in readonly after
mkdir -p /home/pi/video # create default video directory

pip3 install setuptools
python3 setup.py install --force

cp ./assets/video_looper.ini /boot/video_looper.ini

echo "Configuring video_looper to run on start..."
echo "==========================================="

cp ./assets/video_looper.conf /etc/supervisor/conf.d/

echo "Finished!"

if [ $PROMPT_FOR_REBOOT -eq 1 ]; then
  echo
  echo "Settings take effect on next boot."
  echo
  echo -n "REBOOT NOW? [y/N] "
  read
  if [[ ! "$REPLY" =~ ^(yes|y|Y)$ ]]; then
    echo "Exiting without reboot."
  else
    echo "Reboot started..."
    reboot
  fi
else
  # No reboot needed; can start looper with current DTO config
  service supervisor restart
fi
