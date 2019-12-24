from gpiozero import Button


#Class that represents the Joystick state
class Joystick:

    def __init__(self, profile):
        #Define the Joystick state
        self.state = [
            0xA1,  #this is an input report
            0x04,  #Usage report = Joystick
            0x00,  #X-axis between -127 and 127
            0x00,  #Y-axis between -127 and 127
            0x00]  #unsigned char representing 3 buttons, rest empty

        self.profile = profile

        #Set up GPIO input
        self.up_button = Button("GPIO17")     #Up signal
        self.down_button = Button("GPIO18")   #Down signal
        self.left_button = Button("GPIO22")   #Left signal
        self.right_button = Button("GPIO23")  #Right signal

        #Bind state update methods to events
        self.up_button.when_pressed = self.x_axis_event
        self.up_button.when_released = self.x_axis_event
        self.down_button.when_pressed = self.x_axis_event
        self.down_button.when_released = self.x_axis_event
        self.left_button.when_pressed = self.y_axis_event
        self.left_button.when_released = self.y_axis_event
        self.right_button.when_pressed = self.y_axis_event
        self.right_button.when_released = self.y_axis_event

    def x_axis_event(self):
        self.state[2] = hex((self.up_button.is_pressed - self.down_button.is_pressed) * 127)
        self.profile.send_input_report(self.state)

    def y_axis_event(self):
        self.state[3] = hex((self.right_button.is_pressed - self.left_button.is_pressed) * 127)
        self.profile.send_input_report(self.state)

    def set_button1_down(self):
        self.state[4] = self.state[4] + 0x80;

    def set_button1_up(self):
        self.state[4] = self.state[4] - 0x80;

    def set_button2_down(self):
        self.state[4] = self.state[4] + 0x40;

    def set_button2_up(self):
        self.state[4] = self.state[4] - 0x40;

    def set_button3_down(self):
        self.state[4] = self.state[4] + 0x20;

    def set_button3_up(self):
        self.state[4] = self.state[4] - 0x20;
