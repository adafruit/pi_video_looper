# Copyright 2015 Adafruit Industries.
# Author: Tony DiCola
# License: GNU GPLv2, see LICENSE.txt
import ConfigParser
import importlib
import os
import re
import sys
import signal
import time

import pygame

from model import Playlist


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
class VideoLooper(object):

    def __init__(self, config_path):
        """Create an instance of the main video looper application class. Must
        pass path to a valid video looper ini configuration file.
        """
        # Load the configuration.
        self._config = ConfigParser.SafeConfigParser()
        if len(self._config.read(config_path)) == 0:
            raise RuntimeError('Failed to find configuration file at {0}, is the application properly installed?'.format(config_path))
        self._console_output = self._config.getboolean('video_looper', 'console_output')
        # Load configured video player and file reader modules.
        self._player = self._load_player()
        self._reader = self._load_file_reader()
        # Load other configuration values.
        self._osd = self._config.getboolean('video_looper', 'osd')
        self._is_random = self._config.getboolean('video_looper', 'is_random')
        # Parse string of 3 comma separated values like "255, 255, 255" into 
        # list of ints for colors.
        self._bgcolor = map(int, self._config.get('video_looper', 'bgcolor') \
                                             .translate(None, ',') \
                                             .split())
        self._fgcolor = map(int, self._config.get('video_looper', 'fgcolor') \
                                             .translate(None, ',') \
                                             .split())
        # Load sound volume file name value
        self._sound_vol_file = self._config.get('omxplayer', 'sound_vol_file');
        # default value to 0 millibels (omxplayer)
        self._sound_vol = 0
        # Initialize pygame and display a blank screen.
        pygame.display.init()
        pygame.font.init()
        pygame.mouse.set_visible(False)
        size = (pygame.display.Info().current_w, pygame.display.Info().current_h)
        self._screen = pygame.display.set_mode(size, pygame.FULLSCREEN)
        self._blank_screen()
        # Set other static internal state.
        self._extensions = self._player.supported_extensions()
        self._small_font = pygame.font.Font(None, 50)
        self._big_font   = pygame.font.Font(None, 250)
        self._running    = True

    def _print(self, message):
        """Print message to standard output if console output is enabled."""
        if self._console_output:
            print(message)

    def _load_player(self):
        """Load the configured video player and return an instance of it."""
        module = self._config.get('video_looper', 'video_player')
        return importlib.import_module('.' + module, 'Adafruit_Video_Looper') \
            .create_player(self._config)

    def _load_file_reader(self):
        """Load the configured file reader and return an instance of it."""
        module = self._config.get('video_looper', 'file_reader')
        return importlib.import_module('.' + module, 'Adafruit_Video_Looper') \
            .create_file_reader(self._config)

    def _is_number(iself, s):
        try:
            float(s) 
            return True
        except ValueError:
            return False
    
    def _build_playlist(self):
        """Search all the file reader paths for movie files with the provided
        extensions.
        """
        # Get list of paths to search from the file reader.
        paths = self._reader.search_paths()
        # Enumerate all movie files inside those paths.
        movies = []
        for ex in self._extensions:
            for path in paths:
                # Skip paths that don't exist or are files.
                if not os.path.exists(path) or not os.path.isdir(path):
                    continue
                # Ignore hidden files (useful when file loaded on usb
                # key from an OSX computer
                movies.extend(['{0}/{1}'.format(path.rstrip('/'), x) \
                               for x in os.listdir(path) \
                               if re.search('\.{0}$'.format(ex), x, 
                                            flags=re.IGNORECASE) and \
                               x[0] is not '.'])
                # Get the video volume from the file in the usb key
                sound_vol_file_path = '{0}/{1}'.format(path.rstrip('/'), self._sound_vol_file)
                if os.path.exists(sound_vol_file_path):
                    with open(sound_vol_file_path, 'r') as sound_file:
                        sound_vol_string = sound_file.readline()
                        if self._is_number(sound_vol_string):
                            self._sound_vol = int(float(sound_vol_string))
        # Create a playlist with the sorted list of movies.
        return Playlist(sorted(movies), self._is_random)

    def _blank_screen(self):
        """Render a blank screen filled with the background color."""
        self._screen.fill(self._bgcolor)
        pygame.display.update()

    def _render_text(self, message, font=None):
        """Draw the provided message and return as pygame surface of it rendered
        with the configured foreground and background color.
        """
        # Default to small font if not provided.
        if font is None:
            font = self._small_font
        return font.render(message, True, self._fgcolor, self._bgcolor)

    def _animate_countdown(self, playlist, seconds=10):
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
        for i in range(seconds, 0, -1):
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
        pygame.display.update()

    def _prepare_to_run_playlist(self, playlist):
        """Display messages when a new playlist is loaded."""
        # If there are movies to play show a countdown first (if OSD enabled),
        # or if no movies are available show the idle message.
        if playlist.length() > 0:
            self._animate_countdown(playlist)
            self._blank_screen()
        else:
            self._idle_message()

    def run(self):
        """Main program loop.  Will never return!"""
        # Get playlist of movies to play from file reader.
        playlist = self._build_playlist()
        self._prepare_to_run_playlist(playlist)
        # Main loop to play videos in the playlist and listen for file changes.
        while self._running:
            # Load and play a new movie if nothing is playing.
            if not self._player.is_playing():
                movie = playlist.get_next()
                if movie is not None:
                    # Start playing the first available movie.
                    self._print('Playing movie: {0}'.format(movie))
                    self._player.play(movie, loop=playlist.length() == 1, vol = self._sound_vol)
            # Check for changes in the file search path (like USB drives added)
            # and rebuild the playlist.
            if self._reader.is_changed():
                self._player.stop(3)  # Up to 3 second delay waiting for old 
                                      # player to stop.
                # Rebuild playlist and show countdown again (if OSD enabled).
                playlist = self._build_playlist()
                self._prepare_to_run_playlist(playlist)
            # Give the CPU some time to do other tasks.
            time.sleep(0.002)

    def signal_quit(self, signal, frame):
        """Shut down the program, meant to by called by signal handler."""
        self._running = False
        if self._player is not None:
            self._player.stop()
        pygame.quit()


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
