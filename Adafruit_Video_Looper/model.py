# Copyright 2015 Adafruit Industries.
# Author: Tony DiCola
# License: GNU GPLv2, see LICENSE.txt
import random

class Movie:
    """Representation of a movie"""

    def __init__(self, filename: str, repeats: int = 1):
        """Create a playlist from the provided list of movies."""
        self.filename = filename
        self.repeats = int(repeats)
        self.playcount = 0

    def was_played(self):
        if self.repeats > 1:
            # only count up if its necessary, to prevent memory exhaustion if player runs a long time
            self.playcount += 1
        else:
            self.playcount = 1

    def clear_playcount(self):
        self.playcount = 0

    def __lt__(self, other):
        return self.filename < other.filename

    def __eq__(self, other):
        return self.filename == other.filename

    def __str__(self):
        return self.filename

    def __repr__(self):
        return repr((self.filename, self.repeats))

class Playlist:
    """Representation of a playlist of movies."""

    def __init__(self, movies, is_random):
        """Create a playlist from the provided list of movies."""
        self._movies = movies
        self._index = None
        self._is_random = is_random

    def get_next(self) -> Movie:
        """Get the next movie in the playlist. Will loop to start of playlist
        after reaching end.
        """
        # Check if no movies are in the playlist and return nothing.
        if len(self._movies) == 0:
            return None
        # Start Random movie
        if self._is_random:
            self._index = random.randrange(0, self.length())
        else:
            # Start at the first movie and increment through them in order.
            if self._index is None:
                self._index = 0
            else:
                self._index += 1
            # Wrap around to the start after finishing.
            if self._index >= self.length():
                self._index = 0

        return self._movies[self._index]

    def length(self):
        """Return the number of movies in the playlist."""
        return len(self._movies)
