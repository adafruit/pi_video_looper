# Copyright 2015 Adafruit Industries.
# Author: Tony DiCola
# License: GNU GPLv2, see LICENSE.txt
import os
import shutil
import subprocess
import tempfile
import time

from .alsa_config import parse_hw_device

class CVLCPlayer:

    def __init__(self, config):
        """Create an instance of a video player that runs cvlc in the
        background.
        """
        self._process = None
        self._temp_directory = None
        self._load_config(config)

    def __del__(self):
        if self._temp_directory:
            shutil.rmtree(self._temp_directory)

    def _get_temp_directory(self):
        if not self._temp_directory:
            self._temp_directory = tempfile.mkdtemp()
        return self._temp_directory

    def _load_config(self, config):
        self._extensions = config.get('cvlc', 'extensions') \
                                 .translate(str.maketrans('', '', ' \t\r\n.')) \
                                 .split(',')
        #self._extra_args = config.get('cvlc', 'extra_args').split()
        #self._sound = config.get('cvlc', 'sound').lower()
        #assert self._sound in ('hdmi', 'local', 'both', 'alsa'), 'Unknown cvlc sound configuration value: {0} Expected hdmi, local, both or alsa.'.format(self._sound)
        #self._alsa_hw_device = parse_hw_device(config.get('alsa', 'hw_device'))
        #if self._alsa_hw_device != None and self._sound == 'alsa':
        #    self._sound = 'alsa:hw:{},{}'.format(self._alsa_hw_device[0], self._alsa_hw_device[1])
        #self._show_titles = config.getboolean('cvlc', 'show_titles')
        #if self._show_titles:
        #    title_duration = config.getint('cvlc', 'title_duration')
        #    if title_duration >= 0:
        #        m, s = divmod(title_duration, 60)
        #        h, m = divmod(m, 60)
        #        self._subtitle_header = '00:00:00,00 --> {:d}:{:02d}:{:02d},00\n'.format(h, m, s)
        #    else:
        #        self._subtitle_header = '00:00:00,00 --> 99:59:59,00\n'

    def supported_extensions(self):
        """Return list of supported file extensions."""
        return self._extensions

    def play(self, movie, loop=None, vol=0):
        """Play the provided movie file, optionally looping it repeatedly."""
        self.stop(3)  # Up to 3 second delay to let the old player stop.
        # Assemble list of arguments.
        args = ['sudo', '-u','pi', 'cvlc']
        #args.extend(['-o', self._sound])  # Add sound arguments.
        #args.extend(self._extra_args)     # Add extra arguments from config.
        #if vol is not 0:
        #    args.extend(['--vol', str(vol)])
        if loop is None:
            loop = movie.repeats
        if loop <= -1:
            args.append('--loop')  # Add loop parameter if necessary.
        else:
            args.append('--play-and-exit')
        #if self._show_titles and movie.title:
        #    srt_path = os.path.join(self._get_temp_directory(), 'video_looper.srt')
        #    with open(srt_path, 'w') as f:
        #        f.write(self._subtitle_header)
        #        f.write(movie.title)
        #    args.extend(['--subtitles', srt_path])
        #else:
        #    args.append('--no-osd')
        args.append(movie.filename)       # Add movie file path.
        # Run cvlc process and direct standard output to /dev/null.
        self._process = subprocess.Popen(args,
                                         stdout=open(os.devnull, 'wb'),
                                         close_fds=True)

    def is_playing(self):
        """Return true if the video player is running, false otherwise."""
        if self._process is None:
            return False
        self._process.poll()
        return self._process.returncode is None

    def stop(self, block_timeout_sec=0):
        """Stop the video player.  block_timeout_sec is how many seconds to
        block waiting for the player to stop before moving on.
        """
        # Stop the player if it's running.
        if self._process is not None and self._process.returncode is None:
            # There are a couple processes used by cvlc, so kill both
            # with a pkill command.
            subprocess.call(['pkill', '-9', 'vlc'])
        # If a blocking timeout was specified, wait up to that amount of time
        # for the process to stop.
        start = time.time()
        while self._process is not None and self._process.returncode is None:
            if (time.time() - start) >= block_timeout_sec:
                break
            time.sleep(0)
        # Let the process be garbage collected.
        self._process = None

    @staticmethod
    def can_loop_count():
        return False


def create_player(config, **kwargs):
    """Create new video player based on cvlc."""
    return CVLCPlayer(config)
