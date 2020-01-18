from gpiozero import Button
# import binascii
import sys
import struct

# Class that represents a general HID device state
class HumanInterfaceDevice(object):
    MY_DEV_NAME = "Generic HID"
    SDP_RECORD_PATH = sys.path[0] + "sdp/"  #file path of the sdp record to laod
    UUID = "00001124-0000-1000-8000-00805f9b34fb"  #HumanInterfaceDeviceServiceClass UUID

    def __init__(self, report_function):
        self.report_function = report_function

        self.state = bytearray()
        self.state.append(struct.pack("B", 0xA1))  # this is an input report

    def get_state(self):
        return self.state

    def send_report(self):
        self.report_function(self.state)
        # print("state: " + binascii.hexlify(self.state))

    def get_name(self):
        return self.MY_DEV_NAME

    def get_sdp_record_path(self):
        return self.SDP_RECORD_PATH

    def get_uuid(self):
        return self.UUID


# Class that represents the Joystick state
class Joystick(HumanInterfaceDevice):

    def __init__(self, report_function):
        super(Joystick, self).__init__(report_function)

        self.MY_DEV_NAME = "Bluetooth Joystick"
        self.SDP_RECORD_PATH = sys.path[0] + "sdp/sdp_record_joystick.xml"

        # Define the Joystick state
        self.state.append(struct.pack("b", 0x00))  # X-axis between -127 and 127
        self.state.append(struct.pack("b", 0x00))  # Y-axis between -127 and 127
        self.state.append(struct.pack("B", 0x00))  # unsigned char representing 3 buttons, rest of bits are constants

        # Set up GPIO input
        self.up_button = Button("GPIO18")     #Up signal
        self.down_button = Button("GPIO17")   #Down signal
        self.left_button = Button("GPIO23")   #Left signal
        self.right_button = Button("GPIO22")  #Right signal

        self.button_1 = Button("GPIO24")  #Button 1
        self.button_2 = Button("GPIO25")  #Button 2
        self.button_3 = Button("GPIO27")  #Button 3

        # Bind state update methods to events
        self.left_button.when_pressed = self.x_axis_event
        self.left_button.when_released = self.x_axis_event
        self.right_button.when_pressed = self.x_axis_event
        self.right_button.when_released = self.x_axis_event
        self.up_button.when_pressed = self.y_axis_event
        self.up_button.when_released = self.y_axis_event
        self.down_button.when_pressed = self.y_axis_event
        self.down_button.when_released = self.y_axis_event

        self.button_1.when_pressed = self.button_event
        self.button_1.when_released = self.button_event
        self.button_2.when_pressed = self.button_event
        self.button_2.when_released = self.button_event
        self.button_3.when_pressed = self.button_event
        self.button_3.when_released = self.button_event


    def x_axis_event(self):
        self.state[1] = struct.pack("b", (int(self.right_button.is_pressed) - int(self.left_button.is_pressed)) * 127)
        self.send_report()

    def y_axis_event(self):
        self.state[2] = struct.pack("b", (int(self.down_button.is_pressed) - int(self.up_button.is_pressed)) * 127)
        self.send_report()

    def button_event(self):
        # self.state[3] = struct.pack("B", 128 * int(self.button_1.is_pressed) + 64 * int(self.button_2.is_pressed) + 32 * int(self.button_3.is_pressed))
        self.state[3] = struct.pack("B", 0xAA)
        self.send_report()
