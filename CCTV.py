import pandas as pd
import joblib
import time

# Load the trained model, label encoders, and scaler
model = joblib.load('./power_readings_model.pkl')
label_encoder_mode = joblib.load('./label_encoder_mode.pkl')
label_encoder_device = joblib.load('./label_encoder_device.pkl')
scaler = joblib.load('./scaler.pkl')

def predict_mode(new_data):
    # Standardize the new data
    new_data_scaled = scaler.transform(new_data)
    # Predict the mode for new data
    prediction = model.predict(new_data_scaled)
    predicted_mode = label_encoder_mode.inverse_transform(prediction)
    return predicted_mode[0]

def main():
    # Path to the test CSV file
    test_csv_path = './cctv.csv'
    
    # Keep track of the last processed row
    last_processed_row = 0
    
    while True:
        # Load the test CSV file
        test_data = pd.read_csv(test_csv_path)
        
        # Feature extraction: Calculate mean and mode for bus voltage, shunt voltage, and power
        test_data['Bus Voltage Mean'] = test_data['Bus Voltage (V)'].rolling(window=5).mean()
        test_data['Bus Voltage Mode'] = test_data['Bus Voltage (V)'].rolling(window=5).apply(lambda x: x.mode()[0] if not x.mode().empty else x.iloc[0])
        test_data['Shunt Voltage Mean'] = test_data['Shunt Voltage (V)'].rolling(window=5).mean()
        test_data['Shunt Voltage Mode'] = test_data['Shunt Voltage (V)'].rolling(window=5).apply(lambda x: x.mode()[0] if not x.mode().empty else x.iloc[0])
        test_data['Power Mean'] = test_data['Power (W)'].rolling(window=5).mean()
        test_data['Power Mode'] = test_data['Power (W)'].rolling(window=5).apply(lambda x: x.mode()[0] if not x.mode().empty else x.iloc[0])
        
        # Feature extraction: Calculate rate of change for bus voltage, shunt voltage, and power
        test_data['Bus Voltage Rate of Change'] = test_data['Bus Voltage (V)'].diff().rolling(window=5).mean()
        test_data['Shunt Voltage Rate of Change'] = test_data['Shunt Voltage (V)'].diff().rolling(window=5).mean()
        test_data['Power Rate of Change'] = test_data['Power (W)'].diff().rolling(window=5).mean()
        
        # Drop rows with NaN values created by rolling window
        test_data.dropna(inplace=True)
        
        # Encode the 'Device' column
        test_data['Device'] = label_encoder_device.transform(test_data['Device'])
        
        # Check if there are new rows to process
        if len(test_data) > last_processed_row:
            # Process new rows
            for index in range(last_processed_row, len(test_data)):
                new_data = test_data.iloc[index:index+1].drop(columns=['Bus Voltage (V)', 'Shunt Voltage (V)', 'Current (A)', 'Power (W)', 'Timestamp'])
                device = test_data.iloc[index]['Device']
                predicted_mode = predict_mode(new_data)
                device_name = label_encoder_device.inverse_transform([device])[0]
                print(f"Predicted Mode: {predicted_mode} in {device_name}")
            
            # Update the last processed row
            last_processed_row = len(test_data)
        
        # Wait for a short period before checking again
        time.sleep(4)

if __name__ == "__main__":
    main()