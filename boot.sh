# Manually stop and start the Bluetooth service
sudo service bluetooth stop &>/dev/null &
sleep 2
sudo /etc/init.d/bluetooth stop &>/dev/null &
sleep 1
sudo /usr/sbin/bluetoothd --compat &>/dev/null &

# Wait for the service to start
sleep 2

# Start the Python script
sudo python -m hidpi
