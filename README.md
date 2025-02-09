# Anomaly Detection on IoT Devices Using Power Consumption Patterns

## Project Overview

This project focuses on detecting anomalies in IoT devices by analyzing their power consumption patterns. The system monitors various IoT devices such as Thermostats, CCTV cameras, and Smoke Detectors, and uses machine learning models to predict the operational mode of each device. If an anomaly is detected, the system sends a notification to alert the user.


## Files and Their Purpose

- **cctv.csv, smoke_detector.csv, thermostat.csv**: CSV files containing power consumption data for the respective devices.
- **CCTV.py, Smoke.py, Thermostat.py**: Scripts for processing data and predicting the mode of the respective devices.
- **graphs/**: Directory for storing graphs and visualizations.
- **implementation.doc**: Documentation of the project implementation.
- **IoT_Devices_Analysis.ipynb**: Jupyter notebook for analyzing IoT device data.
- **label_encoder_device.pkl, label_encoder_mode.pkl**: Pre-trained label encoders for device and mode labels.
- **power_readings_model.pkl**: Pre-trained machine learning model for predicting device modes.
- **random_both.py**: Script for training the machine learning model.
- **raw_power_readings.csv**: Raw power consumption data.
- **scaler.pkl**: Pre-trained scaler for standardizing features.
- **tempCodeRunnerFile.py**: Temporary file generated by the code runner.
- **UI.py**: Script for the user interface to monitor devices in real-time.
- **Valuesreader.py**: Script for reading data from the serial port and writing it to CSV files.

## How to Run the Project

1. **Set Up the Environment**:
   - Ensure you have Python installed.
   - Install the required libraries using the following command:
     ```sh
     pip install pandas joblib scikit-learn pyserial plyer
     ```

2. **Run the Data Reader**:
   - Connect your ESP32 or other IoT devices to the specified serial port.
   - Run the [`Valuesreader.py`](Valuesreader.py ) script to start reading data from the devices and writing it to CSV files:
     ```sh
     python Valuesreader.py
     ```

3. **Monitor Devices in Real-Time**:
   - Run the [`UI.py`](UI.py ) script to start the real-time monitoring interface:
     ```sh
     python UI.py
     ```

## Contributors

- **Rahul C Kalekar**
- **Sudeep**
- **Hassaan Imran Ahmed**

## License

This project is licensed under a Proprietary License. See the LICENSE file for details.

## Acknowledgments

We would like to thank our mentors, especially Revathi G P for mentoring through out the project and peers for their support and guidance throughout this project.

---

Feel free to reach out to any of the contributors for further information or collaboration opportunities.
