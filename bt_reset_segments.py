#!/usr/bin/env python3
"""Try to reset segment/channel configuration

The "parallel" mode might have split the strip into segments.
This script tries to reset it back to continuous mode (1 segment, 200 LEDs).
"""
import asyncio
from bleak import BleakClient
from Crypto.Cipher import AES

# Device address
DEVICE_ADDRESS = "F0E047EE-ECB2-EAF3-D11B-1C52E2751387"

# Protocol constants
WRITE_CMD_UUID = "d44bc439-abfd-45a2-b575-925416129600"
WRITE_DATA_UUID = "d44bc439-abfd-45a2-b575-92541612960a"

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
    """Build LED count configuration packet"""
    packet = bytearray.fromhex("09 4C 41 4D 50 4E 00 32 00 32 00 00 00 00 00 00")
    high = (count >> 8) & 0xFF
    low = count & 0xFF
    packet[6] = high
    packet[7] = low
    packet[8] = high
    packet[9] = low
    return bytes(packet)

def build_on_off_packet(state):
    """Build ON/OFF command packet"""
    packet = bytearray.fromhex("05 54 55 52 4E 01 00 00 00 00 00 00 00 00 00 00")
    packet[5] = 1 if state else 0
    return bytes(packet)

async def try_segment_reset():
    """Try various approaches to reset segment configuration"""
    print("=" * 70)
    print("ATTEMPTING TO RESET SEGMENT CONFIGURATION")
    print("=" * 70)
    print("Trying commands that might reset parallel mode to continuous")
    print("=" * 70)
    
    try:
        async with BleakClient(DEVICE_ADDRESS, timeout=10.0) as client:
            if client.is_connected:
                print("\n✓ Connected!")
                await asyncio.sleep(1.0)
                
                # Turn ON
                print("\nTurning device ON...")
                on_packet = build_on_off_packet(True)
                encrypted_on = encrypt_aes_ecb(on_packet)
                await client.write_gatt_char(WRITE_CMD_UUID, encrypted_on, response=False)
                await asyncio.sleep(1)
                
                # Set LED count to 200
                print("Setting LED count to 200...")
                count_packet = build_set_lamp_count_packet(200)
                encrypted_count = encrypt_aes_ecb(count_packet)
                await client.write_gatt_char(WRITE_CMD_UUID, encrypted_count, response=False)
                await asyncio.sleep(1)
                
                # Try different approaches
                print("\n" + "=" * 70)
                print("APPROACH 1: Try setting segment count to 1")
                print("=" * 70)
                
                # Try various packet formats that might set segment count
                segment_commands = [
                    # Format: [length] [command] [segment_count] [rest]
                    (bytearray([0x08, 0x53, 0x45, 0x47, 0x4D, 0x45, 0x4E, 0x54, 0x01] + [0] * 7), "Segment=1 (text)"),
                    (bytearray([0x06, 0x53, 0x45, 0x47, 0x01, 0x00] + [0] * 10), "Seg=1 (short)"),
                    (bytearray([0x09, 0x4D, 0x4F, 0x44, 0x45, 0x00, 0x00, 0x00, 0x00] + [0] * 7), "Mode=0"),
                    (bytearray([0x0A, 0x43, 0x4F, 0x4E, 0x54, 0x49, 0x4E, 0x55, 0x4F, 0x55, 0x53] + [0] * 5), "Continuous"),
                ]
                
                for cmd_bytes, desc in segment_commands:
                    try:
                        print(f"\n  Trying: {desc}")
                        print(f"    Packet: {cmd_bytes.hex()}")
                        encrypted = encrypt_aes_ecb(bytes(cmd_bytes))
                        await client.write_gatt_char(WRITE_CMD_UUID, encrypted, response=False)
                        await asyncio.sleep(0.5)
                        
                        # Set LED count again
                        await client.write_gatt_char(WRITE_CMD_UUID, encrypted_count, response=False)
                        await asyncio.sleep(0.5)
                        
                        # Set color to test
                        color_packet = bytearray.fromhex("0F 53 47 4C 53 00 00 64 50 1F 1F 1F 1F 1F 1F 32")
                        encrypted_color = encrypt_aes_ecb(bytes(color_packet))
                        await client.write_gatt_char(WRITE_CMD_UUID, encrypted_color, response=False)
                        print(f"    ✓ Sent - Check your strip!")
                        await asyncio.sleep(3)
                    except Exception as e:
                        print(f"    ✗ Failed: {e}")
                
                # Try writing to WRITE_DATA_UUID instead
                print("\n" + "=" * 70)
                print("APPROACH 2: Try writing segment commands to DATA UUID")
                print("=" * 70)
                
                for cmd_bytes, desc in segment_commands[:2]:  # Try first 2
                    try:
                        print(f"\n  Trying on DATA UUID: {desc}")
                        encrypted = encrypt_aes_ecb(bytes(cmd_bytes))
                        await client.write_gatt_char(WRITE_DATA_UUID, encrypted, response=False)
                        await asyncio.sleep(0.5)
                        await client.write_gatt_char(WRITE_CMD_UUID, encrypted_count, response=False)
                        await asyncio.sleep(0.5)
                        color_packet = bytearray.fromhex("0F 53 47 4C 53 00 00 64 50 1F 1F 1F 1F 1F 1F 32")
                        encrypted_color = encrypt_aes_ecb(bytes(color_packet))
                        await client.write_gatt_char(WRITE_CMD_UUID, encrypted_color, response=False)
                        print(f"    ✓ Sent - Check your strip!")
                        await asyncio.sleep(3)
                    except Exception as e:
                        print(f"    ✗ Failed: {e}")
                
                print("\n" + "=" * 70)
                print("TESTING COMPLETE")
                print("=" * 70)
                print("If still only 70 LEDs work, the configuration might be:")
                print("  1. Firmware-limited and can't be changed via BLE")
                print("  2. Requires a specific reset command we haven't found")
                print("  3. Stored in protected memory")
                print("\nLast resort options:")
                print("  - Physical reset button on controller (if exists)")
                print("  - Extended power cycle (unplug for hours)")
                print("  - Firmware update from manufacturer")
                print("  - Use the app on a different device to reset")
                
                return True
            else:
                print("✗ Failed to connect")
                return False
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    asyncio.run(try_segment_reset())

