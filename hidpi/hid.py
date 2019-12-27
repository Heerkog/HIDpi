from gpiozero import Button
import binascii
import struct

#Class that represents a general HID device state
class HumanInterfaceDevice(object):

    def __init__(self, report_function):
        self.report_function = report_function

        self.state = bytearray()
        self.state.append(struct.pack("B", 0xA1))  # this is an input report

    def get_state(self):
        return self.state

    def send_report(self):
        print("state: " + binascii.hexlify(self.state))
        self.report_function(self.state)
        return True


#Class that represents the Joystick state
class Joystick(HumanInterfaceDevice):

    def __init__(self, report_function):
        super(Joystick, self).__init__(report_function)

        #Define the Joystick state
        self.state.append(struct.pack("b", 0x00))  # X-axis between -127 and 127
        self.state.append(struct.pack("b", 0x00))  # Y-axis between -127 and 127
        self.state.append(struct.pack("B", 0x00))  # unsigned char representing 3 buttons, rest of bits are constants

        #Set up GPIO input
        self.up_button = Button("GPIO17")     #Up signal
        self.down_button = Button("GPIO18")   #Down signal
        self.left_button = Button("GPIO22")   #Left signal
        self.right_button = Button("GPIO23")  #Right signal

        self.button_1 = Button("GPIO24")  #Button 1
        self.button_2 = Button("GPIO25")  #Button 2
        self.button_3 = Button("GPIO27")  #Button 3

        #Bind state update methods to events
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
        self.state[2] = struct.pack("B", 128 * int(self.button_1.is_pressed) + 64 * int(self.button_2.is_pressed) + 32 * int(self.button_3.is_pressed))
        self.send_report()
