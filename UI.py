import tkinter as tk
from tkinter import ttk
import pandas as pd
import joblib
import threading
import time
from plyer import notification

# Load the trained model, label encoders, and scaler
model = joblib.load('./power_readings_model.pkl')
label_encoder_mode = joblib.load('./label_encoder_mode.pkl')
label_encoder_device = joblib.load('./label_encoder_device.pkl')
scaler = joblib.load('./scaler.pkl')

# Dictionary to track the last known status of each device
device_status_tracker = {}

def predict_mode(new_data):
    new_data_scaled = scaler.transform(new_data)
    prediction = model.predict(new_data_scaled)
    predicted_mode = label_encoder_mode.inverse_transform(prediction)
    return predicted_mode[0]

def send_attack_notification(device_name):
    # Send desktop notification if an attack is detected
    notification.notify(
        title='IoT Device Under Attack!',
        message=f'Warning: {device_name} is under attack.',
        timeout=10
    )

def process_device(device_type, file_path):
    global device_status_tracker
    last_processed_row = 0

    while True:
        try:
            # Load the CSV file
            test_data = pd.read_csv(file_path)
            
            # Feature extraction
            test_data['Bus Voltage Mean'] = test_data['Bus Voltage (V)'].rolling(window=5).mean()
            test_data['Bus Voltage Mode'] = test_data['Bus Voltage (V)'].rolling(window=5).apply(lambda x: x.mode()[0] if not x.mode().empty else x.iloc[0])
            test_data['Shunt Voltage Mean'] = test_data['Shunt Voltage (V)'].rolling(window=5).mean()
            test_data['Shunt Voltage Mode'] = test_data['Shunt Voltage (V)'].rolling(window=5).apply(lambda x: x.mode()[0] if not x.mode().empty else x.iloc[0])
            test_data['Power Mean'] = test_data['Power (W)'].rolling(window=5).mean()
            test_data['Power Mode'] = test_data['Power (W)'].rolling(window=5).apply(lambda x: x.mode()[0] if not x.mode().empty else x.iloc[0])
            test_data['Bus Voltage Rate of Change'] = test_data['Bus Voltage (V)'].diff().rolling(window=5).mean()
            test_data['Shunt Voltage Rate of Change'] = test_data['Shunt Voltage (V)'].diff().rolling(window=5).mean()
            test_data['Power Rate of Change'] = test_data['Power (W)'].diff().rolling(window=5).mean()
            test_data.dropna(inplace=True)
            test_data['Device'] = label_encoder_device.transform(test_data['Device'])

            # Process new rows
            for index in range(last_processed_row, len(test_data)):
                new_data = test_data.iloc[index:index+1].drop(columns=['Bus Voltage (V)', 'Shunt Voltage (V)', 'Current (A)', 'Power (W)', 'Timestamp'])
                device = test_data.iloc[index]['Device']
                predicted_mode = predict_mode(new_data)
                device_name = label_encoder_device.inverse_transform([device])[0]

                # Get the last known status for the device
                last_status = device_status_tracker.get(device_name, "Normal")

                # Check status and update UI
                if predicted_mode == "Normal" or predicted_mode == "Connecting":
                    color = "green"
                else:
                    color = "red"
                    # Send a notification only if transitioning from Normal to attack
                    if last_status == "Normal":
                        send_attack_notification(device_name)
                
                # Update the last known status
                device_status_tracker[device_name] = predicted_mode
                
                # Add the log to the results in the UI
                results_text.insert('', tk.END, values=(device_type, device_name, predicted_mode), tags=('normal' if color == "green" else 'attack'))
            
            last_processed_row = len(test_data)
        except Exception as e:
            results_text.insert('', tk.END, values=(device_type, "Error", str(e)), tags=('error'))

        # Wait before checking for new rows
        time.sleep(5)

# Setting up the main window
root = tk.Tk()
root.title("IoT Anomaly Detection (Real-Time)")

# Style settings
style = ttk.Style(root)
root.configure(bg="#f5f5f5")
style.configure("TLabel", font=("Helvetica", 12), background="#f5f5f5")
style.configure("TButton", font=("Helvetica", 12))
style.configure("Treeview", font=("Helvetica", 10), rowheight=25)
style.configure("Treeview.Heading", font=("Helvetica", 12, "bold"))
style.map("Treeview", background=[("selected", "#d1e7dd")])

# Title Label
title_label = tk.Label(root, text="IoT Real-Time Anomaly Detection", font=("Helvetica", 16, "bold"), bg="#f5f5f5")
title_label.pack(pady=10)

# Process all devices in separate threads
def start_real_time_monitoring():
    device_files = {
        "Smoke Detector": './smoke_detector.csv',
        "Thermostat": './thermostat.csv',
        "CCTV": './cctv.csv'
    }

    for device_type, file_path in device_files.items():
        threading.Thread(target=process_device, args=(device_type, file_path), daemon=True).start()

# Start monitoring button
start_button = ttk.Button(root, text="Start Real-Time Monitoring", command=start_real_time_monitoring)
start_button.pack(pady=10)

# Results display area
columns = ("Device Type", "Device Name", "Predicted Mode")
results_text = ttk.Treeview(root, columns=columns, show='headings', height=15)
results_text.pack(padx=10, pady=10, fill="both", expand=True)

# Define table headings
for col in columns:
    results_text.heading(col, text=col)

# Scrollbar for the results table
scrollbar = ttk.Scrollbar(root, orient="vertical", command=results_text.yview)
results_text.configure(yscrollcommand=scrollbar.set)
scrollbar.pack(side="right", fill="y")

# Define tags for colored rows
results_text.tag_configure('normal', background="#d1f7d6", foreground="black")
results_text.tag_configure('attack', background="#f8d7da", foreground="black")
results_text.tag_configure('error', background="#fce5cd", foreground="black")

# Footer Label
footer_label = tk.Label(root, text="Developed by Your Team", font=("Helvetica", 10, "italic"), bg="#f5f5f5")
footer_label.pack(pady=5)

root.mainloop()