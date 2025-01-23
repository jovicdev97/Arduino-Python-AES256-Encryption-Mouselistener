import serial
import time
from pynput import mouse, keyboard
from Cryptodome.Cipher import AES

# AES256-Schlüssel (muss mit dem Arduino-Sketch übereinstimmen)
aes_key = bytes([
    0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07,
    0x08, 0x09, 0x0A, 0x0B, 0x0C, 0x0D, 0x0E, 0x0F,
    0x10, 0x11, 0x12, 0x13, 0x14, 0x15, 0x16, 0x17,
    0x18, 0x19, 0x1A, 0x1B, 0x1C, 0x1D, 0x1E, 0x1F
])

# Verbindung mit Arduino
arduino = serial.Serial('COM3', 9600, timeout=1) 
time.sleep(2)  # Warten auf Arduino-Reset

def format_coordinates(x, y):
    """Formatiert Mauskoordinaten als 16-Byte-String."""
    coord_str = f"x{int(x):04d}y{int(y):04d}      "  # Enough spaces for 16 total bytes - we need to send exactly 16
    return coord_str

def decrypt_data(encrypted_hex):
    """Entschlüsselt empfangene verschlüsselte Daten (Hex-String)."""
    encrypted_data = bytes.fromhex(encrypted_hex)
    cipher = AES.new(aes_key, AES.MODE_ECB)
    decrypted_data = cipher.decrypt(encrypted_data)
    return decrypted_data.decode("utf-8", errors="ignore")

def on_click(x, y, button, pressed):
    if pressed:
        coord_str = format_coordinates(x, y)
        print(f"Mausklick bei: {x}, {y}")
        print(f"Formatiert als: {coord_str}")

        # Daten Arduino senden
        arduino.write(coord_str.encode())
        time.sleep(0.1)  # Warten Antwort Arduino

        # Antwort Arduino lesen
        while arduino.in_waiting:
            try:
                response = arduino.readline().decode("latin-1", errors="ignore").strip()
                print(f"DEBUG: Arduino raw response -> {response}")
                if response.startswith("Verschluesselt:"):
                    encrypted_hex = response.split(":")[1].strip()
                    print(f"Verschlüsselt empfangen: {encrypted_hex}")

                    # Entschlüsseln + anzeigen
                    decrypted = decrypt_data(encrypted_hex)
                    print(f"Entschlüsselte Daten: {decrypted}")
            except UnicodeDecodeError:
                print("Could not decode response.")

def on_press(key):
    if key == keyboard.Key.esc:
        print("Escape pressed, exiting.")
        return False

# Listener start
print("Mausklick-Erfassung gestartet. Drücken Sie Strg+C zum Beenden.")
with mouse.Listener(on_click=on_click) as m_listener, keyboard.Listener(on_press=on_press) as k_listener:
    m_listener.join()
    k_listener.join()
