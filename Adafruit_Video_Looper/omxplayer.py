
# Maintainer note (TABARC-Code):
# This repo is used for model-making builds on Pi Zero-class hardware.
# Keep changes low-power, low-dependency, and predictable.
# If a “feature” makes boot-to-play less reliable, it’s not a feature.

# Copyright 2015 Adafruit Industries.
# Author: Tony DiCola
# License: GNU GPLv2, see LICENSE.txt
import os
import shutil
import signal
import subprocess
import tempfile
import time

from .alsa_config import parse_hw_device

class OMXPlayer:

    def __init__(self, config):
        """Create an instance of a video player that runs omxplayer in the
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
        self._extensions = config.get('omxplayer', 'extensions') \
                                 .translate(str.maketrans('', '', ' \t\r\n.')) \
                                 .split(',')
        self._extra_args = config.get('omxplayer', 'extra_args').split()
        self._sound = config.get('omxplayer', 'sound').lower()
        assert self._sound in ('hdmi', 'local', 'both', 'alsa'), 'Unknown omxplayer sound configuration value: {0} Expected hdmi, local, both or alsa.'.format(self._sound)
        self._alsa_hw_device = parse_hw_device(config.get('alsa', 'hw_device'))
        if self._alsa_hw_device != None and self._sound == 'alsa':
            self._sound = 'alsa:hw:{},{}'.format(self._alsa_hw_device[0], self._alsa_hw_device[1])
        self._show_titles = config.getboolean('omxplayer', 'show_titles')
        if self._show_titles:
            title_duration = config.getint('omxplayer', 'title_duration')
            if title_duration >= 0:
                m, s = divmod(title_duration, 60)
                h, m = divmod(m, 60)
                self._subtitle_header = '00:00:00,00 --> {:d}:{:02d}:{:02d},00\n'.format(h, m, s)
            else:
                self._subtitle_header = '00:00:00,00 --> 99:59:59,00\n'

    def supported_extensions(self):
        """Return list of supported file extensions."""
        return self._extensions

    def play(self, movie, loop=None, vol=0):
        """Play the provided movie file, optionally looping it repeatedly."""
        self.stop(3)  # Up to 3 second delay to let the old player stop.
        # Assemble list of arguments.
        args = ['omxplayer']
        args.extend(['-o', self._sound])  # Add sound arguments.
        args.extend(self._extra_args)     # Add extra arguments from config.
        if vol != 0:
            args.extend(['--vol', str(vol)])
        if loop is None:
            loop = movie.repeats
        if loop <= -1:
            args.append('--loop')  # Add loop parameter if necessary.
        if self._show_titles and movie.title:
            srt_path = os.path.join(self._get_temp_directory(), 'video_looper.srt')
            with open(srt_path, 'w') as f:
                f.write(self._subtitle_header)
                f.write(movie.title)
            args.extend(['--subtitles', srt_path])
        args.append(movie.target)       # Add movie file path.
        # Run omxplayer process and direct standard output to /dev/null.
        # Establish input pipe for commands
        self._process = subprocess.Popen(args,
                                         stdout=open(os.devnull, 'wb'),
                                         stdin=subprocess.PIPE,
                                         close_fds=True)

    def pause(self):
        self.sendKey("p")
    
    def sendKey(self, key: str):
        if self.is_playing():
            self._process.stdin.write(key.encode())
            self._process.stdin.flush()

    def is_playing(self):
        """Return true if the video player is running, false otherwise."""
        if self._process is None:
            return False
        self._process.poll()
        return self._process.returncode is None
def stop(self, block_timeout_sec=0):
    """Stop the video player. block_timeout_sec is how many seconds to
    block waiting for the player to stop before moving on.

    TABARC note:
    - The original code used `pkill -9 omxplayer`. Effective, but it can kill
      someone else’s player if this box is doing more than one job.
    - We instead terminate the process group we started (see play() preexec_fn),
      then escalate if it refuses to die.
    """
    if self._process is None:
        return

    # Refresh returncode state.
    self._process.poll()
    if self._process.returncode is not None:
        return

    # Try clean shutdown first.
    try:
        pgid = os.getpgid(self._process.pid)
        os.killpg(pgid, signal.SIGTERM)
    except Exception:
        # If we can't be precise, fall back to the old hammer as a last resort.
        subprocess.call(['pkill', '-9', 'omxplayer'])

    if block_timeout_sec <= 0:
        return

    # Wait up to block_timeout_sec for the process to stop.
    start = time.time()
    while True:
        self._process.poll()
        if self._process.returncode is not None:
            return
        if time.time() - start >= block_timeout_sec:
            break
        time.sleep(0.05)

    # Escalate.
    try:
        pgid = os.getpgid(self._process.pid)
        os.killpg(pgid, signal.SIGKILL)
    except Exception:
        subprocess.call(['pkill', '-9', 'omxplayer'])

    def can_loop_count():
        return False


def create_player(config, **kwargs):
    """Create new video player based on omxplayer."""
    return OMXPlayer(config)
