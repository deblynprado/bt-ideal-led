#!/usr/bin/env python3
"""Test individual LEDs to find the limit

This script will test LEDs at different positions to see which ones work.
"""
import asyncio
import sys
from bleak import BleakClient
from Crypto.Cipher import AES

# Device address - UPDATE THIS with your device UUID
# Find your device UUID by running: python3 bt_discover.py
DEVICE_ADDRESS = "YOUR-DEVICE-UUID-HERE"

# Protocol constants
SERVICE_UUID = "0000fff0-0000-1000-8000-00805f9b34fb"
WRITE_CMD_UUID = "d44bc439-abfd-45a2-b575-925416129600"
WRITE_DATA_UUID = "d44bc439-abfd-45a2-b575-92541612960a"  # For color data

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

def build_graffiti_paint_packet(led_num, r, g, b, mode=2, speed=50, brightness=100):
    """
    Build packet to set a single LED to a specific color
    Format: 0D 44 4F 4F 44 01 00 [led_num] [mode] [speed] [r] [g] [b] [brightness] 00 00
    """
    packet = bytearray.fromhex("0D 44 4F 4F 44 01 00 06 00 19 FF 00 00 64 00 00")
    packet[7] = led_num & 0xFF  # LED number (single byte, so max 255)
    packet[8] = mode  # 2=solid, 1=fade, 0=flash
    packet[9] = speed  # 0-100
    packet[10] = r & 0xFF
    packet[11] = g & 0xFF
    packet[12] = b & 0xFF
    packet[13] = brightness & 0xFF
    return bytes(packet)

async def test_led_range(start_led, end_led, test_color=(255, 0, 0)):
    """Test LEDs in a range to see which ones light up"""
    print(f"\n{'='*70}")
    print(f"TESTING LEDs {start_led} to {end_led}")
    print(f"{'='*70}")
    print(f"Setting LEDs to RED color to test visibility")
    print(f"Watch your strip - note which LEDs light up!")
    
    try:
        async with BleakClient(DEVICE_ADDRESS, timeout=10.0) as client:
            if client.is_connected:
                print(f"✓ Connected!")
                await asyncio.sleep(1.0)
                
                # First, turn on the device
                print("\nTurning device ON...")
                on_packet = bytearray.fromhex("05 54 55 52 4E 01 00 00 00 00 00 00 00 00 00 00")
                on_packet[5] = 1
                encrypted_on = encrypt_aes_ecb(bytes(on_packet))
                await client.write_gatt_char(WRITE_CMD_UUID, encrypted_on, response=False)
                await asyncio.sleep(2)
                
                # Test LEDs in the range
                r, g, b = test_color
                working_leds = []
                not_working_leds = []
                
                print(f"\nTesting LEDs {start_led} to {end_led}...")
                print("Watch your strip carefully!")
                
                for led_num in range(start_led, end_led + 1):
                    print(f"  Testing LED {led_num}...", end=" ", flush=True)
                    
                    # Build and send graffiti paint packet
                    packet = build_graffiti_paint_packet(led_num, r, g, b, mode=2, speed=50, brightness=100)
                    encrypted = encrypt_aes_ecb(packet)
                    
                    try:
                        await client.write_gatt_char(WRITE_CMD_UUID, encrypted, response=False)
                        print(f"✓ Sent")
                        await asyncio.sleep(0.5)  # Wait to see if LED lights up
                        # Note: We can't automatically detect if it lit up, user needs to observe
                    except Exception as e:
                        print(f"✗ Failed: {e}")
                    
                    # Ask user if this LED lit up
                    if led_num % 10 == 0:
                        print(f"\n  → Checked LEDs {start_led}-{led_num}. Continue? (LEDs should be RED if working)")
                        await asyncio.sleep(1)
                
                print(f"\n{'='*70}")
                print("TEST COMPLETE")
                print(f"{'='*70}")
                print(f"Tested LEDs {start_led} to {end_led}")
                print("Please observe which LEDs lit up RED on your strip")
                print("\nIf LEDs beyond 70 don't light up, possible reasons:")
                print("  1. Hardware limitation - controller only supports ~70 LEDs")
                print("  2. Power limitation - not enough power for 200 LEDs")
                print("  3. Physical issue - strip damaged after LED 70")
                print("  4. Need different configuration for longer strips")
                
            else:
                print("✗ Failed to connect")
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()

async def main():
    """Main function"""
    if len(sys.argv) >= 3:
        start = int(sys.argv[1])
        end = int(sys.argv[2])
    else:
        # Default: test around the 70 LED mark
        start = 60
        end = 100
    
    await test_led_range(start, end)

if __name__ == "__main__":
    asyncio.run(main())

