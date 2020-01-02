# Bluetooth GPIO Joystick for Raspberry Pi
A Python script that takes GPIO input to emulate a Bluetooth joystick device.

# How it works
The script emulates a Bluetooth human interface device (HID) in the form of a joystick device with 3 buttons.
It takes as input GPIO signals as button presses on the Raspberry Pi's **GPIO17**, **GPIO18**, **GPIO22**, **GPIO23**, **GPIO24**, **GPIO25**, and **GPIO27** pins.
These signals are then send to the HID host that is connected to the HID device using Bluetooth.

The different GPIO pins represent the following actions:
  * North/Up: **GPIO17**
  * South/Down: **GPIO18**
  * West/Left: **GPIO22**
  * East/Right: **GPIO23**
  * Button 1: **GPIO24**
  * Button 2: **GPIO25**
  * Button 3: **GPIO27**

Since we are using GPIO input, the joystick state is either centered without any GPIO signals or fully extended with GPIO signals.
That is, the device state is either centered, or in a fully extended north, northeast, east, southeast, south, southwest, west, or northwest position.
As a result, the device operates more alike a d-pad than an analogue joystick that supports degrees of movement.
To account for degrees of movement, one should extend the `hid.Joystick` class and use different input methods.

# Installation
  * Install git bash using the command `sudo apt-get install git-core -y`.
  * Create a directory for the service, and enter it.
  * Clone this repository with the command `git clone https://github.com/Heerkog/HIDpi.git`.
  * Execute `sudo setup.sh` to install all required packages.

# Bluetooth setup
To make the Raspberry Pi discoverable as a HID device, a number of settings must be changed manually.
These settings change the Bluetooth device name and class of the Raspberry Pi from a generic desktop device to a HID main device with a a joystick subclass.
If you want to keep using your Raspberry Pi as a generic desktop device, you may skip these steps.
 
The Raspberry pi Bluetooth stack settings can be initialized using the following commands: 

  * `cd /usr/local/etc`
  * `sudo ln -s /etc/bluetooth bluetooth` 

To change the settings, we edit two lines in the main.conf configuration file:

  * `nano ./bluetooth/main.conf`
  
Change the following two settings (and remove the # at the start of these two lines, if there):

```
Name = Bluetooth Joystick
Class = 0x000508
```

# Execution
To execute the service, run the `boot.sh` script.
Be aware that this restarts both the dbus and Bluetooth service and may take a while.

To automatically start the service during boot, add the `boot.sh` script as a cronjob using the following commands:
  * `sudo crontab -e`

Add the following line at the end of the file:

```
@reboot bash /path/to/HIDpi/boot.sh
``` 

# Device discovery
The device is discoverable for 30 seconds after the service started.
To make it discoverable again for 30 seconds, trigger any of the assigned GPIO signals.