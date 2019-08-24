# Copyright 2015 Adafruit Industries.
# Author: Tony DiCola
# License: GNU GPLv2, see LICENSE.txt
import glob
import subprocess
import time

import pyudev


class USBDriveMounter:
    """Service for automatically mounting attached USB drives."""

    def __init__(self, root='/mnt/usbdrive', readonly=True):
        """Create an instance of the USB drive mounter service.  Root is an
        optional parameter which specifies the location and file name prefix for
        mounted drives (a number will be appended to each mounted drive file
        name).  Readonly is a boolean that indicates if the drives should be
        mounted as read-only or not (default false, writable).
        """
        self._root = root
        self._readonly = readonly
        self._context = pyudev.Context()

    def remove_all(self):
        """Unmount and remove mount points for all mounted drives."""
        for path in glob.glob(self._root + '*'):
            subprocess.call(['umount', '-l', path])
            subprocess.call(['rm', '-r', path])

    def mount_all(self):
        """Mount all attached USB drives.  Readonly is a boolean that specifies
        if the drives should be mounted read only (defaults to true).
        """
        self.remove_all()
        # Enumerate USB drive partitions by path like /dev/sda1, etc.
        nodes = [x.device_node for x in self._context.list_devices(subsystem='block', DEVTYPE='partition')
                 if 'ID_BUS' in x and x['ID_BUS'] == 'usb']
        # Mount each drive under the mount root.
        for i, node in enumerate(nodes):
            path = self._root + str(i)
            subprocess.call(['mkdir', path])
            args = ['mount']
            if self._readonly:
                args.append('-r')
            args.extend([node, path])
            subprocess.check_call(args)

        return nodes

    def has_nodes(self):
        nodes = [x.device_node for x in self._context.list_devices(subsystem='block', DEVTYPE='partition')
                 if 'ID_BUS' in x and x['ID_BUS'] == 'usb']
        return nodes != []

    def start_monitor(self):
        """Initialize monitoring of USB drive changes."""
        self._monitor = pyudev.Monitor.from_netlink(self._context)
        self._monitor.filter_by('block', 'partition')
        self._monitor.start()

    def poll_changes(self):
        """Check for changes to USB drives.  Returns true if there was a USB 
        drive change, otherwise false.
        """
        # Look for a drive change.
        device = self._monitor.poll(0)
        # If a USB drive changed (added/remove) remount all drives.
        if device is not None and device['ID_BUS'] == 'usb':
            return True
        # Else nothing changed.
        return False


if __name__ == '__main__':
    # Run as a service that mounts all USB drives as read-only under the default
    # path of /mnt/usbdrive*.
    drive_mounter = USBDriveMounter(readonly=True)
    drive_mounter.mount_all()
    drive_mounter.start_monitor()
    print ('Listening for USB drive changes (press Ctrl-C to quit)...')
    while True:
        if drive_mounter.poll_changes():
            print ('USB drives changed!')
            drive_mounter.mount_all()
        time.sleep(0)
