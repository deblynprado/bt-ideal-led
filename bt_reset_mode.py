#!/usr/bin/env python3
"""Try to reset mode configuration that might be limiting LEDs

The app's "parallel" vs "continuous" mode might be stored in byte 5 of the
set_color packet (modelIndex). This script tries different values to reset it.
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

def build_set_color_with_mode(r, g, b, model_index=0, reverse=0, speed=50, saturation=50):
    """
    Build set_color packet with mode configuration
    Format: 0F 53 47 4C 53 [modelIndex] [reverse] [speed] [r] [g] [b] [r] [g] [b] [saturation]
    Byte 5: modelIndex (might control parallel/continuous mode)
    Byte 6: reverse flag (1 ^ z)
    """
    packet = bytearray.fromhex("0F 53 47 4C 53 00 00 64 50 1F 00 00 1F 00 00 32")
    
    # Set mode parameters
    packet[5] = model_index & 0xFF  # Model index (might be mode)
    packet[6] = reverse & 0xFF     # Reverse flag
    packet[7] = speed & 0xFF         # Speed
    packet[8] = saturation & 0xFF    # Saturation
    
    # Set color (5-bit, duplicated)
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

async def try_reset_modes():
    """Try different mode configurations to reset parallel/continuous mode"""
    print("=" * 70)
    print("ATTEMPTING TO RESET MODE CONFIGURATION")
    print("=" * 70)
    print("Trying different modelIndex values that might reset mode")
    print("=" * 70)
    
    try:
        async with BleakClient(DEVICE_ADDRESS, timeout=10.0) as client:
            if client.is_connected:
                print("\n✓ Connected!")
                await asyncio.sleep(1.0)
                
                # Turn device ON first
                print("\nTurning device ON...")
                on_packet = build_on_off_packet(True)
                encrypted_on = encrypt_aes_ecb(on_packet)
                await client.write_gatt_char(WRITE_CMD_UUID, encrypted_on, response=False)
                await asyncio.sleep(1)
                
                # Focus on modelIndex = 0 (likely continuous/default mode)
                # Skip modelIndex = 10 since it turns the strip off
                print("\n" + "=" * 70)
                print("FOCUSED RESET: Setting modelIndex = 0 (Continuous Mode)")
                print("=" * 70)
                print("modelIndex = 0 is likely the default/continuous mode")
                print("We'll set this multiple times with LED count = 200")
                print("=" * 70)
                
                # First, ensure device is ON
                print("\nStep 1: Ensuring device is ON...")
                on_packet = build_on_off_packet(True)
                encrypted_on = encrypt_aes_ecb(on_packet)
                await client.write_gatt_char(WRITE_CMD_UUID, encrypted_on, response=False)
                await asyncio.sleep(1)
                
                # Set modelIndex = 0 multiple times (this might reset the mode)
                print("\nStep 2: Setting modelIndex = 0 (Continuous Mode)...")
                for i in range(3):
                    color_packet = build_set_color_with_mode(255, 255, 255, model_index=0, reverse=0)
                    encrypted_color = encrypt_aes_ecb(color_packet)
                    await client.write_gatt_char(WRITE_CMD_UUID, encrypted_color, response=False)
                    print(f"  Attempt {i+1}/3: Set modelIndex=0")
                    await asyncio.sleep(0.5)
                
                # Set LED count to 200 multiple times
                print("\nStep 3: Setting LED count to 200 (multiple times)...")
                for i in range(5):
                    count_packet = build_set_lamp_count_packet(200)
                    encrypted_count = encrypt_aes_ecb(count_packet)
                    await client.write_gatt_char(WRITE_CMD_UUID, encrypted_count, response=False)
                    print(f"  Attempt {i+1}/5: Set count=200")
                    await asyncio.sleep(0.5)
                
                # Ensure device stays ON
                print("\nStep 4: Ensuring device stays ON...")
                await client.write_gatt_char(WRITE_CMD_UUID, encrypted_on, response=False)
                await asyncio.sleep(1)
                
                # Set color with modelIndex = 0 again
                print("\nStep 5: Setting all LEDs to WHITE with modelIndex=0...")
                color_packet = build_set_color_with_mode(255, 255, 255, model_index=0, reverse=0)
                encrypted_color = encrypt_aes_ecb(color_packet)
                await client.write_gatt_char(WRITE_CMD_UUID, encrypted_color, response=False)
                await asyncio.sleep(2)
                
                print("\n" + "=" * 70)
                print("RESET COMPLETE")
                print("=" * 70)
                print("Check your LED strip:")
                print("  - Count how many LEDs are lit")
                print("  - If still only ~70, we'll try other modelIndex values")
                print("=" * 70)
                
                # Now try a few other modelIndex values systematically
                print("\n" + "=" * 70)
                print("TESTING OTHER MODEL INDEX VALUES")
                print("=" * 70)
                print("Testing modelIndex values that might enable all LEDs")
                print("(Skipping modelIndex=10 since it turns strip off)")
                print("=" * 70)
                
                # Try values that work (skip 9 and 10 since they cause issues)
                # Focus on 0-8 which seem to work
                model_indices_to_try = [0, 1, 2, 3, 4, 5, 6, 7, 8]
                
                print("Testing modelIndex values 0-8 (skipping 9 and 10)")
                print("Watch your strip carefully - note which value enables the most LEDs!")
                
                for model_idx in model_indices_to_try:
                    print(f"\n{'='*70}")
                    print(f"Testing modelIndex = {model_idx}")
                    print(f"{'='*70}")
                    
                    # Ensure ON first
                    print("  Turning ON...")
                    await client.write_gatt_char(WRITE_CMD_UUID, encrypted_on, response=False)
                    await asyncio.sleep(0.5)
                    
                    # Set LED count to 200
                    print("  Setting LED count to 200...")
                    count_packet = build_set_lamp_count_packet(200)
                    encrypted_count = encrypt_aes_ecb(count_packet)
                    await client.write_gatt_char(WRITE_CMD_UUID, encrypted_count, response=False)
                    await asyncio.sleep(0.5)
                    
                    # Set color with this modelIndex (BRIGHT WHITE for visibility)
                    print(f"  Setting color with modelIndex={model_idx}...")
                    color_packet = build_set_color_with_mode(255, 255, 255, model_index=model_idx, reverse=0)
                    encrypted_color = encrypt_aes_ecb(color_packet)
                    await client.write_gatt_char(WRITE_CMD_UUID, encrypted_color, response=False)
                    print(f"  ✓ Complete - COUNT HOW MANY LEDs ARE LIT!")
                    print(f"     👀 Watch your strip now!")
                    await asyncio.sleep(4)  # Longer pause to observe
                
                # Try setting LED count with different values in sequence
                print("\n" + "=" * 70)
                print("FINAL ATTEMPT: Sequential Count Reset")
                print("=" * 70)
                print("Setting count to: 70 -> 100 -> 150 -> 200")
                
                for count in [70, 100, 150, 200]:
                    count_packet = build_set_lamp_count_packet(count)
                    encrypted_count = encrypt_aes_ecb(count_packet)
                    await client.write_gatt_char(WRITE_CMD_UUID, encrypted_count, response=False)
                    print(f"  Set to {count} LEDs")
                    await asyncio.sleep(1)
                
                # Final color test
                color_packet = build_set_color_with_mode(255, 255, 255, model_index=0, reverse=0)
                encrypted_color = encrypt_aes_ecb(color_packet)
                await client.write_gatt_char(WRITE_CMD_UUID, encrypted_color, response=False)
                await asyncio.sleep(2)
                
                print("\n" + "=" * 70)
                print("RESET ATTEMPTS COMPLETE")
                print("=" * 70)
                print("If LEDs beyond 70 still don't work:")
                print("  1. The configuration might be stored in non-volatile memory")
                print("  2. You may need to use the app to change mode back")
                print("  3. Try unplugging power for 30+ seconds (not just 10)")
                print("  4. The controller firmware might have a bug")
                print("  5. Contact the manufacturer or check for firmware update")
                
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
    await try_reset_modes()

if __name__ == "__main__":
    asyncio.run(main())

