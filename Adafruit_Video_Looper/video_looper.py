# Copyright 2015 Adafruit Industries.
# Author: Tony DiCola
# License: GNU GPLv2, see LICENSE.txt

import configparser
import importlib
import os
import re
import subprocess
import sys
import signal
import time
import pygame
import threading
from datetime import datetime

from .alsa_config import parse_hw_device
from .model import Playlist, Movie
from .playlist_builders import build_playlist_m3u


# Basic video looper architecure:
#
# - VideoLooper class contains all the main logic for running the looper program.
#
# - Almost all state is configured in a .ini config file which is required for
#   loading and using the VideoLooper class.
#
# - VideoLooper has loose coupling with file reader and video player classes that
#   are used to find movie files and play videos respectively.  The configuration
#   defines which file reader and video player module will be loaded.
#
# - A file reader module needs to define at top level create_file_reader function
#   that takes as a parameter a ConfigParser config object.  The function should
#   return an instance of a file reader class.  See usb_drive.py and directory.py
#   for the two provided file readers and their public interface.
#
# - Similarly a video player modules needs to define a top level create_player
#   function that takes in configuration.  See omxplayer.py and hello_video.py
#   for the two provided video players and their public interface.
#
# - Future file readers and video players can be provided and referenced in the
#   config to extend the video player use to read from different file sources
#   or use different video players.
class VideoLooper:

    def __init__(self, config_path):
        """Create an instance of the main video looper application class. Must
        pass path to a valid video looper ini configuration file.
        """
        # Load the configuration.
        self._config = configparser.ConfigParser()
        if len(self._config.read(config_path)) == 0:
            raise RuntimeError('Failed to find configuration file at {0}, is the application properly installed?'.format(config_path))
        self._console_output = self._config.getboolean('video_looper', 'console_output')
        # Load other configuration values.
        self._osd = self._config.getboolean('video_looper', 'osd')
        self._is_random = self._config.getboolean('video_looper', 'is_random')
        self._resume_playlist = self._config.getboolean('video_looper', 'resume_playlist') 
        self._keyboard_control = self._config.getboolean('video_looper', 'keyboard_control')
        # Get seconds for countdown from config
        self._countdown_time = self._config.getint('video_looper', 'countdown_time')
        # Get seconds for waittime bewteen files from config
        self._wait_time = self._config.getint('video_looper', 'wait_time')
        # Parse string of 3 comma separated values like "255, 255, 255" into
        # list of ints for colors.
        self._bgcolor = list(map(int, self._config.get('video_looper', 'bgcolor')
                                             .translate(str.maketrans('','', ','))
                                             .split()))
        self._fgcolor = list(map(int, self._config.get('video_looper', 'fgcolor')
                                             .translate(str.maketrans('','', ','))
                                             .split()))
        # Initialize pygame and display a blank screen.
        pygame.display.init()
        pygame.font.init()
        pygame.mouse.set_visible(False)
        self._screen = pygame.display.set_mode((0,0), pygame.FULLSCREEN | pygame.NOFRAME)
        self._size = (pygame.display.Info().current_w, pygame.display.Info().current_h)
        self._bgimage = self._load_bgimage()
        self._blank_screen()
        # Load configured video player and file reader modules.
        self._player = self._load_player()
        self._reader = self._load_file_reader()
        # Load ALSA hardware configuration.
        self._alsa_hw_device = parse_hw_device(self._config.get('alsa', 'hw_device'))
        self._alsa_hw_vol_control = self._config.get('alsa', 'hw_vol_control')
        self._alsa_hw_vol_file = self._config.get('alsa', 'hw_vol_file')
        # default ALSA hardware volume (volume will not be changed)
        self._alsa_hw_vol = None
        # Load sound volume file name value
        self._sound_vol_file = self._config.get('omxplayer', 'sound_vol_file')
        # default value to 0 millibels (omxplayer)
        self._sound_vol = 0
        # Set other static internal state.
        self._extensions = '|'.join(self._player.supported_extensions())
        self._small_font = pygame.font.Font(None, 50)
        self._big_font   = pygame.font.Font(None, 250)
        self._running    = True
        self._playbackStopped = False
        #used for not waiting the first time
        self._firstStart = True

        # start keyboard handler thread:
        # Event handling for key press, if keyboard control is enabled
        if self._keyboard_control:
            self._keyboard_thread = threading.Thread(target=self._handle_keyboard_shortcuts, daemon=True)
            self._keyboard_thread.start()

    def _print(self, message):
        """Print message to standard output if console output is enabled."""
        if self._console_output:
            now = datetime.now()
            print("[{}] {}".format(now, message))

    def _load_player(self):
        """Load the configured video player and return an instance of it."""
        module = self._config.get('video_looper', 'video_player')
        return importlib.import_module('.' + module, 'Adafruit_Video_Looper').create_player(self._config)

    def _load_file_reader(self):
        """Load the configured file reader and return an instance of it."""
        module = self._config.get('video_looper', 'file_reader')
        return importlib.import_module('.' + module, 'Adafruit_Video_Looper').create_file_reader(self._config, self._screen)

    def _load_bgimage(self):
        """Load the configured background image and return an instance of it."""
        image = None
        if self._config.has_option('video_looper', 'bgimage'):
            imagepath = self._config.get('video_looper', 'bgimage')
            if imagepath != "" and os.path.isfile(imagepath):
                self._print('Using ' + str(imagepath) + ' as a background')
                image = pygame.image.load(imagepath)
                image = pygame.transform.scale(image, self._size)
        return image

    def _is_number(self, s):
        try:
            float(s) 
            return True
        except ValueError:
            return False

    def _build_playlist(self):
        """Try to build a playlist (object) from a playlist (file).
        Falls back to an auto-generated playlist with all files.
        """
        if self._config.has_option('playlist', 'path'):
            playlist_path = self._config.get('playlist', 'path')
            if playlist_path != "":
                if os.path.isabs(playlist_path):
                    if not os.path.isfile(playlist_path):
                        self._print('Playlist path {0} does not exist.'.format(playlist_path))
                        return self._build_playlist_from_all_files()
                        #raise RuntimeError('Playlist path {0} does not exist.'.format(playlist_path))
                else:
                    paths = self._reader.search_paths()
                    
                    if not paths:
                        return Playlist([])
                    
                    for path in paths:
                        maybe_playlist_path = os.path.join(path, playlist_path)
                        if os.path.isfile(maybe_playlist_path):
                            playlist_path = maybe_playlist_path
                            self._print('Playlist path resolved to {0}.'.format(playlist_path))
                            break
                    else:
                        self._print('Playlist path {0} does not resolve to any file.'.format(playlist_path))
                        return self._build_playlist_from_all_files()
                        #raise RuntimeError('Playlist path {0} does not resolve to any file.'.format(playlist_path))

                basepath, extension = os.path.splitext(playlist_path)
                if extension == '.m3u' or extension == '.m3u8':
                    return build_playlist_m3u(playlist_path)
                else:
                    self._print('Unrecognized playlist format {0}.'.format(extension))
                    return self._build_playlist_from_all_files()
                    #raise RuntimeError('Unrecognized playlist format {0}.'.format(extension))
            else:
                return self._build_playlist_from_all_files()
        else:
            return self._build_playlist_from_all_files()

    def _build_playlist_from_all_files(self):
        """Search all the file reader paths for movie files with the provided
        extensions.
        """
        # Get list of paths to search from the file reader.
        paths = self._reader.search_paths()
        # Enumerate all movie files inside those paths.
        movies = []
        for path in paths:
            # Skip paths that don't exist or are files.
            if not os.path.exists(path) or not os.path.isdir(path):
                continue

            for x in os.listdir(path):
                # Ignore hidden files (useful when file loaded on usb key from an OSX computer
                if x[0] != '.' and re.search('\.({0})$'.format(self._extensions), x, flags=re.IGNORECASE):
                    repeatsetting = re.search('_repeat_([0-9]*)x', x, flags=re.IGNORECASE)
                    if (repeatsetting is not None):
                        repeat = repeatsetting.group(1)
                    else:
                        repeat = 1
                    basename, extension = os.path.splitext(x)
                    movies.append(Movie('{0}/{1}'.format(path.rstrip('/'), x), basename, repeat))

            # Get the ALSA hardware volume from the file in the usb key
            if self._alsa_hw_vol_file:
                alsa_hw_vol_file_path = '{0}/{1}'.format(path.rstrip('/'), self._alsa_hw_vol_file)
                if os.path.exists(alsa_hw_vol_file_path):
                    with open(alsa_hw_vol_file_path, 'r') as alsa_hw_vol_file:
                        alsa_hw_vol_string = alsa_hw_vol_file.readline()
                        self._alsa_hw_vol = alsa_hw_vol_string
                    
            # Get the video volume from the file in the usb key
            if self._sound_vol_file:
                sound_vol_file_path = '{0}/{1}'.format(path.rstrip('/'), self._sound_vol_file)
                if os.path.exists(sound_vol_file_path):
                    with open(sound_vol_file_path, 'r') as sound_file:
                        sound_vol_string = sound_file.readline()
                        if self._is_number(sound_vol_string):
                            self._sound_vol = int(float(sound_vol_string))
        # Create a playlist with the sorted list of movies.
        return Playlist(sorted(movies))

    def _blank_screen(self):
        """Render a blank screen filled with the background color."""
        self._screen.fill(self._bgcolor)
        if self._bgimage is not None:
            rect = self._bgimage.get_rect()
            self._screen.blit(self._bgimage, rect)
        pygame.display.update()

    def _render_text(self, message, font=None):
        """Draw the provided message and return as pygame surface of it rendered
        with the configured foreground and background color.
        """
        # Default to small font if not provided.
        if font is None:
            font = self._small_font
        return font.render(message, True, self._fgcolor, self._bgcolor)

    def _animate_countdown(self, playlist):
        """Print text with the number of loaded movies and a quick countdown
        message if the on screen display is enabled.
        """
        # Print message to console with number of movies in playlist.
        message = 'Found {0} movie{1}.'.format(playlist.length(), 
            's' if playlist.length() >= 2 else '')
        self._print(message)
        # Do nothing else if the OSD is turned off.
        if not self._osd:
            return
        # Draw message with number of movies loaded and animate countdown.
        # First render text that doesn't change and get static dimensions.
        label1 = self._render_text(message + ' Starting playback in:')
        l1w, l1h = label1.get_size()
        sw, sh = self._screen.get_size()
        for i in range(self._countdown_time, 0, -1):
            # Each iteration of the countdown rendering changing text.
            label2 = self._render_text(str(i), self._big_font)
            l2w, l2h = label2.get_size()
            # Clear screen and draw text with line1 above line2 and all
            # centered horizontally and vertically.
            self._screen.fill(self._bgcolor)
            self._screen.blit(label1, (sw/2-l1w/2, sh/2-l2h/2-l1h))
            self._screen.blit(label2, (sw/2-l2w/2, sh/2-l2h/2))
            pygame.display.update()
            # Pause for a second between each frame.
            time.sleep(1)

    def _idle_message(self):
        """Print idle message from file reader."""
        # Print message to console.
        message = self._reader.idle_message()
        self._print(message)
        # Do nothing else if the OSD is turned off.
        if not self._osd:
            return
        # Display idle message in center of screen.
        label = self._render_text(message)
        lw, lh = label.get_size()
        sw, sh = self._screen.get_size()
        self._screen.fill(self._bgcolor)
        self._screen.blit(label, (sw/2-lw/2, sh/2-lh/2))
        # If keyboard control is enabled, display message about it
        if self._keyboard_control:
            label2 = self._render_text('press ESC to quit')
            l2w, l2h = label2.get_size()
            self._screen.blit(label2, (sw/2-l2w/2, sh/2-l2h/2+lh))
        pygame.display.update()

    def display_message(self,message):
        self._print(message)
        # Do nothing else if the OSD is turned off.
        if not self._osd:
            return
        # Display idle message in center of screen.
        label = self._render_text(message)
        lw, lh = label.get_size()
        sw, sh = self._screen.get_size()
        self._screen.fill(self._bgcolor)
        self._screen.blit(label, (sw/2-lw/2, sh/2-lh/2))
        pygame.display.update()

    def _prepare_to_run_playlist(self, playlist):
        """Display messages when a new playlist is loaded."""
        # If there are movies to play show a countdown first (if OSD enabled),
        # or if no movies are available show the idle message.
        self._blank_screen()
        self._firstStart = True
        if playlist.length() > 0:
            self._animate_countdown(playlist)
            self._blank_screen()
        else:
            self._idle_message()

    def _set_hardware_volume(self):
        if self._alsa_hw_vol != None:
            msg = 'setting hardware volume (device: {}, control: {}, value: {})'
            self._print(msg.format(
                self._alsa_hw_device,
                self._alsa_hw_vol_control,
                self._alsa_hw_vol
            ))
            cmd = ['amixer', '-M']
            if self._alsa_hw_device != None:
                cmd.extend(('-c', str(self._alsa_hw_device[0])))
            cmd.extend(('set', self._alsa_hw_vol_control, '--', self._alsa_hw_vol))
            subprocess.check_call(cmd)
            
    def _handle_keyboard_shortcuts(self):
        while self._running:
            event = pygame.event.wait()
            if event.type == pygame.KEYDOWN:
                # If pressed key is ESC quit program
                if event.key == pygame.K_ESCAPE:
                    self._print("ESC was pressed. quitting...")
                    self.quit()
                if event.key == pygame.K_k:
                    self._print("k was pressed. skipping...")
                    self._player.stop(3)
                if event.key == pygame.K_s:
                    if self._playbackStopped:
                        self._print("s was pressed. starting...")
                        self._playbackStopped = False
                    else:
                        self._print("s was pressed. stopping...")
                        self._playbackStopped = True
                        self._player.stop(3)
                if event.key == pygame.K_p:
                    self._print("p was pressed. shutting down...")
                    self.quit(True)
                    


    def run(self):
        """Main program loop.  Will never return!"""
        # Get playlist of movies to play from file reader.
        playlist = self._build_playlist()
        self._prepare_to_run_playlist(playlist)
        self._set_hardware_volume()
        movie = playlist.get_next(self._is_random, self._resume_playlist)
        # Main loop to play videos in the playlist and listen for file changes.
        while self._running:
            # Load and play a new movie if nothing is playing.
            if not self._player.is_playing() and not self._playbackStopped:
                if movie is not None: #just to avoid errors

                    if movie.playcount >= movie.repeats:
                        movie.clear_playcount()
                        movie = playlist.get_next(self._is_random, self._resume_playlist)
                    elif self._player.can_loop_count() and movie.playcount > 0:
                        movie.clear_playcount()
                        movie = playlist.get_next(self._is_random, self._resume_playlist)

                    movie.was_played()

                    if self._wait_time > 0 and not self._firstStart:
                        self._print('Waiting for: {0} seconds'.format(self._wait_time))
                        time.sleep(self._wait_time)
                    self._firstStart = False

                    #generating infotext
                    if self._player.can_loop_count():
                        infotext = '{0} time{1} (player counts loops)'.format(movie.repeats, "s" if movie.repeats>1 else "")
                    else:
                        infotext = '{0}/{1}'.format(movie.playcount, movie.repeats)
                    if playlist.length()==1:
                        infotext = '(endless loop)'

                    # Start playing the first available movie.
                    self._print('Playing movie: {0} {1}'.format(movie, infotext))
                    # todo: maybe clear screen to black so that background (image/color) is not visible for videos with a resolution that is < screen resolution
                    self._player.play(movie, loop=-1 if playlist.length()==1 else None, vol = self._sound_vol)

            # Check for changes in the file search path (like USB drives added)
            # and rebuild the playlist.
            if self._reader.is_changed() and not self._playbackStopped:
                self._print("reader changed, stopping player")
                self._player.stop(3)  # Up to 3 second delay waiting for old 
                                      # player to stop.
                self._print("player stopped")
                # Rebuild playlist and show countdown again (if OSD enabled).
                playlist = self._build_playlist()
                self._prepare_to_run_playlist(playlist)
                self._set_hardware_volume()
                movie = playlist.get_next(self._is_random, self._resume_playlist)

            # Give the CPU some time to do other tasks. low values increase "responsiveness to changes" and reduce the pause between files
            # but increase CPU usage
            # since keyboard commands are handled in a seperate thread this sleeptime mostly influences the pause between files
                        
            time.sleep(0.002)

    def quit(self, shutdown=False):
        """Shut down the program"""
        self._print("quitting Video Looper")
        self._playbackStopped = True
        if self._player is not None:
            self._player.stop()
        pygame.quit()
        if shutdown:
            os.system("sudo shutdown now")
        self._running = False



    def signal_quit(self, signal, frame):
        """Shut down the program, meant to by called by signal handler."""
        self._print("received signal to quit")
        self.quit()

# Main entry point.
if __name__ == '__main__':
    print('Starting Adafruit Video Looper.')
    # Default config path to /boot.
    config_path = '/boot/video_looper.ini'
    # Override config path if provided as parameter.
    if len(sys.argv) == 2:
        config_path = sys.argv[1]
    # Create video looper.
    videolooper = VideoLooper(config_path)
    # Configure signal handlers to quit on TERM or INT signal.
    signal.signal(signal.SIGTERM, videolooper.signal_quit)
    signal.signal(signal.SIGINT, videolooper.signal_quit)
    # Run the main loop.
    videolooper.run()
