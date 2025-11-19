#!/usr/bin/env python3
"""Attempt factory reset by trying various reset-like commands

Since the mode configuration persists, we'll try various commands that might
reset the device to factory defaults.
"""
import asyncio
from bleak import BleakClient
from Crypto.Cipher import AES

# Device address
DEVICE_ADDRESS = "F0E047EE-ECB2-EAF3-D11B-1C52E2751387"

# Protocol constants
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

async def try_factory_reset():
    """Try various commands that might reset factory defaults"""
    print("=" * 70)
    print("ATTEMPTING FACTORY RESET")
    print("=" * 70)
    print("Trying various reset-like commands")
    print("=" * 70)
    
    # Potential reset commands to try
    # These are educated guesses based on common patterns
    reset_attempts = [
        # All zeros (common reset pattern)
        (bytes([0] * 16), "All zeros"),
        # All 0xFF (another reset pattern)
        (bytes([0xFF] * 16), "All 0xFF"),
        # RESET command (if it exists)
        (bytes([0x52, 0x45, 0x53, 0x45, 0x54] + [0] * 11), "RESET text"),
        # Factory reset pattern
        (bytes([0x46, 0x41, 0x43, 0x54, 0x4F, 0x52, 0x59] + [0] * 9), "FACTORY text"),
        # Default/Init patterns
        (bytes([0x44, 0x45, 0x46, 0x41, 0x55, 0x4C, 0x54] + [0] * 9), "DEFAULT text"),
        (bytes([0x49, 0x4E, 0x49, 0x54] + [0] * 12), "INIT text"),
    ]
    
    try:
        async with BleakClient(DEVICE_ADDRESS, timeout=10.0) as client:
            if client.is_connected:
                print("\n✓ Connected!")
                await asyncio.sleep(1.0)
                
                print("\nWARNING: These commands are experimental!")
                print("They might not work or could have unexpected effects.")
                print("Proceed? (The device should be safe, but use at your own risk)")
                print("\nTrying reset commands...")
                
                for packet, description in reset_attempts:
                    try:
                        print(f"\n  Trying: {description}")
                        print(f"    Packet: {packet.hex()}")
                        encrypted = encrypt_aes_ecb(packet)
                        await client.write_gatt_char(WRITE_CMD_UUID, encrypted, response=False)
                        print(f"    ✓ Sent")
                        await asyncio.sleep(1)
                    except Exception as e:
                        print(f"    ✗ Failed: {e}")
                
                # After reset attempts, try setting LED count to 200
                print("\n" + "=" * 70)
                print("Setting LED count to 200 after reset attempts...")
                print("=" * 70)
                
                count_packet = bytearray.fromhex("09 4C 41 4D 50 4E 00 32 00 32 00 00 00 00 00 00")
                count_packet[6] = 0x00  # High byte of 200 (0x00C8)
                count_packet[7] = 0xC8  # Low byte of 200
                count_packet[8] = 0x00
                count_packet[9] = 0xC8
                
                encrypted_count = encrypt_aes_ecb(bytes(count_packet))
                await client.write_gatt_char(WRITE_CMD_UUID, encrypted_count, response=False)
                print("✓ Set LED count to 200")
                
                await asyncio.sleep(1)
                
                # Turn on and set color
                on_packet = bytearray.fromhex("05 54 55 52 4E 01 00 00 00 00 00 00 00 00 00 00")
                on_packet[5] = 1
                encrypted_on = encrypt_aes_ecb(bytes(on_packet))
                await client.write_gatt_char(WRITE_CMD_UUID, encrypted_on, response=False)
                await asyncio.sleep(1)
                
                color_packet = bytearray.fromhex("0F 53 47 4C 53 00 00 64 50 1F 1F 1F 1F 1F 1F 32")
                encrypted_color = encrypt_aes_ecb(bytes(color_packet))
                await client.write_gatt_char(WRITE_CMD_UUID, encrypted_color, response=False)
                print("✓ Set all LEDs to white")
                
                print("\n" + "=" * 70)
                print("Check your LED strip - do all 200 LEDs light up?")
                print("=" * 70)
                
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
    asyncio.run(try_factory_reset())

