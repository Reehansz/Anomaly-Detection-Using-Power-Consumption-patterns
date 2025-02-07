import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
import joblib

# Load the dataset
data = pd.read_csv('./raw_power_readings.csv')

# Feature extraction: Calculate mean and mode for bus voltage, shunt voltage, and power
data['Bus Voltage Mean'] = data['Bus Voltage (V)'].rolling(window=5).mean()
data['Bus Voltage Mode'] = data['Bus Voltage (V)'].rolling(window=5).apply(lambda x: x.mode()[0] if not x.mode().empty else x.iloc[0])
data['Shunt Voltage Mean'] = data['Shunt Voltage (V)'].rolling(window=5).mean()
data['Shunt Voltage Mode'] = data['Shunt Voltage (V)'].rolling(window=5).apply(lambda x: x.mode()[0] if not x.mode().empty else x.iloc[0])
data['Power Mean'] = data['Power (W)'].rolling(window=5).mean()
data['Power Mode'] = data['Power (W)'].rolling(window=5).apply(lambda x: x.mode()[0] if not x.mode().empty else x.iloc[0])

# Feature extraction: Calculate rate of change for bus voltage, shunt voltage, and power
data['Bus Voltage Rate of Change'] = data['Bus Voltage (V)'].diff().rolling(window=5).mean()
data['Shunt Voltage Rate of Change'] = data['Shunt Voltage (V)'].diff().rolling(window=5).mean()
data['Power Rate of Change'] = data['Power (W)'].diff().rolling(window=5).mean()

# Drop rows with NaN values created by rolling window
data.dropna(inplace=True)

# Encode the 'Mode' and 'Device' columns to numerical values
label_encoder_mode = LabelEncoder()
data['Mode'] = label_encoder_mode.fit_transform(data['Mode'])

label_encoder_device = LabelEncoder()
data['Device'] = label_encoder_device.fit_transform(data['Device'])

# Define features and target variable
X = data.drop(columns=['Mode', 'Bus Voltage (V)', 'Shunt Voltage (V)', 'Current (A)', 'Power (W)', 'Timestamp'])
y = data['Mode']

# Standardize the features
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42)

# Initialize the RandomForestClassifier
model = RandomForestClassifier(n_estimators=100, random_state=42)

# Train the model
model.fit(X_train, y_train)

# Make predictions on the test set
y_pred = model.predict(X_test)

# Calculate and display the accuracy
accuracy = accuracy_score(y_test, y_pred)
print(f"Model Accuracy: {accuracy * 100:.2f}%")

# Print classification report for other metrics
print("\nClassification Report:")
print(classification_report(y_test, y_pred, target_names=label_encoder_mode.classes_))

# Save the trained model, label encoders, and scaler to disk using protocol=4 to avoid KeyError
joblib.dump(model, 'power_readings_model.pkl', protocol=4)
joblib.dump(label_encoder_mode, 'label_encoder_mode.pkl', protocol=4)
joblib.dump(label_encoder_device, 'label_encoder_device.pkl', protocol=4)
joblib.dump(scaler, 'scaler.pkl', protocol=4)

print("Model, label encoders, and scaler saved successfully.")