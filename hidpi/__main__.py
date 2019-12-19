from hidpi.service import BTHIDService
import os
import sys
import dbus.mainloop.glib
from gi.repository import Gtk


if __name__ == '__main__':
    if not os.geteuid() == 0:
        sys.exit("Only root can run this script")

    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
    myservice = BTHIDService()

    Gtk.main()