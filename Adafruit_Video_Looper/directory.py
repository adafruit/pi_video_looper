# Copyright 2015 Adafruit Industries.
# Author: Tony DiCola
# License: GNU GPLv2, see LICENSE.txt
import os

class DirectoryReader:

    def __init__(self, config):
        """Create an instance of a file reader that just reads a single
        directory on disk.
        """
        self._load_config(config)
        self._filecount = self.count_files()

    def _load_config(self, config):
        self._path = config.get('directory', 'path')

    def search_paths(self):
        """Return a list of paths to search for files."""
        return [self._path]

    def is_changed(self):
        """Return true if the number of files in the paths have changed."""
        current_count = self.count_files()
        if current_count != self._filecount:
            self._filecount = current_count
            return True
        else:
            return False

    def idle_message(self):
        """Return a message to display when idle and no files are found."""
        return 'No files found in {0}'.format(self._path)

    def count_files(self):
        return len(os.listdir(self._path))


def create_file_reader(config, screen):
    """Create new file reader based on reading a directory on disk."""
    return DirectoryReader(config)
