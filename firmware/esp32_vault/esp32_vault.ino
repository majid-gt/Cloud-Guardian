#include <Preferences.h>
#include <ArduinoJson.h>
#include "mbedtls/sha256.h"
#include "mbedtls/aes.h"
#include "esp_system.h"

Preferences preferences;

// ====== PROVISIONING DATA (USED ONLY ON FIRST BOOT) ======
const char* SETUP_PASSWORD = "YOUR PASSWORD";
const char* AWS_ACCESS_KEY = "YOUR AWS ACCESS KEY";
const char* AWS_SECRET_KEY = "YOUR AWS SECRET KEY";
const char* AWS_REGION     = "YOUR AWS REGION";

// ====== CONFIG ======
#define SALT_LENGTH 16
#define AES_KEY_LENGTH 32
#define AES_BLOCK_SIZE 16

// ====== FUNCTION DECLARATIONS ======
void runProvisioning();
void handleUnlock(String password);
void handleChangePassword(String oldPassword, String newPassword);
void sha256(const String &input, uint8_t output[32]);
void deriveKey(const String &password, uint8_t salt[SALT_LENGTH], uint8_t key[32]);
void aesEncrypt(uint8_t* plaintext, size_t length, uint8_t key[32], uint8_t** ciphertext, size_t* outLength);
void aesDecrypt(uint8_t* ciphertext, size_t length, uint8_t key[32], uint8_t** plaintext, size_t* outLength);

// ==========================================================

void setup() {
  Serial.begin(115200);
  delay(2000);

  preferences.begin("vault", false);

  if (!preferences.isKey("phash")) {
    Serial.println("Vault not initialized. Running provisioning...");
    runProvisioning();
  } else {
    Serial.println("Vault Ready.");
  }
}

void sha256(const String &input, uint8_t output[32]) {
  mbedtls_sha256_context ctx;
  mbedtls_sha256_init(&ctx);
  mbedtls_sha256_starts(&ctx, 0);  // 0 = SHA256
  mbedtls_sha256_update(&ctx, (const unsigned char*)input.c_str(), input.length());
  mbedtls_sha256_finish(&ctx, output);
  mbedtls_sha256_free(&ctx);
}

void deriveKey(const String &password, uint8_t salt[SALT_LENGTH], uint8_t key[32]) {
  mbedtls_sha256_context ctx;
  mbedtls_sha256_init(&ctx);
  mbedtls_sha256_starts(&ctx, 0);

  mbedtls_sha256_update(&ctx, (const unsigned char*)password.c_str(), password.length());
  mbedtls_sha256_update(&ctx, salt, SALT_LENGTH);

  mbedtls_sha256_finish(&ctx, key);
  mbedtls_sha256_free(&ctx);
}

void aesEncrypt(uint8_t* plaintext, size_t length, uint8_t key[32], uint8_t** ciphertext, size_t* outLength) {

  size_t paddedLength = length;
  uint8_t padding = AES_BLOCK_SIZE - (length % AES_BLOCK_SIZE);
  paddedLength += padding;

  uint8_t* padded = (uint8_t*)malloc(paddedLength);
  memcpy(padded, plaintext, length);

  // PKCS7 padding
  for (size_t i = length; i < paddedLength; i++) {
    padded[i] = padding;
  }

  // Allocate output: IV + ciphertext
  *outLength = paddedLength + AES_BLOCK_SIZE;
  *ciphertext = (uint8_t*)malloc(*outLength);

  uint8_t iv[AES_BLOCK_SIZE];
  esp_fill_random(iv, AES_BLOCK_SIZE);

  // Copy IV to beginning
  memcpy(*ciphertext, iv, AES_BLOCK_SIZE);

  mbedtls_aes_context ctx;
  mbedtls_aes_init(&ctx);
  mbedtls_aes_setkey_enc(&ctx, key, 256);

  mbedtls_aes_crypt_cbc(&ctx, MBEDTLS_AES_ENCRYPT,
                        paddedLength,
                        iv,
                        padded,
                        *ciphertext + AES_BLOCK_SIZE);

  mbedtls_aes_free(&ctx);

  free(padded);
}

void aesDecrypt(uint8_t* ciphertext, size_t length, uint8_t key[32], uint8_t** plaintext, size_t* outLength) {

  uint8_t iv[AES_BLOCK_SIZE];
  memcpy(iv, ciphertext, AES_BLOCK_SIZE);

  size_t cipherLength = length - AES_BLOCK_SIZE;

  uint8_t* decrypted = (uint8_t*)malloc(cipherLength);

  mbedtls_aes_context ctx;
  mbedtls_aes_init(&ctx);
  mbedtls_aes_setkey_dec(&ctx, key, 256);

  mbedtls_aes_crypt_cbc(&ctx, MBEDTLS_AES_DECRYPT,
                        cipherLength,
                        iv,
                        ciphertext + AES_BLOCK_SIZE,
                        decrypted);

  mbedtls_aes_free(&ctx);

  // Remove PKCS7 padding
  uint8_t padding = decrypted[cipherLength - 1];
  *outLength = cipherLength - padding;

  *plaintext = (uint8_t*)malloc(*outLength);
  memcpy(*plaintext, decrypted, *outLength);

  free(decrypted);
}

void runProvisioning() {

  // Generate random salt
  uint8_t salt[SALT_LENGTH];
  esp_fill_random(salt, SALT_LENGTH);

  // Hash password
  uint8_t passwordHash[32];
  sha256(String(SETUP_PASSWORD), passwordHash);

  // Derive AES key
  uint8_t key[32];
  deriveKey(String(SETUP_PASSWORD), salt, key);

  // Create credentials JSON
  StaticJsonDocument<256> doc;
  doc["access_key"] = AWS_ACCESS_KEY;
  doc["secret_key"] = AWS_SECRET_KEY;
  doc["region"]     = AWS_REGION;

  String credentialsJson;
  serializeJson(doc, credentialsJson);

  // Encrypt credentials
  uint8_t* ciphertext;
  size_t cipherLength;

  aesEncrypt(
    (uint8_t*)credentialsJson.c_str(),
    credentialsJson.length(),
    key,
    &ciphertext,
    &cipherLength
  );

  // Store in NVS
  preferences.putBytes("salt", salt, SALT_LENGTH);
  preferences.putBytes("blob", ciphertext, cipherLength);
  preferences.putBytes("phash", passwordHash, 32);

  free(ciphertext);

  Serial.println("Provisioning Complete.");
}


void handleUnlock(String password) {

  uint8_t storedHash[32];
  preferences.getBytes("phash", storedHash, 32);

  uint8_t incomingHash[32];
  sha256(password, incomingHash);

  if (memcmp(storedHash, incomingHash, 32) != 0) {
    Serial.println("{\"status\":\"denied\"}");
    return;
  }

  uint8_t salt[SALT_LENGTH];
  preferences.getBytes("salt", salt, SALT_LENGTH);

  uint8_t key[32];
  deriveKey(password, salt, key);

  size_t blobLength = preferences.getBytesLength("blob");

  if (blobLength == 0) {
    Serial.println("{\"status\":\"denied\"}");
    return;
  }

  uint8_t* blob = (uint8_t*)malloc(blobLength);
  preferences.getBytes("blob", blob, blobLength);

  uint8_t* plaintext;
  size_t plainLength;

  aesDecrypt(blob, blobLength, key, &plaintext, &plainLength);

  free(blob);

  StaticJsonDocument<256> credDoc;
  deserializeJson(credDoc, plaintext, plainLength);

  StaticJsonDocument<512> response;
  response["status"] = "ok";
  response["access_key"] = credDoc["access_key"];
  response["secret_key"] = credDoc["secret_key"];
  response["region"]     = credDoc["region"];

  serializeJson(response, Serial);
  Serial.println();

  free(plaintext);
}

void handleChangePassword(String oldPassword, String newPassword) {

  uint8_t storedHash[32];
  preferences.getBytes("phash", storedHash, 32);

  uint8_t incomingHash[32];
  sha256(oldPassword, incomingHash);

  // Verify old password
  if (memcmp(storedHash, incomingHash, 32) != 0) {
    Serial.println("{\"status\":\"denied\"}");
    return;
  }

  // Load salt and encrypted blob
  uint8_t oldSalt[SALT_LENGTH];
  preferences.getBytes("salt", oldSalt, SALT_LENGTH);

  size_t blobLength = preferences.getBytesLength("blob");
  if (blobLength == 0) {
    Serial.println("{\"status\":\"error\"}");
    return;
  }

  uint8_t* blob = (uint8_t*)malloc(blobLength);
  preferences.getBytes("blob", blob, blobLength);

  // Derive old key
  uint8_t oldKey[32];
  deriveKey(oldPassword, oldSalt, oldKey);

  // Decrypt existing credentials
  uint8_t* plaintext;
  size_t plainLength;
  aesDecrypt(blob, blobLength, oldKey, &plaintext, &plainLength);

  free(blob);

  // Generate new salt
  uint8_t newSalt[SALT_LENGTH];
  esp_fill_random(newSalt, SALT_LENGTH);

  // Derive new key
  uint8_t newKey[32];
  deriveKey(newPassword, newSalt, newKey);

  // Encrypt credentials again
  uint8_t* newCipher;
  size_t newCipherLength;

  aesEncrypt(plaintext, plainLength, newKey, &newCipher, &newCipherLength);

  free(plaintext);

  // Store new values
  uint8_t newHash[32];
  sha256(newPassword, newHash);

  preferences.putBytes("salt", newSalt, SALT_LENGTH);
  preferences.putBytes("blob", newCipher, newCipherLength);
  preferences.putBytes("phash", newHash, 32);

  free(newCipher);

  Serial.println("{\"status\":\"password_changed\"}");
}

void loop() {
  if (Serial.available()) {
    String input = Serial.readStringUntil('\n');

    StaticJsonDocument<512> doc;
    DeserializationError error = deserializeJson(doc, input);

    if (error) return;

    const char* command = doc["command"];

    if (strcmp(command, "unlock") == 0) {
      String password = doc["password"];
      handleUnlock(password);
    }
    else if (strcmp(command, "change_password") == 0) {
      String oldPassword = doc["old_password"];
      String newPassword = doc["new_password"];
      handleChangePassword(oldPassword, newPassword);
    }
  }
}