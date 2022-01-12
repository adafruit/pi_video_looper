# pi_video_looper
An application to turn your Raspberry Pi into a dedicated looping video playback device.
Can be used in art installations, fairs, theatre, events, infoscreens, advertisment etc...

Easy to use out of the box but also has a lot of settings to make it fit your use case.

See the [video_looper.ini configuration file](https://github.com/christiansievers/pi_video_looper/blob/master/assets/video_looper.ini) for an overview of options. If you miss a feature just post an issue on Github. (https://github.com/adafruit/pi_video_looper)

Currently only Raspberry Pi OS Lite __(Legacy)__ is supported.
You can download it from here: https://www.raspberrypi.com/software/operating-systems/#raspberry-pi-os-legacy

There are also pre-compiled versions available from: https://videolooper.de/ (but they might not contain the latest version of pi_video_looper)

## Changelog
#### new in v1.0.10
 - NEW PLAYER: "Image Player" (beta)  
   The new player can display images instead of videos (slideshow).  
   Display duration and other options can be controlled via the "image_player" section in video_looper.ini  
   All other settings, like background image, color, wait time, copy mode, keyboard shortcuts, etc. should work as expected  
   Currently tested formats: jpg, gif, png (others might work also - you need to adapt the extensions setting)

#### new in v1.0.9
 - fixed: background image is reloaded in copymode without restart

#### new in v1.0.8
 - playlist resume option  
   when enabled will resume last played file on restart
 - console output now has a timestamp for easier event tracking
 - Keyboard key for shutdown added ("p")

#### new in v1.0.7
 - huge improvements to CPU utilisation with keyboard_control enabled
 - better randomness for random playback

#### new in v1.0.6

 - Support for OMXPlayer ALSA sound output.  
   Enabled by setting sound output for omxplayer to `alsa` in video_looper.ini. A new config key `alsa.hw_device` can be used to specify a non-default output device.
 - Support for ALSA hardware volume control.  
   The new config keys `alsa.hw_vol_file` and `alsa.hw_vol_control` can be used to set the output device volume in a text file provided with the videos.
 - The `sound_vol_file` functionality can now be disabled by leaving the config value empty.

#### new in v1.0.5

 - Support for M3U playlists.  
   To be enabled by specifying a playlist path in config key `playlist.path`. It can be absolute, or relative to the `file_reader`'s search directories (`directory`: path given, `usb_drive`: all USB drives' root).  
   Paths in the playlist can be absolute, or relative to the playlist's path.  
   Playlists can include a title for each item (`#EXTINF` directive); see next point.
   If something goes wrong with the playlist (file not found etc.) it will fall back to just play all files in the `file_reader` directory. (enable `console_output` for more info)
 - Support for video titles (OMXPlayer only).  
   Can display a text on top of the videos.  
   To be enabled by config key `omxplayer.show_titles`.
   Without a playlist file, titles are simply the videos' filename (without extension).  
   If a M3U playlist is used, then titles come from the playlist instead.
   
   An easy way to create M3U files is e.g. VLC. For an example m3u file see assets/example.m3u

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
 - keyboard control (quitting the player)
 - option for displaying an image instead of a blank screen between videos
    
#### how to install:
sudo ./install.sh

#### features and settings
To change the settings of the video looper (e.g. random playback) edit the `/boot/video_looper.ini` file via ssh with `sudo nano /boot/video_looper.ini` or directly on the RPis SD Card via a cardreader.

#### copymode explained:
when a usb drive with video files is plugged in, they are copied onto the rpi. (with progress bar)

to protect the player from unauthorised drives a file must be present on the drive that has a filename 
as defined in the password setting in the ini file (default: videopi)

there is also a setting that controls, if files on the drive should replace the existing files or get added. (replace means that the videofiles on the rpi get deleted)
this ini setting can be overruled by placing a file named "replace" or "add" on the drive.
the default mode is "replace"

Note: files with the same name always get overwritten

#### notable things:
* you can have one video repeated X times before playing the next by adding _repeat_Nx to the filename of a video, where N is a positive number
    * with hello_video there is no gap when a video is repeated but there is a small gap between different videos
    * with omxplayer there will also be a short gap between the repeats
    
* if you have only one video then omxplayer can also loop seamlessly (and with audio)
* the last supported Rasperry Pi OS image version is 2021-05-07 (https://downloads.raspberrypi.org/raspios_lite_armhf/images/raspios_lite_armhf-2021-05-28/2021-05-07-raspios-buster-armhf-lite.zip)

#### keyboard commands:
if enabled (via config file) the following keyboard commands are active:
* "ESC" - stops playback and exits video_looper
* "k" - sKip - stops the playback of current file and plays next file
* "s" - Stop/Start - stops or starts playback of current file
* "p" - Power off - stop playback and shutdown RPi

#### troubleshooting:
* nothing happening (screen flashes once) when in copymode and new drive is plugged in?
    * check if you have the "password file" on your drive (see copymode explained above)
* if enabled (via config file) log output can be found in `/var/log/supervisor/`
  You can use e.g. `tail -f /var/log/supervisor/*` to view the logs

for a detailed tutorial visit: https://learn.adafruit.com/raspberry-pi-video-looper/installation
