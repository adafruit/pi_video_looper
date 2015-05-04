# Copyright 2015 Adafruit Industries.
# Author: Tony DiCola
# License: GNU GPLv2, see LICENSE.txt
import os
import subprocess
import time


class OMXPlayer(object):

    def __init__(self, config):
        """Create an instance of a video player that runs omxplayer in the
        background.
        """
        self._process = None
        self._load_config(config)

    def _load_config(self, config):
        self._extensions = config.get('omxplayer', 'extensions') \
                                 .translate(None, ' \t\r\n.') \
                                 .split(',')
        self._extra_args = config.get('omxplayer', 'extra_args').split()
        self._sound = config.get('omxplayer', 'sound').lower()
        assert self._sound in ('hdmi', 'local', 'both'), 'Unknown omxplayer sound configuration value: {0} Expected hdmi, local, or both.'.format(self._sound)

    def supported_extensions(self):
        """Return list of supported file extensions."""
        return self._extensions

    def play(self, movie, loop=False, vol=0):
        """Play the provided movied file, optionally looping it repeatedly."""
        self.stop(3)  # Up to 3 second delay to let the old player stop.
        # Assemble list of arguments.
        args = ['omxplayer']
        args.extend(['-o', self._sound])  # Add sound arguments.
        args.extend(self._extra_args)     # Add extra arguments from config.
        if vol is not 0:
            args.extend(['--vol', str(vol)])
        if loop:
            args.append('--loop')         # Add loop parameter if necessary.
        args.append(movie)                # Add movie file path.
        # Run omxplayer process and direct standard output to /dev/null.
        self._process = subprocess.Popen(args,
                                         stdout=open(os.devnull, 'wb'),
                                         close_fds=True)

    def is_playing(self):
        """Return true if the video player is running, false otherwise."""
        if self._process is None:
            return False
        self._process.poll()
        return self._process.returncode is None

    def stop(self, block_timeout_sec=None):
        """Stop the video player.  block_timeout_sec is how many seconds to
        block waiting for the player to stop before moving on.
        """
        # Stop the player if it's running.
        if self._process is not None and self._process.returncode is None:
            # There are a couple processes used by omxplayer, so kill both
            # with a pkill command.
            subprocess.call(['pkill', '-9', 'omxplayer'])
        # If a blocking timeout was specified, wait up to that amount of time
        # for the process to stop.
        start = time.time()
        while self._process is not None and self._process.returncode is None:
            if (time.time() - start) >= block_timeout_sec:
                break
            time.sleep(0)
        # Let the process be garbage collected.
        self._process = None


def create_player(config):
    """Create new video player based on omxplayer."""
    return OMXPlayer(config)
