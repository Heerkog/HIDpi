# Manually start the Bluetooth service
sudo /usr/sbin/bluetoothd --compat &

# Wait for the service to start
sleep 5

# Start the Python script
sudo python -m hidpi
