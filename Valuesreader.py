import serial
import csv
import time
import os

# Configure the serial port for Windows (in your case COM6)
serial_port = 'COM6'  # Replace with the correct COM port for your ESP32
baud_rate = 9600

# Device type mapping (device name to label)
device_labels = {
    "Thermostat": "Thermostat",
    "CCTV": "CCTV",
    "Smoke Detector": "Smoke Detector",
}

# CSV file paths for each device
csv_files = {
    "Thermostat": './thermostat.csv',
    "CCTV": './cctv.csv',
    "Smoke Detector": './smoke_detector.csv'
}

# Buffer to collect data for each device
data_buffer = {device: [] for device in device_labels}

# Create a serial connection
ser = serial.Serial(serial_port, baud_rate)

# Function to write buffered data to CSV files
def write_to_csv():
    """Writes buffered data for each device to their respective CSV files."""
    for device_name, data_rows in data_buffer.items():
        if data_rows:
            file_path = csv_files[device_name]
            file_exists = os.path.isfile(file_path)
            
            with open(file_path, mode='a', newline='') as file:
                writer = csv.writer(file)
                # Write header only if the file is newly created
                if not file_exists:
                    writer.writerow(["Device", "Bus Voltage (V)", "Shunt Voltage (V)", "Current (A)", "Power (W)", "Timestamp"])
                # Write all rows for this device
                writer.writerows(data_rows)
            
            print(f"Appended {len(data_rows)} rows to {device_name}'s CSV file.")
            # Clear the buffer after writing
            data_buffer[device_name] = []

try:
    # Read and skip the ESP32 header ("Device, Bus Voltage (V), Shunt Voltage (V), Current (A), Power (W)")
    header = ser.readline().decode('utf-8').strip()
    print(f"Skipping ESP32 header: {header}")

    # Start reading data from the serial port continuously
    last_write_time = time.time()  # Track the last time data was written
    update_interval = 5  # Time interval in seconds for real-time updates

    while True:
        if ser.in_waiting > 0:
            # Read one line of data from the serial port
            line = ser.readline().decode('utf-8').strip()

            # Debugging: Print the raw data to see the incoming line
            print(f"Raw data: {line}")

            try:
                # Split the incoming data into individual components
                data = line.split(',')

                # Ensure the data contains exactly 5 values
                if len(data) != 5:
                    print(f"Invalid data length: {line}, skipping.")
                    continue

                # Extract data from the split line
                device_name, bus_voltage, shunt_voltage, current, power = data

                # Check if the device is in the known devices list
                if device_name not in device_labels:
                    print(f"Unknown device: {device_name}, skipping data.")
                    continue

                # Get the current timestamp
                timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

                # Add the row to the buffer for the device
                data_buffer[device_name].append([device_name, bus_voltage, shunt_voltage, current, power, timestamp])

            except ValueError:
                print(f"Invalid data format: {line}, skipping.")
                continue

        # Check if it's time to update the CSV files
        if time.time() - last_write_time >= update_interval:
            write_to_csv()
            last_write_time = time.time()  # Reset the timer

except KeyboardInterrupt:
    print("Data logging stopped.")
finally:
    # Write any remaining data in the buffer to CSV files
    write_to_csv()
    # Close the serial connection
    ser.close()
