# Author: Tobias Perschon
# License: GNU GPLv2, see LICENSE.txt
import os, pygame
from time import perf_counter

class ImagePlayer:

    def __init__(self, config, screen):
        """Create an instance of an image player uses pygame to display static images.
        """
        self._load_config(config)
        self._screen = screen
        self._loop = 0
        self._startTime = 0

    def _load_config(self, config):
        self._extensions = config.get('image_player', 'extensions') \
                                 .translate(str.maketrans('', '', ' \t\r\n.')) \
                                 .split(',')
        self._duration = config.getint('image_player', 'duration')
        self._size = (pygame.display.Info().current_w, pygame.display.Info().current_h)

    def supported_extensions(self):
        """Return list of supported file extensions."""
        return self._extensions

    def play(self, image, loop=None):
        """Display the provided image file."""
        if loop is None:
            self._loop = image.repeats
        else:
            self._loop = loop
        if self._loop == 0:
            self._loop = 1
        
        imagepath = image.filename
        if imagepath != "" and os.path.isfile(imagepath):
            pyimage = pygame.image.load(imagepath)
            pyimage = pygame.transform.scale(pyimage, self._size)
            rect = pyimage.get_rect()
            self._screen.blit(pyimage, rect)
            pygame.display.update()
            #future todo: crossfade option
        
        self._startTime = perf_counter()

    def is_playing(self):
        """Here we need to compare for how long the image was displayed, also taking the in and set playing to false if time is up also"""
        if self._loop <= -1: #loop one image = play forever
            return True
        
        return (perf_counter() - self._startTime) < self._duration*self._loop

    def stop(self):
        """Stop the image display."""
        #todo: maybe use the bg image from config and or the bg color - see _blank_screen function in main file
        self._screen.fill((0, 0, 0))

    @staticmethod
    def can_loop_count():
        return True


def create_player(config):
    """Create new image player."""
    return ImagePlayer(config)
