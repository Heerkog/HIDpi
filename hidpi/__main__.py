from hidpi.service import BTHIDService
import os
import sys

from gi.repository import GObject as gobject

from dbus.mainloop.glib import DBusGMainLoop


if __name__ == '__main__':
    if not os.geteuid() == 0:
        sys.exit("Only root can run this script")

    DBusGMainLoop(set_as_default=True)

    mainloop = gobject.MainLoop()
    myservice = BTHIDService(mainloop)
    mainloop.run()