# ESP32 Hardware Credential Vault

This firmware implements a hardware-backed credential vault for Cloud Guardian.

## Features

- AES-256 encrypted AWS credential storage
- Password-protected vault unlock
- Secure credential retrieval over serial
- Password rotation support

## Setup

1. Open `esp32_vault.ino` in Arduino IDE
2. Update the following values:

SETUP_PASSWORD
AWS_ACCESS_KEY
AWS_SECRET_KEY
AWS_REGION

3. Upload firmware to ESP32 DevKit V1

## Usage

Plug ESP32 into the system and run:

cg analyze --hardware-auth

Cloud Guardian will automatically retrieve credentials from the hardware vault.
