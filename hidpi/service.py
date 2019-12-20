import os
import sys
import dbus
import dbus.service
import dbus.mainloop.glib
from gi.repository import GLib
from hidpi.hid import Joystick
import socket

global mainloop

#define a bluez 5 profile object for our keyboard
class BluezProfile(dbus.service.Object):
    file_descriptor = -1

    def __init__(self, bus, path):
        print("Init")
        dbus.service.Object.__init__(self, bus, path)
        print(dbus.service.Object.Introspect(path))

    @dbus.service.method("org.bluez.Profile1", in_signature="", out_signature="")
    def Release(self):
        print("Release")
        mainloop.quit()

    @dbus.service.method("org.bluez.Profile1", in_signature="", out_signature="")
    def Cancel(self):
        print("Cancel")

    @dbus.service.method("org.bluez.Profile1", in_signature="oha{sv}", out_signature="")
    def NewConnection(self, path, file_descriptor, properties):
        self.file_descriptor = file_descriptor.take()
        #self.control_channel = socket.fromfd(file_descriptor, socket.AF_BLUETOOTH, socket.SOCK_STREAM)

        print("NewConnection(%s, %d)" % (path, self.file_descriptor))

        for key in properties.keys():
            if key == "Version" or key == "Features":
                print("  %s = 0x%04x" % (key, properties[key]))
            else:
                print("  %s = %s" % (key, properties[key]))

        GLib.io_add_watch(self.file_descriptor, GLib.PRIORITY_DEFAULT, GLib.IO_IN | GLib.IO_PRI, self.io_callback)

    @dbus.service.method("org.bluez.Profile1", in_signature="o", out_signature="")
    def RequestDisconnection(self, path):
        print("RequestDisconnection(%s)" % (path))

        if (self.file_descriptor > 0):
            os.close(self.file_descriptor)
            self.file_descriptor = -1

    def io_callback(self, file_descriptor, conditions):
        data = os.read(file_descriptor, 1024)
        print("{0}".format(data.decode('ascii')))
        return True

    def io_write(self, value):
        try:
            os.write(self.file_descriptor, value.encode('utf8'))
        except ConnectionResetError:
            self.file_descriptor = -1


#create a bluetooth device to emulate a HID joystick
class BTJoystick:
    MY_ADDRESS = "B8:27:EB:77:31:44"
    MY_DEV_NAME = "RPi_HID_Joystick"
    control_port = 17  #HID control port as specified in SDP > Protocol Descriptor List > L2CAP > HID Control Port
    interrupt_port = 19  #HID interrupt port as specified in SDP > Additional Protocol Descriptor List > L2CAP > HID Interrupt Port
    PROFILE_DBUS_PATH = "/bluez/heerkog/bthid_profile"  #dbus path of the bluez profile
    SDP_RECORD_PATH = sys.path[0] + "/sdp/sdp_record_joystick.xml"  #file path of the sdp record to laod
    UUID = "00001124-0000-1000-8000-00805f9b34fb"  #HumanInterfaceDeviceServiceClass UUID

    def __init__(self):
        mainloop = GLib.MainLoop()
        print("Configuring Bluez Profile")

        #setup profile options
        service_record = self.read_sdp_service_record()

        opts = {
            "ServiceRecord": service_record,
            "Role": "server",
            "AutoConnect": True,
            "RequireAuthentication": False,
            "RequireAuthorization": False
        }

        #retrieve a proxy for the bluez profile interface
        system_bus = dbus.SystemBus()

        adapter_properties = dbus.Interface(system_bus.get_object("org.bluez", "/org/bluez/hci0"), "org.freedesktop.DBus.Properties")
        adapter_properties.Set('org.bluez.Adapter1', 'Powered', dbus.Boolean(1))
        adapter_properties.Set('org.bluez.Adapter1', 'Pairable', dbus.Boolean(1))
        adapter_properties.Set('org.bluez.Adapter1', 'Discoverable', dbus.Boolean(1))

        profile_manager = dbus.Interface(system_bus.get_object("org.bluez", "/org/bluez"), "org.bluez.ProfileManager1")
        profile_manager.RegisterProfile(self.PROFILE_DBUS_PATH, self.UUID, opts)
        self.profile = BluezProfile(system_bus, self.PROFILE_DBUS_PATH)

        print("Profile registered")

        mainloop.run()

    #read and return an sdp record from a file
    def read_sdp_service_record(self):
        print("Reading service record: " + self.SDP_RECORD_PATH)

        try:
            fh = open(self.SDP_RECORD_PATH, "r")
        except:
            sys.exit("Failed to read SDP record.")

        return fh.read()

    #send a string to the bluetooth host machine
    def send_input_report(self, report):
        message = chr(report[0]) + chr(report[1]) + chr(report[2]) + chr(report[3]) + chr(report[4])

        print("Sending "+ message)
        self.profile.io_write(message)


#define a dbus HID service
class BTHIDService(dbus.service.Object):

    def __init__(self):
        print("Setting up service")
        #create joystick class
        self.joystick = Joystick(self)

        #create and setup our device
        self.device = BTJoystick()

    def send_input_report(self, report):
        self.device.send_input_report(report)
