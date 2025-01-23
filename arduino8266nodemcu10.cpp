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

void setup() {
  Serial.begin(9600);
  while (!Serial) {}
  
  aes.setKey(aesKey, sizeof(aesKey));
}

// Funktion zum Verschlüsseln eines 16-Byte Blocks
void encryptBlock(byte* output, const byte* input) {
  aes.encryptBlock(output, input);
}

// Funktion zum Entschlüsseln eines 16-Byte Blocks
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

    Serial.print("Verschluesselt: ");
    for (int i = 0; i < 16; i++) {
      if (encrypted[i] < 16) Serial.print('0');
      Serial.print(encrypted[i], HEX);
    }
    Serial.println();
  }
}