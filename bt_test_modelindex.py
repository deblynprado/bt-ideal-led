#!/usr/bin/env python3
"""Test modelIndex values 0-8 to find which enables all 200 LEDs

This script tests only the working modelIndex values (0-8) and helps
identify which one restores full LED functionality.
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

def build_set_color_with_mode(r, g, b, model_index=0, reverse=0, speed=50, saturation=50):
    """Build set_color packet with mode configuration"""
    packet = bytearray.fromhex("0F 53 47 4C 53 00 00 64 50 1F 00 00 1F 00 00 32")
    packet[5] = model_index & 0xFF
    packet[6] = reverse & 0xFF
    packet[7] = speed & 0xFF
    packet[8] = saturation & 0xFF
    
    r_5bit = (r >> 3) & 0x1F
    g_5bit = (g >> 3) & 0x1F
    b_5bit = (b >> 3) & 0x1F
    
    packet[9] = r_5bit
    packet[12] = r_5bit
    packet[10] = g_5bit
    packet[13] = g_5bit
    packet[11] = b_5bit
    packet[14] = b_5bit
    
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

def build_on_off_packet(state):
    """Build ON/OFF command packet"""
    packet = bytearray.fromhex("05 54 55 52 4E 01 00 00 00 00 00 00 00 00 00 00")
    packet[5] = 1 if state else 0
    return bytes(packet)

async def test_modelindex():
    """Test modelIndex values 0-8 to find the one that enables all LEDs"""
    print("=" * 70)
    print("TESTING MODELINDEX VALUES 0-8")
    print("=" * 70)
    print("This will test each modelIndex value with LED count = 200")
    print("Watch your strip and note which value enables the MOST LEDs!")
    print("=" * 70)
    
    try:
        async with BleakClient(DEVICE_ADDRESS, timeout=10.0) as client:
            if client.is_connected:
                print("\n✓ Connected!")
                await asyncio.sleep(1.0)
                
                # Prepare ON packet
                on_packet = build_on_off_packet(True)
                encrypted_on = encrypt_aes_ecb(on_packet)
                
                # Test each modelIndex value
                for model_idx in range(9):  # 0-8
                    print(f"\n{'='*70}")
                    print(f"TESTING modelIndex = {model_idx}")
                    print(f"{'='*70}")
                    
                    # Step 1: Turn ON
                    print("  1. Turning device ON...")
                    await client.write_gatt_char(WRITE_CMD_UUID, encrypted_on, response=False)
                    await asyncio.sleep(0.5)
                    
                    # Step 2: Set LED count to 200
                    print("  2. Setting LED count to 200...")
                    count_packet = build_set_lamp_count_packet(200)
                    encrypted_count = encrypt_aes_ecb(count_packet)
                    await client.write_gatt_char(WRITE_CMD_UUID, encrypted_count, response=False)
                    await asyncio.sleep(0.5)
                    
                    # Step 3: Set color with this modelIndex
                    print(f"  3. Setting color with modelIndex={model_idx}...")
                    color_packet = build_set_color_with_mode(255, 255, 255, model_index=model_idx, reverse=0)
                    encrypted_color = encrypt_aes_ecb(color_packet)
                    await client.write_gatt_char(WRITE_CMD_UUID, encrypted_color, response=False)
                    
                    print(f"\n  ✓ Test complete for modelIndex={model_idx}")
                    print(f"  👀 COUNT THE LEDs ON YOUR STRIP RIGHT NOW!")
                    print(f"  📝 How many LEDs are lit? (Write it down)")
                    print(f"\n  Waiting 5 seconds before next test...")
                    await asyncio.sleep(5)
                
                print("\n" + "=" * 70)
                print("TESTING COMPLETE")
                print("=" * 70)
                print("Review your notes:")
                print("  - Which modelIndex value enabled the MOST LEDs?")
                print("  - Did any modelIndex enable all 200 LEDs?")
                print("\nOnce you identify the working modelIndex, we can create")
                print("a script that sets it permanently.")
                
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
    asyncio.run(test_modelindex())

