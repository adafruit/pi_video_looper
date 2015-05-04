# Copyright 2015 Adafruit Industries.
# Author: Tony DiCola
# License: GNU GPLv2, see LICENSE.txt
import random

class Playlist(object):
    """Representation of a playlist of movies."""

    def __init__(self, movies, is_random):
        """Create a playlist from the provided list of movies."""
        self._movies = movies
        self._index = None
        self._is_random = is_random

    def get_next(self):
        """Get the next movie in the playlist. Will loop to start of playlist
        after reaching end.
        """
        # Check if no movies are in the playlist and return nothing.
        if len(self._movies) == 0:
            return None
        # Start Random movie
        if self._is_random:
            self._index = random.randrange(0, len(self._movies))
        else:
            # Start at the first movie and increment through them in order.
            if self._index is None:
                self._index = 0
            else:
                self._index += 1
            # Wrap around to the start after finishing.
            if self._index >= len(self._movies):
                self._index = 0

        return self._movies[self._index]

    def length(self):
        """Return the number of movies in the playlist."""
        return len(self._movies)
