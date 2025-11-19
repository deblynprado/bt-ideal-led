# iDeal LED Bluetooth Controller

Python scripts for controlling iDeal LED strips via Bluetooth Low Energy (BLE) using the reverse-engineered protocol.

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Scripts](#scripts)
- [Protocol Details](#protocol-details)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

## 🎯 Overview

This repository contains Python scripts to control iDeal LED strips via BLE. The protocol was reverse-engineered from the official iDeal LED Android app. All commands are AES-encrypted using a key extracted from the app.

**Based on:** [8none1/idealLED](https://github.com/8none1/idealLED)

## ✨ Features

- ✅ Turn LED strip ON/OFF
- ✅ Set LED count configuration
- ✅ Set colors (RGB)
- ✅ Control individual LEDs
- ✅ Device discovery and scanning
- ✅ Service and characteristic discovery
- ✅ Hardware diagnostics
- ✅ Configuration troubleshooting

## 📦 Requirements

- Python 3.7+
- macOS, Linux, or Windows
- Bluetooth adapter (built-in or USB)
- iDeal LED controller device

### Python Packages

```bash
pip3 install bleak pycryptodome
```

- **bleak**: Bluetooth Low Energy library
- **pycryptodome**: AES encryption support

## 🚀 Installation

1. Clone this repository:
```bash
git clone <your-repo-url>
cd "BT iDEAL Led"
```

2. Install dependencies:
```bash
pip3 install bleak pycryptodome
```

3. Find your device UUID:
```bash
python3 bt_discover.py
```

4. Update device UUID in scripts:
   - Open any script file
   - Find `DEVICE_ADDRESS = "YOUR-DEVICE-UUID-HERE"`
   - Replace with your device's UUID from step 3

## 🎮 Quick Start

### 1. Discover Your Device

```bash
python3 bt_discover.py
```

This will scan for BLE devices and show their UUIDs and names. Look for your iDeal LED device.

### 2. Basic Control

**Turn device ON:**
```bash
python3 bt_led_control.py on
```

**Turn device OFF:**
```bash
python3 bt_led_control.py off
```

**Set LED count:**
```bash
python3 bt_led_control.py count 200
```

### 3. Test Connection

```bash
python3 bt_ideal_led.py
```

This will test ON/OFF commands on all available characteristics.

## 📜 Scripts

### Core Control Scripts

| Script | Description |
|--------|-------------|
| `bt_discover.py` | Scan and discover BLE devices |
| `bt_ideal_led.py` | Test ON/OFF on all characteristics |
| `bt_led_control.py` | Simple ON/OFF and LED count control |

### Advanced Scripts

| Script | Description |
|--------|-------------|
| `bt_set_led_count.py` | Set LED count configuration |
| `bt_set_all_color.py` | Set all LEDs to a single color |
| `bt_test_leds.py` | Test individual LEDs |
| `bt_read_state.py` | Read device state/characteristics |
| `bt_read_config.py` | Attempt to read device configuration |

### Diagnostic Scripts

| Script | Description |
|--------|-------------|
| `bt_test_hardware.py` | Comprehensive hardware diagnostics |
| `bt_check_firmware.py` | Check firmware version and OTA capabilities |
| `bt_reset_config.py` | Attempt to reset device configuration |
| `bt_reset_mode.py` | Test different modeIndex values |
| `bt_reset_segments.py` | Try to reset segment/channel configuration |
| `bt_factory_reset.py` | Attempt factory reset commands |
| `bt_factory_reset_commands.py` | Try various factory reset commands |
| `bt_find_segment_config.py` | Find segment/channel configuration |
| `bt_test_modelindex.py` | Test modelIndex values 0-8 |

### Documentation

| File | Description |
|------|-------------|
| `FINAL_DIAGNOSIS.md` | Complete diagnosis of LED count limitation issue |
| `FIRMWARE_UPDATE_GUIDE.md` | Guide for firmware updates |
| `HARDWARE_DIAGNOSTIC_GUIDE.md` | Hardware testing procedures |

## 🔧 Protocol Details

### Service and Characteristics

- **Service UUID**: `0000fff0-0000-1000-8000-00805f9b34fb`
- **Write Command UUID**: `d44bc439-abfd-45a2-b575-925416129600`
- **Notification UUID**: `d44bc439-abfd-45a2-b575-925416129601`

### Encryption

All commands are encrypted using **AES-ECB** mode with a 16-byte key:

```python
SECRET_ENCRYPTION_KEY = bytes([
    0x34, 0x52, 0x2A, 0x5B, 0x7A, 0x6E, 0x49, 0x2C,
    0x08, 0x09, 0x0A, 0x9D, 0x8D, 0x2A, 0x23, 0xF8
])
```

### Command Packets

**ON/OFF Command:**
```
05 54 55 52 4E [state] 00 00 00 00 00 00 00 00 00 00
                ^^^^^^
                1 = ON, 0 = OFF
```

**LED Count Command:**
```
09 4C 41 4D 50 4E 00 [high] [low] [high] [low] 00 00 00 00 00 00
                    ^^^^^^^^^^^^^^ ^^^^^^^^^^^^^^
                    LED count (big-endian 16-bit, duplicated)
```

**Set Color Command:**
```
0F 53 47 4C 53 [mode] [reverse] [speed] [sat] [r] [g] [b] [r] [g] [b] [bright]
```

## 🐛 Troubleshooting

### Connection Issues

**Problem:** `TimeoutError` or connection fails

**Solutions:**
1. Make sure device is powered ON
2. Move device closer to computer
3. Check if device is connected to another device (phone, etc.)
4. Try power cycling the device
5. Run `bt_discover.py` to verify device is visible

### Device Not Found

**Problem:** Device doesn't appear in scan

**Solutions:**
1. Make sure device is powered ON
2. Check Bluetooth is enabled on your computer
3. Try running scan multiple times
4. Move device closer
5. Check device name - it might show as "Unknown"

### Commands Not Working

**Problem:** Commands sent but device doesn't respond

**Solutions:**
1. Verify device UUID is correct
2. Check device is not connected to another device
3. Try sending command multiple times
4. Check if device blinks (acknowledgment)
5. Verify encryption key is correct

### LED Count Limitation

**Problem:** Only ~70 LEDs work instead of 200

**This is a known firmware/configuration issue:**
- Device may be stuck in "parallel mode"
- Configuration stored in non-volatile memory
- See `FINAL_DIAGNOSIS.md` for details
- Try firmware update or manufacturer reset

## 📝 Usage Examples

### Example 1: Basic ON/OFF

```python
python3 bt_led_control.py on
python3 bt_led_control.py off
```

### Example 2: Set LED Count

```python
python3 bt_led_control.py count 200
```

### Example 3: Discover Devices

```python
python3 bt_discover.py
```

### Example 4: Hardware Diagnostics

```python
python3 bt_test_hardware.py
```

## 🔍 Finding Your Device UUID

1. Run discovery:
```bash
python3 bt_discover.py
```

2. Look for your device in the list (may show as "Unknown" or device name)

3. Copy the UUID (format: `XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX`)

4. Update scripts:
   - Open any script
   - Find `DEVICE_ADDRESS = "YOUR-DEVICE-UUID-HERE"`
   - Replace with your UUID

## 📚 Additional Resources

- [Original Repository](https://github.com/8none1/idealLED)
- [BLE Protocol Documentation](https://github.com/8none1/idealLED)
- [Home Assistant Integration](https://github.com/8none1/idealLED)

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## ⚠️ Disclaimer

This software is provided "as is" without warranty. Use at your own risk. The protocol was reverse-engineered and may not work with all iDeal LED devices or firmware versions.

## 📄 License

This project is based on the work from [8none1/idealLED](https://github.com/8none1/idealLED). Please refer to the original repository for license information.

## 🙏 Acknowledgments

- [8none1](https://github.com/8none1) for reverse-engineering the protocol
- The iDeal LED community for testing and feedback

---

**Note:** Make sure to update `DEVICE_ADDRESS` in all scripts with your device's UUID before use!

