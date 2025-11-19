#!/usr/bin/env python3
"""Set the LED count for iDeal LED lights

Based on: https://github.com/8none1/idealLED

Usage:
    python3 bt_set_led_count.py [count]
    
Examples:
    python3 bt_set_led_count.py 200    # Set to 200 LEDs
    python3 bt_set_led_count.py 100    # Set to 100 LEDs
"""
import asyncio
import sys
from bleak import BleakClient
from Crypto.Cipher import AES

# Device address - UPDATE THIS with your device UUID
DEVICE_ADDRESS = "F0E047EE-ECB2-EAF3-D11B-1C52E2751387"

# Protocol constants from https://github.com/8none1/idealLED
SERVICE_UUID = "0000fff0-0000-1000-8000-00805f9b34fb"
WRITE_CMD_UUID = "d44bc439-abfd-45a2-b575-925416129600"

# AES encryption key
SECRET_ENCRYPTION_KEY = bytes([0x34, 0x52, 0x2A, 0x5B, 0x7A, 0x6E, 0x49, 0x2C, 
                                0x08, 0x09, 0x0A, 0x9D, 0x8D, 0x2A, 0x23, 0xF8])

def encrypt_aes_ecb(plaintext):
    """Encrypt packet using AES ECB mode"""
    if len(plaintext) < 16:
        plaintext = plaintext + bytes(16 - len(plaintext))
    elif len(plaintext) > 16:
        plaintext = plaintext[:16]
    
    cipher = AES.new(SECRET_ENCRYPTION_KEY, AES.MODE_ECB)
    ciphertext = cipher.encrypt(plaintext)
    return ciphertext

def build_set_lamp_count_packet(count):
    """
    Build LED count configuration packet
    
    Format: 09 4C 41 4D 50 4E 00 [high] [low] [high] [low] 00 00 00 00 00 00
            |---------------| |   | |   | |---------------|
                  header      |---| |---|       footer
                            lamp count (big endian, duplicated)
    
    Bytes 6-7: LED count high/low (big endian)
    Bytes 8-9: Same count duplicated
    """
    packet = bytearray.fromhex("09 4C 41 4D 50 4E 00 32 00 32 00 00 00 00 00 00")
    
    # Extract high and low bytes (big endian)
    high = (count >> 8) & 0xFF
    low = count & 0xFF
    
    # Set the count in both positions (duplicated)
    packet[6] = high
    packet[7] = low
    packet[8] = high
    packet[9] = low
    
    return bytes(packet)

async def set_led_count(count):
    """Set the LED count on the device"""
    if count < 1 or count > 1000:
        print(f"Error: LED count must be between 1 and 1000 (got {count})")
        return False
    
    print(f"Setting LED count to {count}...")
    print(f"Connecting to device: {DEVICE_ADDRESS}")
    
    try:
        async with BleakClient(DEVICE_ADDRESS, timeout=10.0) as client:
            if client.is_connected:
                print(f"✓ Connected!")
                await asyncio.sleep(1.0)
                
                # Build the LED count packet
                packet = build_set_lamp_count_packet(count)
                print(f"Plain packet: {packet.hex()}")
                
                # Encrypt the packet
                encrypted = encrypt_aes_ecb(packet)
                print(f"Encrypted packet: {encrypted.hex()}")
                
                # Send command
                try:
                    await client.write_gatt_char(WRITE_CMD_UUID, encrypted, response=True)
                    print(f"✓ Sent with response")
                except:
                    await client.write_gatt_char(WRITE_CMD_UUID, encrypted, response=False)
                    print(f"✓ Sent without response")
                
                print(f"\n✓ LED count set to {count}!")
                print(f"  Device will blink 3 times to acknowledge")
                print(f"  All {count} LEDs should now be active")
                return True
            else:
                print("✗ Failed to connect")
                return False
    except asyncio.TimeoutError:
        print("\n✗ Connection timeout!")
        print("Make sure device is powered ON and within range")
        return False
    except Exception as e:
        print(f"\n✗ Error: {e}")
        return False

async def main():
    """Main function"""
    if len(sys.argv) < 2:
        print("Usage: python3 bt_set_led_count.py [count]")
        print("\nExamples:")
        print("  python3 bt_set_led_count.py 200    # Set to 200 LEDs")
        print("  python3 bt_set_led_count.py 100    # Set to 100 LEDs")
        print("  python3 bt_set_led_count.py 144    # Set to 144 LEDs")
        sys.exit(1)
    
    try:
        count = int(sys.argv[1])
    except ValueError:
        print(f"Error: '{sys.argv[1]}' is not a valid number")
        sys.exit(1)
    
    success = await set_led_count(count)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    asyncio.run(main())

