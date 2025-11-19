#!/usr/bin/env python3
"""Set all LEDs to a single color to test the working range

Usage:
    python3 bt_set_all_color.py [r] [g] [b]
    
Examples:
    python3 bt_set_all_color.py 255 0 0    # All RED
    python3 bt_set_all_color.py 0 255 0    # All GREEN  
    python3 bt_set_all_color.py 0 0 255    # All BLUE
    python3 bt_set_all_color.py 255 255 255 # All WHITE
"""
import asyncio
import sys
from bleak import BleakClient
from Crypto.Cipher import AES

# Device address
DEVICE_ADDRESS = "F0E047EE-ECB2-EAF3-D11B-1C52E2751387"

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

def build_set_color_packet(r, g, b):
    """
    Build packet to set entire strip to a single color
    Format: 0F 53 47 4C 53 00 00 64 50 [r] [g] [b] [r] [g] [b] 32
    Uses 5-bit color (shifted right 3 bits) to save power
    """
    packet = bytearray.fromhex("0F 53 47 4C 53 00 00 64 50 1F 00 00 1F 00 00 32")
    
    # Convert to 5-bit color (shift right 3 bits) to avoid overloading power regulator
    r_5bit = (r >> 3) & 0x1F
    g_5bit = (g >> 3) & 0x1F
    b_5bit = (b >> 3) & 0x1F
    
    # Set color (duplicated in packet)
    packet[9] = r_5bit
    packet[12] = r_5bit
    packet[10] = g_5bit
    packet[13] = g_5bit
    packet[11] = b_5bit
    packet[14] = b_5bit
    
    return bytes(packet)

async def set_all_color(r, g, b):
    """Set all LEDs to a single color"""
    print(f"Setting all LEDs to RGB({r}, {g}, {b})...")
    print(f"Connecting to device: {DEVICE_ADDRESS}")
    
    try:
        async with BleakClient(DEVICE_ADDRESS, timeout=10.0) as client:
            if client.is_connected:
                print(f"✓ Connected!")
                await asyncio.sleep(1.0)
                
                # Turn device ON first
                print("Turning device ON...")
                on_packet = bytearray.fromhex("05 54 55 52 4E 01 00 00 00 00 00 00 00 00 00 00")
                on_packet[5] = 1
                encrypted_on = encrypt_aes_ecb(bytes(on_packet))
                await client.write_gatt_char(WRITE_CMD_UUID, encrypted_on, response=False)
                await asyncio.sleep(1)
                
                # Set color
                print(f"Setting color to RGB({r}, {g}, {b})...")
                packet = build_set_color_packet(r, g, b)
                encrypted = encrypt_aes_ecb(packet)
                
                print(f"Plain packet: {packet.hex()}")
                print(f"Encrypted: {encrypted.hex()}")
                
                await client.write_gatt_char(WRITE_CMD_UUID, encrypted, response=False)
                print(f"\n✓ Color set!")
                print(f"\nObserve your LED strip:")
                print(f"  - Count how many LEDs are lit")
                print(f"  - Note if LEDs beyond ~70 are working")
                print(f"  - This will help determine the actual working range")
                
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
    """Main function"""
    if len(sys.argv) >= 4:
        r = int(sys.argv[1])
        g = int(sys.argv[2])
        b = int(sys.argv[3])
    else:
        # Default: bright white to see all LEDs
        r, g, b = 255, 255, 255
    
    await set_all_color(r, g, b)

if __name__ == "__main__":
    asyncio.run(main())

