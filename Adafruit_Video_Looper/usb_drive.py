# Copyright 2015 Adafruit Industries.
# Author: Tony DiCola
# License: GNU GPLv2, see LICENSE.txt
import glob

from usb_drive_mounter import USBDriveMounter


class USBDriveReader(object):

    def __init__(self, config):
        """Create an instance of a file reader that uses the USB drive mounter
        service to keep track of attached USB drives and automatically mount
        them for reading videos.
        """
        self._load_config(config)
        self._mounter = USBDriveMounter(root=self._mount_path,
                                        readonly=self._readonly)
        self._mounter.start_monitor()


    def _load_config(self, config):
        self._mount_path = config.get('usb_drive', 'mount_path')
        self._readonly = config.getboolean('usb_drive', 'readonly')

    def search_paths(self):
        """Return a list of paths to search for files. Will return a list of all
        mounted USB drives.
        """
        self._mounter.mount_all()
        return glob.glob(self._mount_path + '*')

    def is_changed(self):
        """Return true if the file search paths have changed, like when a new
        USB drive is inserted.
        """
        return self._mounter.poll_changes()

    def idle_message(self):
        """Return a message to display when idle and no files are found."""
        return 'Insert USB drive with compatible movies.'


def create_file_reader(config):
    """Create new file reader based on mounting USB drives."""
    return USBDriveReader(config)
