# pi_video_looper
An application to turn your Raspberry Pi into a dedicated looping video playback device.
Can be used in art installations, fairs, theatre, events, infoscreens, advertisment etc...

Easy to use out of the box but also has a lot of settings to make it fit your use case.

If you miss a feature just post an issue on github. (https://github.com/adafruit/pi_video_looper)

## Changelog

#### new in v1.0.4
 - new keyboard shortcut "k"  
   skips the playback of current video (if a video is set to repeat it only skips one iteration)
 - new keyboard shortcut "s"
   stops the current playback. pressing s again starts the playback
 - reworked shortcut handling 
 

#### new in v1.0.3
 - **major new feature:** copymode  
 files will be copied from the usb stick to the player (with fancy progress bar)  
 you can choose if the current files should be deleted beforehand (replace mode is default) 
 or if files from the stick should be added (add mode)  
 the copymode is protected with a "password" which is represented with a file on the drive (set it via the video_looper.ini
 for more infos see "copymode explained below" 
 
 - advanced playlist feature: add _repeat_Nx to any filename (N is a positive integer) and file will be looped that many times
  (additional infos see below)
 - added reload.sh to restart the looper and reload the settings from the ini

#### new in v1.0.2:
 - in directory mode the directory is now monitored;
   if the number of files changes the playlist is regenerated (usefull if the folder is filled e.g. via a network share)
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


#### copymode explained:
when a usb drive with video files is plugged in, they are copied onto the rpi. (with progress bar)

to protect the player from unauthorised drives a file must be present on the drive that has a filename 
as defined in the password setting in the ini file (default: videopi)

there is also a setting that controls, if files on the drive should replace the existing files or get added. (replace means that the videofiles on the rpi get deleted)
this ini setting can be overruled by placing a file named "replace" or "add" on the drive.
the default mode is "replace"

Note: files with the same name always get overwritten

#### notable things:
* you can have one video repeated X times before playing the next by adding _repeat_Nx to the filename of a video ,
where N is a positive number
    * with hello_video there is no gap when a video is repeated but there is a small gap between different videos
    * with omxplayer there will also be a short gap between the repeats
    
* if you have only one video then omxplayer can also loop seamlessly (and wth audio)


#### trouble shooting:
* nothing happening (screen flashes once) when in copymode and new drive is plugged in?
    * check if you have the "password file" on your drive (see copymode explained above)

for a detailed tutorial visit: https://learn.adafruit.com/raspberry-pi-video-looper/installation
