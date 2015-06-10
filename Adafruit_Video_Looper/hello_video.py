# Copyright 2015 Adafruit Industries.
# Author: Tony DiCola
# License: GNU GPLv2, see LICENSE.txt
import os
import subprocess
import time


class HelloVideoPlayer(object):

    def __init__(self, config):
        """Create an instance of a video player that runs hello_video.bin in the
        background.
        """
        self._process = None
        self._load_config(config)

    def _load_config(self, config):
        self._extensions = config.get('hello_video', 'extensions') \
                                 .translate(None, ' \t\r\n.') \
                                 .split(',')

    def supported_extensions(self):
        """Return list of supported file extensions."""
        return self._extensions

    def play(self, movie, loop=False, **kwargs):
        """Play the provided movied file, optionally looping it repeatedly."""
        self.stop(3)  # Up to 3 second delay to let the old player stop.
        # Assemble list of arguments.
        args = ['hello_video.bin']
        if loop:
            args.append('--loop')         # Add loop parameter if necessary.
        args.append(movie)                # Add movie file path.
        # Run hello_video process and direct standard output to /dev/null.
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
            # process.kill() doesn't seem to work reliably if USB drive is
            # removed, instead just run a kill -9 on it.
            subprocess.call(['kill', '-9', str(self._process.pid)])
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
    """Create new video player based on hello_video."""
    return HelloVideoPlayer(config)
