# pi_video_looper
An application to turn your Raspberry Pi into a dedicated looping video playback device.
Can be used in art installations, fairs, theatre, events, infoscreens, advertisment etc...

Easy to use out of the box but also has a lot of settings to make it fit your use case.

If you miss a feature just post an issue on github. (https://github.com/adafruit/pi_video_looper)

## Changelog

#### new in v1.0.2:
 - in directory mode the directory is now monitored;
   if the number of files have changed the playlist is regenerated
 - some defaults have changed
 - new option for the countdown time (default is now 5 seconds)
 - new option for a wait time between videos (default is 0 seconds)
 - tweaks to the install script (skip the build of hello_video by using (sudo ./install.sh no_hello_video))
 - cleanup of the directory structure
 - added enable.sh analogous to disable.sh
 - added ntfs and exfat support for the usb drive
  
#### new in v1.0.1:
 - reworked for python3
 - keyboard control (quiting the player)
 - option for displaying an image instead of a blank screen between videos
    
#### how to install:
sudo ./install.sh

for a detailed tutorial visit: https://learn.adafruit.com/raspberry-pi-video-looper/installation
