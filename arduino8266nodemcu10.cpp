#include <Crypto.h>
#include <AES.h>
#include <string.h>

// AES256 32 Byte Key
byte aesKey[] = {
  0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07,
  0x08, 0x09, 0x0A, 0x0B, 0x0C, 0x0D, 0x0E, 0x0F,
  0x10, 0x11, 0x12, 0x13, 0x14, 0x15, 0x16, 0x17,
  0x18, 0x19, 0x1A, 0x1B, 0x1C, 0x1D, 0x1E, 0x1F
};

AES256 aes;

// Timing
unsigned long encryptStartTime;
unsigned long encryptEndTime;

void setup() {
  Serial.begin(9600);
  while (!Serial) {}
  
  aes.setKey(aesKey, sizeof(aesKey));
}

// Encrypt 16 Byte Block
void encryptBlock(byte* output, const byte* input) {
  encryptStartTime = micros();
  aes.encryptBlock(output, input);
  encryptEndTime = micros();
  unsigned long encrypt_time = encryptEndTime - encryptStartTime;
  
  Serial.print("$ $ ARDUINO: successfully received Coordinates ");
  for(int i = 0; i < 16; i++) Serial.print((char)input[i]);
  Serial.println(" $ $");
  
  Serial.print("$ $ ARDUINO: Encrypted to ");
  for (int i = 0; i < 16; i++) {
    if (output[i] < 16) Serial.print('0');
    Serial.print(output[i], HEX);
  }
  Serial.print(" (This took: ");
  Serial.print(encrypt_time);
  Serial.println(" Microseconds) $ $");
  
  Serial.println("$ $ ARDUINO: Sending back encrypted data $ $");
  
  Serial.print("ENC_DATA:");
  for (int i = 0; i < 16; i++) {
    if (output[i] < 16) Serial.print('0');
    Serial.print(output[i], HEX);
  }
  Serial.println();
}

// Decrypt 16 Byte Block
void decryptBlock(byte* output, const byte* input) {
  aes.decryptBlock(output, input);
}

void loop() {
  if (Serial.available() >= 16) {
    byte inputBlock[16];
    byte encrypted[16];
    
    for (int i = 0; i < 16; i++) {
      inputBlock[i] = (byte)Serial.read();
    }
    
    encryptBlock(encrypted, inputBlock);
  }
}