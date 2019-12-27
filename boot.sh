# Manually stop and start the Bluetooth service
sudo service bluetooth stop
sleep 5
sudo /etc/init.d/bluetooth stop
sleep 1
sudo /usr/sbin/bluetoothd --compat &

# Wait for the service to start
sleep 4

# Start the Python script
sudo python -m hidpi
