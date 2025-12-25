# Author: Tobias Perschon
# License: GNU GPLv2, see LICENSE.txt
import os, pygame
from time import monotonic

class ImagePlayer:

    def __init__(self, config, screen, bgimage):
        """Create an instance of an image player uses pygame to display static images.
        """
        self._load_config(config)
        self._screen = screen
        self._loop = 0
        self._startTime = 0
        self._bgimage = bgimage
        self._isPaused = False

    def _load_config(self, config):
        self._extensions = config.get('image_player', 'extensions') \
                                 .translate(str.maketrans('', '', ' \t\r\n.')) \
                                 .split(',')
        self._duration = config.getint('image_player', 'duration')
        self._size = (pygame.display.Info().current_w, pygame.display.Info().current_h)
        self._bgcolor = list(map(int, config.get('video_looper', 'bgcolor')
                                        .translate(str.maketrans('','', ','))
                                        .split()))
        self._scale = config.getboolean('image_player', 'scale') 
        self._center = config.getboolean('image_player', 'center') 
        self._wait_time = config.getint('video_looper', 'wait_time')

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
        
        imagepath = image.target

        if imagepath != "" and os.path.isfile(imagepath):
            self._blank_screen(False)
            pyimage = pygame.image.load(imagepath)
            image_x = 0
            image_y = 0
            screen_w, screen_h = self._size
            image_w, image_h = pyimage.get_size()
            new_image_w, new_image_h = pyimage.get_size()
            screen_aspect_ratio = screen_w / screen_h
            photo_aspect_ratio = image_w / image_h

            if self._scale:
                if screen_aspect_ratio < photo_aspect_ratio:  # Width is binding
                    new_image_w = screen_w
                    new_image_h = int(new_image_w / photo_aspect_ratio)
                    pyimage = pygame.transform.scale(pyimage, (new_image_w, new_image_h))
                elif screen_aspect_ratio > photo_aspect_ratio:  # Height is binding
                    new_image_h = screen_h
                    new_image_w = int(new_image_h * photo_aspect_ratio)
                    pyimage = pygame.transform.scale(pyimage, (new_image_w, new_image_h))
                else:  # Images have the same aspect ratio
                    pyimage = pygame.transform.scale(pyimage, (screen_w, screen_h))

            if self._center:
                if screen_aspect_ratio < photo_aspect_ratio:
                    image_y = (screen_h - new_image_h) // 2
                elif screen_aspect_ratio > photo_aspect_ratio:
                    image_x = (screen_w - new_image_w) // 2

            self._screen.blit(pyimage, (image_x, image_y))
            pygame.display.flip()
            #future todo: crossfade, ken burns possbile?
            #future todo: maybe preload images and/or create pygame image dict

        self._startTime = monotonic()

    def pause(self):
        self._isPaused = not self._isPaused
    
    def sendKey(self, key: str):
        print("sendKey not available for image_player")

    def is_playing(self):
        """Here we need to compare for how long the image was displayed"""
        if self._loop <= -1 or self._isPaused: #loop one image = play forever
            return True
        
        playing = (monotonic() - self._startTime) < self._duration*self._loop
        
        if not playing and self._wait_time > 0: #only refresh background if we wait between images
            self._blank_screen()
        
        return playing

    def stop(self, block_timeout_sec=0):
        """Stop the image display."""
        self._blank_screen()
        self._startTime = self._startTime-self._duration*self._loop

    def _blank_screen(self, flip=True):
        """Render a blank screen filled with the background color and optional the background image."""
        self._screen.fill(self._bgcolor)
        if self._bgimage[0] is not None:
            self._screen.blit(self._bgimage[0], (self._bgimage[1], self._bgimage[2]))
        if(flip):
            pygame.display.flip()

    @staticmethod
    def can_loop_count():
        return True


def create_player(config, **kwargs):
    """Create new image player."""
    return ImagePlayer(config, screen=kwargs['screen'], bgimage=kwargs['bgimage'])
