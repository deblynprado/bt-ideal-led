#!/usr/bin/env python3
"""Control iDeal LED lights using the reverse-engineered protocol

Based on: https://github.com/8none1/idealLED

Installation:
    pip3 install pycryptodome bleak

Usage:
    python3 bt_ideal_led.py
"""
import asyncio
import sys

try:
    from bleak import BleakClient
except ImportError:
    print("Error: bleak library not found. Install with: pip3 install bleak")
    sys.exit(1)

try:
    from Crypto.Cipher import AES
except ImportError:
    print("Error: pycryptodome library not found. Install with: pip3 install pycryptodome")
    print("\nAlternatively, you can use cryptography library:")
    print("  pip3 install cryptography")
    print("  (The script will need to be modified to use cryptography instead)")
    sys.exit(1)

# Device address - UPDATE THIS with your device UUID
DEVICE_ADDRESS = "F0E047EE-ECB2-EAF3-D11B-1C52E2751387"

# Protocol constants from https://github.com/8none1/idealLED
SERVICE_UUID = "0000fff0-0000-1000-8000-00805f9b34fb"
WRITE_CMD_UUID = "d44bc439-abfd-45a2-b575-925416129600"  # For commands
# Also try these variants if the above doesn't work:
WRITE_CMD_UUID_VARIANTS = [
    "d44bc439-abfd-45a2-b575-925416129600",  # Original from repo
    "d44bc439-abfd-45a2-b575-92541612960b",  # What we found (ends in 0b)
    "d44bc439-abfd-45a2-b575-92541612960a",  # For color data
]

# AES encryption key extracted from the Android app
SECRET_ENCRYPTION_KEY = bytes([0x34, 0x52, 0x2A, 0x5B, 0x7A, 0x6E, 0x49, 0x2C, 
                                0x08, 0x09, 0x0A, 0x9D, 0x8D, 0x2A, 0x23, 0xF8])

def encrypt_aes_ecb(plaintext):
    """Encrypt packet using AES ECB mode"""
    # Pad to 16 bytes if needed
    if len(plaintext) < 16:
        plaintext = plaintext + bytes(16 - len(plaintext))
    elif len(plaintext) > 16:
        plaintext = plaintext[:16]
    
    cipher = AES.new(SECRET_ENCRYPTION_KEY, AES.MODE_ECB)
    ciphertext = cipher.encrypt(plaintext)
    return ciphertext

def build_on_off_packet(state):
    """
    Build ON/OFF command packet
    Format: 05 54 55 52 4E 01 00 00 00 00 00 00 00 00 00 00
            Byte 5: 1 for ON, 0 for OFF
    """
    packet = bytearray.fromhex("05 54 55 52 4E 01 00 00 00 00 00 00 00 00 00 00")
    packet[5] = 1 if state else 0
    return bytes(packet)

async def turn_on_off(client, state, char_uuid):
    """Turn device ON or OFF"""
    try:
        # Build the command packet
        packet = build_on_off_packet(state)
        print(f"Plain packet: {packet.hex()}")
        
        # Encrypt the packet
        encrypted = encrypt_aes_ecb(packet)
        print(f"Encrypted packet: {encrypted.hex()}")
        
        # Write to characteristic
        await client.write_gatt_char(char_uuid, encrypted, response=False)
        print(f"✓ Sent {'ON' if state else 'OFF'} command")
        return True
    except Exception as e:
        print(f"✗ Failed to send command: {e}")
        return False

async def test_all_characteristics():
    """Test ON/OFF on all possible characteristic UUIDs"""
    print("=" * 70)
    print("TESTING iDeal LED PROTOCOL")
    print("=" * 70)
    print(f"Device: {DEVICE_ADDRESS}")
    print(f"Service: {SERVICE_UUID}")
    print("=" * 70)
    
    try:
        async with BleakClient(DEVICE_ADDRESS) as client:
            if client.is_connected:
                print("\n✓ Connected successfully!")
                await asyncio.sleep(1.0)
                
                # Discover services
                services = client.services
                services_list = list(services)
                print(f"\nFound {len(services_list)} service(s)")
                
                # Find writeable characteristics in the target service
                target_chars = []
                for service in services_list:
                    if str(service.uuid).lower() == SERVICE_UUID.lower():
                        print(f"\n✓ Found target service: {service.uuid}")
                        for char in service.characteristics:
                            if "write" in char.properties or "write-without-response" in char.properties:
                                target_chars.append(char)
                                print(f"  Writeable characteristic: {char.uuid}")
                
                if not target_chars:
                    print("\n⚠ No writeable characteristics found in target service")
                    print("Trying known UUIDs...")
                    target_chars = [None] * len(WRITE_CMD_UUID_VARIANTS)
                
                # Test each characteristic UUID
                char_uuids_to_test = []
                for char in target_chars:
                    if char:
                        char_uuids_to_test.append(char.uuid)
                
                # Also try known UUIDs
                for uuid in WRITE_CMD_UUID_VARIANTS:
                    if uuid not in char_uuids_to_test:
                        char_uuids_to_test.append(uuid)
                
                print(f"\n{'='*70}")
                print("TESTING ON/OFF COMMANDS")
                print(f"{'='*70}")
                print("Testing with AES-encrypted packets on each characteristic...")
                
                for char_uuid in char_uuids_to_test:
                    print(f"\n{'='*70}")
                    print(f"Testing characteristic: {char_uuid}")
                    print(f"{'='*70}")
                    
                    # Try OFF first (device might already be on)
                    print("\n🔴 Testing OFF command...")
                    await turn_on_off(client, False, char_uuid)
                    await asyncio.sleep(2)
                    print("  👀 Did the device turn OFF?")
                    
                    # Try ON
                    print("\n🟢 Testing ON command...")
                    await turn_on_off(client, True, char_uuid)
                    await asyncio.sleep(2)
                    print("  👀 Did the device turn ON?")
                    
                    print("\n⏸️  Waiting 3 seconds before next test...")
                    await asyncio.sleep(3)
                
                print("\n" + "=" * 70)
                print("TESTING COMPLETE")
                print("=" * 70)
                print("If the device responded, note which characteristic UUID worked!")
                
            else:
                print("✗ Failed to connect")
    except Exception as e:
        print(f"✗ Connection failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_all_characteristics())

