# pi_video_looper
An application to turn your Raspberry Pi into a dedicated looping video playback device.
Can be used in art installations, fairs, theatre, events, infoscreens, advertisements etc...

Works right out of the box, but also has a lot of customisation options to make it fit your use case. See the [video_looper.ini](https://github.com/adafruit/pi_video_looper/blob/master/assets/video_looper.ini) configuration file for an overview of options. 

If you miss a feature just post an issue here on Github. (https://github.com/adafruit/pi_video_looper)

Currently only the __Legacy__ version of Raspberry Pi OS Lite is supported.  
The last working image is this one:
<https://downloads.raspberrypi.com/raspios_oldstable_lite_armhf/images/raspios_oldstable_lite_armhf-2022-01-28/2022-01-28-raspios-buster-armhf-lite.zip>

If you need to run this image on PI 3A+ you need to add newer firmware files after the flashing.
Download firmware files from [here](https://github.com/raspberrypi/firmware/archive/refs/heads/stable.zip) and copy all the fixup*.dat and start*.elf from the boot folder of the zip to the boot folder of your SD card (overwriting existing files)

For a detailed tutorial visit: <https://learn.adafruit.com/raspberry-pi-video-looper/installation>  
There are also pre-compiled images available from <https://videolooper.de> (but they might not always contain the latest version of pi_video_looper)

## Changelog
#### new in v1.0.19
 - keyboard and gpio control can now be disabled while a video is running - makes the most sense together with the "one shot playback" setting

#### v1.0.18
 - fixed one-shot playback with only one video file
 - added option to not start video playback on looper startup (boot)

#### new in v1.0.17
 - GPIO pins can now be used to send "keyboard commands", i.e. to pause playback or shut down the system

#### new in v1.0.16
 - send previous/next chapter commands to omxplayer (o/i on keyboard)

#### new in v1.0.15
 - one shot playback: option to enable stopping playback after each file (usefull in combination with gpio triggers)

#### new in v1.0.14
 - control the video looper via RPI GPIO pins (see section "control" below)

#### new in v1.0.13
 - Additional date/time functionality added. 
   Allows you to add a second smaller line to display things like the date correctly.
 - pressing spacebar will pause/resume omxplayer and image_player
 
#### new in v1.0.12
 - date/time display option
   allows you to display the current date and time between the videos
 - added "back" keyboard shortcut to play previous file

#### v1.0.11
 - fixed skip bug with image_player
 - fixed possible dependency issue

#### new in v1.0.10
 - NEW PLAYER: "Image Player" (beta)  
   Displays images in a slideshow instead of playing videos.
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

 - Support for omxplayer ALSA sound output.  
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
 - Support for video titles (omxplayer only).  
   Can display a text on top of the videos.  
   To be enabled by config key `omxplayer.show_titles`.
   Without a playlist file, titles are simply the videos' filename (without extension).  
   If an M3U playlist is used, then titles come from the playlist instead.
   
   An easy way to create M3U files is e.g. VLC. For an example M3U file see assets/example.m3u

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
   if the number of files changes the playlist is regenerated (useful if the folder is filled e.g. via a network share)
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
    
## How to install
`sudo apt-get install git`  
`cd ~`  
`git clone https://github.com/adafruit/pi_video_looper`  
`cd pi_video_looper`  
`sudo ./install.sh`

Default player is omxplayer. Use the `no_hello_video` flag to install without the hello_video player (a bit faster to install):  
`sudo ./install.sh no_hello_video`

## How to update
An update is always like a fresh installation so you will loose custom changes made to the /boot/video_looper.ini   

For backing up the current ini:     
`sudo cp /boot/video_looper.ini /boot/video_looper.ini_backup`  

For the update:    
`cd ~`   
`sudo rm -rf pi_video_looper`   
`git clone https://github.com/adafruit/pi_video_looper`    
`cd pi_video_looper`   
`sudo ./install.sh` 

## Features and settings
To change the settings of the video looper (e.g. random playback, copy mode, GPIO control, advanced features) edit the `/boot/video_looper.ini` file, i.e. by quitting the player with 'ESC' and logging in to the Raspberry with an attached keyboard, or remotely via ssh. Then edit the configuration file with `sudo nano /boot/video_looper.ini`.

Alternatively insert the SD card into your computer and edit it with your preferred text editor. 

#### copymode explained:
By default, the looper plays any video files from a USB drive in alphabetical order. With copymode, you only need a USB drive once, to copy the video files directly onto the RPi's SD card. Once enabled in the video_looper.ini, all files from an attached USB drive are copied onto the RPi. A progress bar shows you, well, the progress of the operation.

To protect the player from unauthorised access you need to create a file on the drive called "videopi". The extension doesn't matter. This file acts as a password. (The wording of this "password" can be changed in the video_looper.ini)

You might also want to decide if new files on the drive should replace existing files or get added. "Replace" means that any existing videofiles on the RPi get deleted, and only the new files remain.  
This setting can be overruled by placing a file named "replace" or "add" on the drive.  
The default mode is "replace".  

Note: files with the same name always get overwritten.  

#### notable things:
* you can have one video repeated X times before playing the next by adding _repeat_Nx to the filename of a video, where N is a positive number
    * with hello_video there is no gap when a video is repeated but there is a small gap between different videos
    * with omxplayer there will also be a short gap between the repeats
    
* if you have only one video then omxplayer will also loop seamlessly (and with audio)

* to reduce the wear of the SD card and potentially extend the lifespan of the player, you could enable the overlay filesystem via `raspi-config` and select Performance Options->Overlay Filesystem

### Control
The video looper can be controlled via keyboard input or via configured GPIO pins. 
Keyboard control is enabled by default via the `keyboard_control` setting in the video_looper.ini file. 

#### keyboard commands:
The following keyboard commands are active by default (can be disabled in the [video_looper.ini](https://github.com/adafruit/pi_video_looper/blob/master/assets/video_looper.ini)):
* "ESC" - stops playback and exits video_looper
* "k" - sKip - stops the playback of current file and plays next file
* "b" - Back - stops the playback of current file and plays previous file
* "s" - Stop/Start - stops or starts playback of current file
* "p" - Power off - stop playback and shutdown RPi
* " " - (space bar) - Pause/Resume the omxplayer and imageplayer
* "o" - next chapter (only omxplayer)
* "i" - previous chapter (only omxplayer)

#### GPIO control:
To enable GPIO control you need to set a GPIO pin mapping via the `gpio_pin_map` in the `control` section of the video_looper.ini. 
Pins numbers are in "BOARD" numbering - see: https://www.raspberrypi.com/documentation/computers/raspberry-pi.html#gpio. Bridge a mapped pin with a Ground pin to trigger it.

The pin mapping has the form: "pinnumber" : "action”. The action can be one of the following:
* a filename as a string to play 
* an absolute index number (starting with 0) 
* a string in the form of `+n` or `-n` (with n being an integer) for a relative jump
* a keyboard command (see above) in the form of a pygame key constant (see list: https://www.pygame.org/docs/ref/key.html)

Here are some examples that can be set: 
* `"11" : 1`  -> pin 11 will start the second file in the playlist
* `"13" : "4"` -> pin 13 starts the 5th video
* `"16" : "+2"` -> pin 16 jumps 2 videos ahead
* `"18" : "-1"` -> pin 18 jumps one video back
* `"15" : "video.mp4"` -> pin 15 plays a file with name "video.mp4" (if it exists)
* `"19" : "K_SPACE"` -> pin 19 sends the "space" keyboard command, pausing the current video
* `"21" : "K_p"` -> pin 21 sends "p" keyboard command and thus triggers the shutdown of the Raspberry Pi

For your convenience, these exact mappings can be easily enabled by uncommenting the example line in the video_looper.ini. You can also define your own mappings.

Note: to be used as an absolute index the action needs to be an integer not a string.
Note 2: "keyboard_control" needs to be enabled in the ini for gpio to utilise keyboard commands.


## Troubleshooting:
* nothing happening (screen flashes once) when in copymode and new drive is plugged in?
    * check if you have the "password file" on your drive (see copymode explained above)
* log output can be found in `/var/log/supervisor/`. Enable detailed logging in the video_looper.ini with console_output = true.  
  Use `sudo tail -f /var/log/supervisor/video_looper-stdout*` and `sudo tail -f /var/log/supervisor/video_looper-stderr*` to view the logs.
* It’s currently doubtful if the pi_video_looper (which requires the legacy Raspberry Pi OS because of its omxplayer dependency) runs on the new Raspberry Pi 5.
