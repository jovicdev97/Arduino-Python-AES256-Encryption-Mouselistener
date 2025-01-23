import serial
import time
from pynput import mouse, keyboard
from Cryptodome.Cipher import AES
import statistics
import psutil
import platform
from datetime import datetime

def print_timestamp():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

# AES256-Schlüssel (muss mit dem Arduino-Sketch übereinstimmen)
aes_key = bytes([
    0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07,
    0x08, 0x09, 0x0A, 0x0B, 0x0C, 0x0D, 0x0E, 0x0F,
    0x10, 0x11, 0x12, 0x13, 0x14, 0x15, 0x16, 0x17,
    0x18, 0x19, 0x1A, 0x1B, 0x1C, 0x1D, 0x1E, 0x1F
])

print("**Script start**")
print("**Connecting to Arduino via COM 3**")
arduino = serial.Serial('COM3', 9600, timeout=1)
time.sleep(2)
print("**Success**")
print("**Mouse Listener waiting**\n\n")

# Add running flag
running = True

# Add timing statistics storage
encryption_times = []
decryption_times = []
total_times = []

def log_system_info():
    print("\n=== System Information ===")
    print(f"CPU: {platform.processor()}")
    print(f"Python Version: {platform.python_version()}")
    print(f"OS: {platform.system()} {platform.release()}")
    print(f"CPU Usage: {psutil.cpu_percent()}%")
    print(f"Memory Usage: {psutil.Process().memory_info().rss / 1024 / 1024:.2f} MB")
    print("========================\n")

def format_coordinates(x, y):
    """Formatiert Mauskoordinaten als 16-Byte-String."""
    coord_str = f"x{int(x):04d}y{int(y):04d}      "  # Enough spaces for 16 total bytes - we need to send exactly 16
    return coord_str

def decrypt_data(encrypted_hex, click_start_time):
    dec_start = time.perf_counter_ns()
    encrypted_data = bytes.fromhex(encrypted_hex)
    cipher = AES.new(aes_key, AES.MODE_ECB)
    decrypted_data = cipher.decrypt(encrypted_data)
    result = decrypted_data.decode("utf-8", errors="ignore")
    dec_end = time.perf_counter_ns()
    dec_time = (dec_end - dec_start) / 1000  # to microseconds
    
    ts = print_timestamp()
    print(f"{ts} = = PYTHON: Decrypting starts.")
    print(f"{ts} = = PYTHON: Decrypting to {result} succesful (This took: {dec_time:.2f} Microseconds)")
    
    total_time = (dec_end - click_start_time) / 1000
    print(f"\n** Statistics about Mouseclick **")
    print(f"TOTAL TIME FOR DECRYPT: {dec_time:.2f}us")
    print(f"TOTAL TIME FROM PLAIN COORDINATES TO RECEIVING THE DECRYPTED DATA IN PYTHON: {total_time:.2f}us")
    print(f"\nThe whole process took: {total_time:.2f}us")
    print(f"\nThis means: whenever you click with your (hardware mouse), it takes {total_time/1000:.2f} MILLISECONDS to get that data captured by the listener, send it to arduino, encrypt it, send it back, decrypt it.\n")
    
    return result

def on_click(x, y, button, pressed):
    if not pressed or not running:
        return False
    
    click_start_time = time.perf_counter_ns()
    coord_str = format_coordinates(x, y)
    ts = print_timestamp()
    
    print(f"{ts} = = PYTHON: CLICK detected at Coordinates {x} {y} ==")
    
    send_start = time.perf_counter_ns()
    arduino.write(coord_str.encode())
    send_end = time.perf_counter_ns()
    send_time = (send_end - send_start) / 1000
    
    print(f"{ts} = = PYTHON: Sending Coordinates to Arduino (This took: {send_time:.2f} Microseconds) ==")
    
    while arduino.in_waiting and running:
        response = arduino.readline().decode("latin-1", errors="ignore").strip()
        if response.startswith("ENC_DATA:"):
            encrypted_hex = response.split(":")[1].strip()
            ts = print_timestamp()
            print(f"{ts} = = PYTHON: Received encrypted data: {encrypted_hex} ==")
            decrypted = decrypt_data(encrypted_hex, click_start_time)

def on_press(key):
    global running
    if key == keyboard.Key.esc:
        print("Escape pressed, exiting...")
        running = False
        arduino.close()
        return False

# Listener start
print("Mausklick-Erfassung gestartet. Drücken Sie Strg+C zum Beenden.")
with mouse.Listener(on_click=on_click) as m_listener, \
     keyboard.Listener(on_press=on_press) as k_listener:
    while running:
        time.sleep(0.1)  # my cpu goes crazy if i dont do this
    
m_listener.stop()
k_listener.stop()