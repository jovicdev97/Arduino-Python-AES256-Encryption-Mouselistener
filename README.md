# Arduino-Python Encryption Mouse Listener

## Overview

This project demonstrates a system where an Arduino and a Python script work together to encrypt and decrypt mouse click coordinates. The Arduino handles the encryption, while the Python script listens for mouse clicks, sends the coordinates to the Arduino, and then decrypts the encrypted coordinates received back from the Arduino. The Python script also generates performance reports and visualizations based on the encryption and decryption times.

## Setup Instructions

### Arduino Setup

1. Connect your Arduino to your computer.
2. Open the `arduino8266nodemcu10.cpp` file in the Arduino IDE.
3. Upload the code to your Arduino.

### Python Script Setup

1. Ensure you have Python installed on your computer.
2. Install the required Python libraries:
   ```sh
   pip install pyserial pynput pycryptodome matplotlib seaborn pandas
   ```
3. Connect your Arduino to your computer via COM 3.
4. Ensure the baud rate is set to 9600.

## Running the Python Script

1. Open a terminal or command prompt.
2. Navigate to the directory containing the `main.py` script.
3. Run the script:
   ```sh
   python main.py
   ```
4. The script will start listening for mouse clicks. When a click is detected, it will send the coordinates to the Arduino for encryption and then decrypt the encrypted coordinates received back from the Arduino.

## Performance Metrics and Visualizations

The Python script generates performance reports and visualizations based on the encryption and decryption times. These reports include statistics such as average, minimum, and maximum times for transmission, encryption, and decryption. The script also generates visualizations of the distribution of total operation times, which are saved as PNG files.
