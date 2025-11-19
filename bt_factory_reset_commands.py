#!/usr/bin/env python3
"""Try factory reset commands

Attempts various factory reset commands that might restore
the device to default configuration (200 LEDs, continuous mode).
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

async def try_factory_reset():
    """Try various factory reset commands"""
    print("=" * 70)
    print("ATTEMPTING FACTORY RESET COMMANDS")
    print("=" * 70)
    print("⚠️  WARNING: These commands may reset all settings!")
    print("=" * 70)
    
    try:
        async with BleakClient(DEVICE_ADDRESS, timeout=10.0) as client:
            if client.is_connected:
                print("\n✓ Connected!")
                await asyncio.sleep(1.0)
                
                # Factory reset command attempts
                reset_commands = [
                    # Reset command (common pattern)
                    (bytearray([0x06, 0x52, 0x45, 0x53, 0x45, 0x54] + [0] * 10), "RESET"),
                    # Factory reset
                    (bytearray([0x0D, 0x46, 0x41, 0x43, 0x54, 0x4F, 0x52, 0x59, 0x52, 0x45, 0x53, 0x45, 0x54] + [0] * 3), "FACTORYRESET"),
                    # Default settings
                    (bytearray([0x0D, 0x44, 0x45, 0x46, 0x41, 0x55, 0x4C, 0x54, 0x53, 0x45, 0x54, 0x54, 0x49] + [0] * 3), "DEFAULTSETTI"),
                    # Restore defaults
                    (bytearray([0x0E, 0x52, 0x45, 0x53, 0x54, 0x4F, 0x52, 0x45, 0x44, 0x45, 0x46, 0x41, 0x55, 0x4C, 0x54] + [0]), "RESTOREDEFAULT"),
                    # Clear config
                    (bytearray([0x0B, 0x43, 0x4C, 0x45, 0x41, 0x52, 0x43, 0x4F, 0x4E, 0x46, 0x49, 0x47] + [0] * 4), "CLEARCONFIG"),
                    # Init defaults
                    (bytearray([0x0A, 0x49, 0x4E, 0x49, 0x54, 0x44, 0x45, 0x46, 0x41, 0x55, 0x4C, 0x54] + [0] * 4), "INITDEFAULT"),
                    # Reset to 200 LEDs
                    (bytearray([0x0C, 0x52, 0x45, 0x53, 0x45, 0x54, 0x32, 0x30, 0x30, 0x4C, 0x45, 0x44] + [0] * 4), "RESET200LED"),
                ]
                
                print("\nTesting factory reset commands...")
                print("After each command, we'll:")
                print("  1. Set LED count to 200")
                print("  2. Turn device ON")
                print("  3. Set color to test")
                print("  4. Wait for you to check LED count")
                
                for cmd_bytes, desc in reset_commands:
                    print(f"\n{'='*70}")
                    print(f"Testing: {desc}")
                    print(f"Command: {cmd_bytes.hex()}")
                    print(f"{'='*70}")
                    
                    try:
                        # Send reset command
                        encrypted = encrypt_aes_ecb(bytes(cmd_bytes))
                        await client.write_gatt_char(WRITE_CMD_UUID, encrypted, response=False)
                        print("  ✓ Reset command sent")
                        await asyncio.sleep(1)
                        
                        # Set LED count to 200
                        print("  Setting LED count to 200...")
                        count_packet = build_set_lamp_count_packet(200)
                        encrypted_count = encrypt_aes_ecb(count_packet)
                        await client.write_gatt_char(WRITE_CMD_UUID, encrypted_count, response=False)
                        await asyncio.sleep(1)
                        
                        # Turn ON
                        print("  Turning device ON...")
                        on_packet = bytearray.fromhex("05 54 55 52 4E 01 00 00 00 00 00 00 00 00 00 00")
                        encrypted_on = encrypt_aes_ecb(bytes(on_packet))
                        await client.write_gatt_char(WRITE_CMD_UUID, encrypted_on, response=False)
                        await asyncio.sleep(1)
                        
                        # Set color
                        print("  Setting color to WHITE...")
                        color_packet = bytearray.fromhex("0F 53 47 4C 53 00 00 64 50 1F 1F 1F 1F 1F 1F 32")
                        encrypted_color = encrypt_aes_ecb(bytes(color_packet))
                        await client.write_gatt_char(WRITE_CMD_UUID, encrypted_color, response=False)
                        
                        print(f"\n  ✓ Complete - CHECK YOUR STRIP NOW!")
                        print(f"  👀 How many LEDs are lit?")
                        print(f"\n  Waiting 5 seconds before next test...")
                        await asyncio.sleep(5)
                        
                    except Exception as e:
                        print(f"  ✗ Failed: {e}")
                        await asyncio.sleep(1)
                
                print("\n" + "=" * 70)
                print("FACTORY RESET TESTING COMPLETE")
                print("=" * 70)
                print("If none of these worked, firmware update is likely needed.")
                print("See FIRMWARE_UPDATE_GUIDE.md for next steps.")
                
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

