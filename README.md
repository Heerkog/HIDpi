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
These settings change the Bluetooth device name and class of the Raspberry Pi from a generic desktop device to a HID main device with a joystick subclass.
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
To execute the HID service, we must run the bluetooth service in the compatibility and debug mode.
To achieve this, we must edit the `dbus-org.bluez.service` file by executing the following command:

  * `sudo nano /etc/systemd/system/dbus-org.bluez.service`
  
Edit the `ExecStart=` line under the `[Service]` heading to specify:
```
ExecStart=/usr/lib/bluetooth/bluetoothd --nodetach --compat --debug -p time
```

Next, we must create a settings file with the Bluetooth adapter's physical address and a fixed pin.
We use a fixed pin because we don't want to have to log in to the Raspberry Pi every time we want to pair with another device.

To create a settings file copy the `sample_settings.xml` file using the following command:
  * `cp sample_settings.xml settings.xml`
  
Then edit the `settings.xml` file:
  * `Nano settings.xml`

Change the `address` value in the file to the physical address of your Raspberry Pi's Bluetooth adapter.
To find the physical address of your adapter, you may execute the `sudo bluetoothctl show` command.
Next, change the `pin` value to one of your own choosing.

Finally, reboot and run the `boot.sh` script.

# Running as a service
To automatically start the service during boot, add the `hid.service` file as a start up service. 
First, edit the `hid.service` file to include the correct path to where you cloned this repository.
Then execute the following commands:
  * `sudo cp hid.service /etc/systemd/system/`
  * `sudo systemctl enable hid.service`
  * `sudo systemctl daemon-reload`
  * `sudo systemctl start hid.service`
  
You may check whether the service is working with:
  * `sudo systemctl status hid.service`
  
# Device discovery
The device is discoverable for 30 seconds after the service started.
To make it discoverable again for 30 seconds, trigger any of the assigned GPIO signals.