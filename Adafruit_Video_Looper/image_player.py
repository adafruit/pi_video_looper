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
        self._bgcolor = list(map(int, config.get('video_looper', 'bgcolor')
                                        .translate(str.maketrans('','', ','))
                                        .split()))

    def supported_extensions(self):
        """Return list of supported file extensions."""
        return self._extensions

    def play(self, image, loop=None, **kwargs):
        """Display the provided image file."""
        if loop is None:
            self._loop = image.repeats
        else:
            self._loop = loop
        if self._loop == 0:
            self._loop = 1
        
        imagepath = image.filename

        if imagepath != "" and os.path.isfile(imagepath):
            self._screen.fill(self._bgcolor)
            pyimage = pygame.image.load(imagepath)

            center_image = True

            screen_w, screen_h = self._size
            image_w, image_h = pyimage.get_size()

            screen_aspect_ratio = screen_w / screen_h
            photo_aspect_ratio = image_w / image_h

            if screen_aspect_ratio < photo_aspect_ratio:  # Width is binding
                new_image_w = screen_w
                new_image_h = int(new_image_w / photo_aspect_ratio)
                pyimage = pygame.transform.scale(pyimage, (new_image_w, new_image_h))
                image_x = 0
                image_y = (screen_h - new_image_h) // 2 if center_image else 0

            elif screen_aspect_ratio > photo_aspect_ratio:  # Height is binding
                new_image_h = screen_h
                new_image_w = int(new_image_h * photo_aspect_ratio)
                pyimage = pygame.transform.scale(pyimage, (new_image_w, new_image_h))
                image_x = (screen_w - new_image_w) // 2 if center_image else 0
                image_y = 0

            else:  # Images have the same aspect ratio
                pyimage = pygame.transform.scale(pyimage, (screen_w, screen_h))
                image_x = 0
                image_y = 0

            self._screen.blit(pyimage, (image_x, image_y))
            pygame.display.flip()
            #future todo: crossfade option, ken burns
        
        self._startTime = perf_counter()

    def is_playing(self):
        """Here we need to compare for how long the image was displayed, also taking the in and set playing to false if time is up also"""
        if self._loop <= -1: #loop one image = play forever
            return True

        return (perf_counter() - self._startTime) < self._duration*self._loop

    def stop(self):
        """Stop the image display."""
        #todo: maybe use the bg image from config and or the bg color - see _blank_screen function in main file
        self._screen.fill(self._bgcolor)

    @staticmethod
    def can_loop_count():
        return True


def create_player(config, screen):
    """Create new image player."""
    return ImagePlayer(config, screen)
