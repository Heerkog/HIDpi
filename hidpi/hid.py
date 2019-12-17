#Class that represents the Joystick state
class Joystick():

    def __init__(self):
        self.state = [
            0xA1,  #this is an input report
            0x04,  #Usage report = Joystick
            0x00,  #X-axis between -127 and 127
            0x00,  #Y-axis between -127 and 127
            0x00]  #unsigned char representing 3 buttons, rest empty

    def set_x_axis(self, x):
        self.state[2] = x;

    def set_y_axis(self, y):
        self.state[3] = y;

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

    def reset(self):
        self.state[2] = 0x00;
        self.state[3] = 0x00;
        self.state[4] = 0x00;

    def get_state(self):
        return self.state