import matplotlib
matplotlib.use('Agg') 

import serial
import time
from pynput import mouse, keyboard
from Cryptodome.Cipher import AES
import statistics
import psutil
import platform
from datetime import datetime
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

def print_timestamp():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

# AES256-Schlüssel (muss mit arduino8266nodemcu10 übereinstimmen)
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

# Running flag
running = True

# Timing
encryption_times = []
decryption_times = []
total_times = []

class Metrics:
    def __init__(self):
        self.transmission_times = []
        self.encryption_times = []
        self.decryption_times = []
        self.total_times = []
        self.clicks_processed = 0
        self.start_time = time.time()

metrics = Metrics()

def log_system_info():
    print("\n=== Memory Info ===")
    print(f"Usage: {psutil.Process().memory_info().rss / 1024 / 1024:.2f} MB")
    print("========================\n")

def format_coordinates(x, y):
    """Formatiert Mauskoordinaten als 16-Byte-String."""
    coord_str = f"x{int(x):04d}y{int(y):04d}      "  # we need to send exactly 16 bytes so we add leerzeichen
    return coord_str

def generate_report():
    """Generate comprehensive performance report with visualizations"""
    runtime = time.time() - metrics.start_time
    
    # Statistics PRINT
    print("\n====== AVG REPORT ======")
    print(f"Total Runtime: {runtime:.2f} seconds")
    print(f"Total Clicks Processed: {metrics.clicks_processed}")
    
    if metrics.transmission_times:
        print("\nTransmission Statistics (microseconds):")
        print(f"  Average: {statistics.mean(metrics.transmission_times):.2f}")
        print(f"  Min: {min(metrics.transmission_times):.2f}")
        print(f"  Max: {max(metrics.transmission_times):.2f}")
    
    if metrics.decryption_times:
        print("\nDecryption Statistics (microseconds):")
        print(f"  Average: {statistics.mean(metrics.decryption_times):.2f}")
        print(f"  Min: {min(metrics.decryption_times):.2f}")
        print(f"  Max: {max(metrics.decryption_times):.2f}")
    
    if metrics.total_times:
        print("\nTotal Operation Statistics (microseconds):")
        print(f"  Average: {statistics.mean(metrics.total_times):.2f}")
        print(f"  Min: {min(metrics.total_times):.2f}")
        print(f"  Max: {max(metrics.total_times):.2f}")
    
    log_system_info()
    print("==============================\n")

    try:
        if not metrics.total_times:
            print("No data available for visualization")
            return
            
        plt.style.use('bmh')
        
        with plt.style.context('bmh'):
            fig, ax = plt.subplots(figsize=(10, 6), dpi=100)
            fig.suptitle('Performance Analysis', fontsize=16)

            sns.histplot(data=metrics.total_times, bins=30, kde=True, ax=ax)
            ax.set_title('Distribution of Total Operation Times')
            ax.set_xlabel('Time (microseconds)')
            ax.set_ylabel('Frequency')
            
            mean_time = statistics.mean(metrics.total_times)
            median_time = statistics.median(metrics.total_times)
            ax.axvline(mean_time, color='r', linestyle='--', label=f'Mean: {mean_time:.2f}μs')
            ax.axvline(median_time, color='g', linestyle='--', label=f'Median: {median_time:.2f}μs')
            ax.legend()

            plt.tight_layout()
            
            # File save
            try:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                plot_filename = f'performance_metrics_{timestamp}.png'
                fig.savefig(plot_filename, bbox_inches='tight', dpi=100)
                print(f"\nPerformance visualization saved as: {plot_filename}")
            except Exception as e:
                print(f"\nError saving plot: {e}")
            finally:
                plt.close(fig)  
                plt.close('all') 
                
    except Exception as e:
        print(f"\nError generating visualization: {e}")
        plt.close('all') 

def decrypt_data(encrypted_hex, click_start_time):
    dec_start = time.perf_counter_ns()
    encrypted_data = bytes.fromhex(encrypted_hex)
    cipher = AES.new(aes_key, AES.MODE_ECB)
    decrypted_data = cipher.decrypt(encrypted_data)
    result = decrypted_data.decode("utf-8", errors="ignore")
    dec_end = time.perf_counter_ns()
    dec_time = (dec_end - dec_start) / 1000
    
    ts = print_timestamp()
    print(f"{ts} = = PYTHON: Decrypting starts.")
    print(f"{ts} = = PYTHON: Decrypting to {result} successful (This took: {dec_time:.2f} Microseconds)")
    
    total_time = (dec_end - click_start_time) / 1000
    print(f"\n** Statistics about Mouseclick **")
    print(f"Time to send coordinates: {send_time:.2f}us")
    print(f"TOTAL TIME FOR DECRYPT: {dec_time:.2f}us")
    print(f"TOTAL TIME FROM PLAIN COORDINATES TO RECEIVING THE DECRYPTED DATA IN PYTHON: {total_time:.2f}us")
    print(f"\nThe whole process took: {total_time:.2f}us")
    print(f"\nThis means: whenever you click with your (hardware mouse), it takes {total_time/1000:.2f} MILLISECONDS to get that data captured by the listener, send it to arduino, encrypt it, send it back, decrypt it.\n")
    
    metrics.decryption_times.append(dec_time)
    metrics.total_times.append(total_time)
    metrics.clicks_processed += 1
    
    return result

def on_click(x, y, button, pressed):
    global running, send_time
    if not pressed or not running:
        return
    
    click_start_time = time.perf_counter_ns()
    coord_str = format_coordinates(x, y)
    ts = print_timestamp()
    
    print(f"{ts} = = PYTHON: CLICK detected at Coordinates {x} {y} ==")
    
    # Reset Buffer after clcik
    arduino.reset_input_buffer()
    arduino.reset_output_buffer()
    
    send_start = time.perf_counter_ns()
    try:
        arduino.write(coord_str.encode())
        arduino.flush()
        send_end = time.perf_counter_ns()
        send_time = (send_end - send_start) / 1000
        
        print(f"{ts} = = PYTHON: Sending Coordinates to Arduino (This took: {send_time:.2f} Microseconds) ==")
        metrics.transmission_times.append(send_time)
        
        # Wait for response
        response_timeout = time.time() + 2
        while time.time() < response_timeout and running:
            if arduino.in_waiting > 0:
                try:
                    response = arduino.readline().decode("latin-1", errors="ignore").strip()
                    if response:
                        print(f"{ts} = = PYTHON: Received raw response: {response}")
                        
                        if response.startswith("ENC_DATA:"):
                            encrypted_hex = response.split(":")[1].strip()
                            print(f"{ts} = = PYTHON: Received encrypted data: {encrypted_hex} ==")
                            decrypted = decrypt_data(encrypted_hex, click_start_time)
                            return 
                except Exception as e:
                    print(f"{ts} = = PYTHON: Error reading response: {e}")
                    continue
                    
            time.sleep(0.01)
            
        if time.time() >= response_timeout:
            print(f"{ts} = = PYTHON: ERROR - No response received from Arduino within timeout period")
            
    except serial.SerialException as e:
        print(f"{ts} = = PYTHON: Serial communication error: {e}")
        running = False
        return

def on_press(key):
    global running
    if key == keyboard.Key.esc:
        print("Escape pressed, generating final report...")
        generate_report()
        running = False
        arduino.close()
        plt.close('all') 
        return False

# Listener start
print("Mausklick-Erfassung gestartet. Drücken Sie Strg+C zum Beenden.")
with mouse.Listener(on_click=on_click) as m_listener, \
     keyboard.Listener(on_press=on_press) as k_listener:
    try:
        while running:
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\nProgram interrupted by user")
    finally:
        running = False
        arduino.close()
        print("Serial connection closed")
    
m_listener.stop()
k_listener.stop()