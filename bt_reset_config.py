#!/usr/bin/env python3
"""Reset LED strip configuration to restore full 200 LED functionality

This script tries multiple approaches to reset the configuration that might
have been changed by the iDeal LED app (parallel/continuous modes).
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

def build_on_off_packet(state):
    """Build ON/OFF command packet"""
    packet = bytearray.fromhex("05 54 55 52 4E 01 00 00 00 00 00 00 00 00 00 00")
    packet[5] = 1 if state else 0
    return bytes(packet)

def build_set_lamp_count_packet(count):
    """Build LED count configuration packet"""
    packet = bytearray.fromhex("09 4C 41 4D 50 4E 00 32 00 32 00 00 00 00 00 00")
    high = (count >> 8) & 0xFF
    low = count & 0xFF
    packet[6] = high
    packet[7] = low
    packet[8] = high
    packet[9] = low
    return bytes(packet)

async def reset_configuration():
    """Try multiple reset approaches"""
    print("=" * 70)
    print("RESETTING LED STRIP CONFIGURATION")
    print("=" * 70)
    print("This will try multiple approaches to restore 200 LED functionality")
    print("=" * 70)
    
    try:
        async with BleakClient(DEVICE_ADDRESS, timeout=10.0) as client:
            if client.is_connected:
                print("\n✓ Connected!")
                await asyncio.sleep(1.0)
                
                # Approach 1: Power cycle sequence
                print("\n" + "=" * 70)
                print("APPROACH 1: Power Cycle Sequence")
                print("=" * 70)
                print("Turning OFF...")
                off_packet = build_on_off_packet(False)
                encrypted_off = encrypt_aes_ecb(off_packet)
                await client.write_gatt_char(WRITE_CMD_UUID, encrypted_off, response=False)
                await asyncio.sleep(2)
                
                print("Turning ON...")
                on_packet = build_on_off_packet(True)
                encrypted_on = encrypt_aes_ecb(on_packet)
                await client.write_gatt_char(WRITE_CMD_UUID, encrypted_on, response=False)
                await asyncio.sleep(2)
                
                # Approach 2: Set LED count multiple times with different values
                print("\n" + "=" * 70)
                print("APPROACH 2: Reset LED Count (Multiple Attempts)")
                print("=" * 70)
                
                # Try setting to different values first, then 200
                test_counts = [70, 100, 150, 200]
                
                for count in test_counts:
                    print(f"\nSetting LED count to {count}...")
                    packet = build_set_lamp_count_packet(count)
                    encrypted = encrypt_aes_ecb(packet)
                    await client.write_gatt_char(WRITE_CMD_UUID, encrypted, response=False)
                    await asyncio.sleep(1)
                    print(f"  ✓ Sent count={count}")
                
                # Set to 200 multiple times
                print("\nSetting to 200 LEDs (multiple times)...")
                for i in range(3):
                    packet = build_set_lamp_count_packet(200)
                    encrypted = encrypt_aes_ecb(packet)
                    await client.write_gatt_char(WRITE_CMD_UUID, encrypted, response=False)
                    await asyncio.sleep(1)
                    print(f"  Attempt {i+1}/3 sent")
                
                # Approach 3: Try setting all LEDs to white to test
                print("\n" + "=" * 70)
                print("APPROACH 3: Testing with Full Color Command")
                print("=" * 70)
                print("Setting all LEDs to WHITE to test range...")
                
                # Build set_color packet (all white)
                color_packet = bytearray.fromhex("0F 53 47 4C 53 00 00 64 50 1F 00 00 1F 00 00 32")
                # Set to full white (5-bit: 31,31,31)
                color_packet[9] = 31  # R
                color_packet[12] = 31
                color_packet[10] = 31  # G
                color_packet[13] = 31
                color_packet[11] = 31  # B
                color_packet[14] = 31
                
                encrypted_color = encrypt_aes_ecb(bytes(color_packet))
                await client.write_gatt_char(WRITE_CMD_UUID, encrypted_color, response=False)
                await asyncio.sleep(2)
                
                # Approach 4: Try sending LED count command with different timing
                print("\n" + "=" * 70)
                print("APPROACH 4: Aggressive LED Count Reset")
                print("=" * 70)
                print("Sending 200 LED count command 5 times rapidly...")
                
                for i in range(5):
                    packet = build_set_lamp_count_packet(200)
                    encrypted = encrypt_aes_ecb(packet)
                    await client.write_gatt_char(WRITE_CMD_UUID, encrypted, response=False)
                    await asyncio.sleep(0.3)
                
                await asyncio.sleep(1)
                
                # Approach 5: Turn off, set count, turn on sequence
                print("\n" + "=" * 70)
                print("APPROACH 5: OFF -> Set Count -> ON Sequence")
                print("=" * 70)
                
                print("Turning OFF...")
                off_packet = build_on_off_packet(False)
                encrypted_off = encrypt_aes_ecb(off_packet)
                await client.write_gatt_char(WRITE_CMD_UUID, encrypted_off, response=False)
                await asyncio.sleep(1)
                
                print("Setting LED count to 200...")
                count_packet = build_set_lamp_count_packet(200)
                encrypted_count = encrypt_aes_ecb(count_packet)
                await client.write_gatt_char(WRITE_CMD_UUID, encrypted_count, response=False)
                await asyncio.sleep(1)
                
                print("Turning ON...")
                on_packet = build_on_off_packet(True)
                encrypted_on = encrypt_aes_ecb(on_packet)
                await client.write_gatt_char(WRITE_CMD_UUID, encrypted_on, response=False)
                await asyncio.sleep(2)
                
                print("\n" + "=" * 70)
                print("RESET COMPLETE")
                print("=" * 70)
                print("Check your LED strip:")
                print("  - Count how many LEDs are lit")
                print("  - If still only ~70 LEDs work, try these steps:")
                print("\n1. PHYSICAL POWER CYCLE:")
                print("   - Unplug the LED strip power")
                print("   - Wait 10 seconds")
                print("   - Plug back in")
                print("   - Run this script again")
                print("\n2. CHECK iDeal LED APP:")
                print("   - Open the app")
                print("   - Look for 'Settings' or 'Configuration'")
                print("   - Look for 'Mode' settings (Parallel/Continuous)")
                print("   - Try switching back to 'Continuous' mode")
                print("   - Look for 'Reset' or 'Factory Defaults' option")
                print("   - Check for 'Segment' or 'Channel' settings")
                print("\n3. If app has segment/channel settings:")
                print("   - Set segments to 1 (or continuous)")
                print("   - Set channel count to match your LED count")
                print("\n4. The app might have saved a configuration that limits LEDs")
                print("   - Try deleting the device from the app")
                print("   - Re-pair it")
                print("   - Set LED count to 200 in the app")
                
                return True
            else:
                print("✗ Failed to connect")
                return False
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    await reset_configuration()

if __name__ == "__main__":
    asyncio.run(main())

