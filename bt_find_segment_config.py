#!/usr/bin/env python3
"""Find segment/channel configuration that might be limiting LEDs

Since modelIndex doesn't help, there might be a separate segment/channel
configuration command that limits the active LEDs.
"""
import asyncio
from bleak import BleakClient
from Crypto.Cipher import AES

# Device address
DEVICE_ADDRESS = "F0E047EE-ECB2-EAF3-D11B-1C52E2751387"

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

async def test_all_writeable_characteristics():
    """Test all writeable characteristics with different commands"""
    print("=" * 70)
    print("TESTING ALL WRITEABLE CHARACTERISTICS")
    print("=" * 70)
    print("Looking for segment/channel configuration commands")
    print("=" * 70)
    
    try:
        async with BleakClient(DEVICE_ADDRESS, timeout=10.0) as client:
            if client.is_connected:
                print("\n✓ Connected!")
                await asyncio.sleep(1.0)
                
                # Get all services and characteristics
                services = client.services
                services_list = list(services)
                
                print(f"\nFound {len(services_list)} service(s)")
                
                # Find all writeable characteristics
                writeable_chars = []
                for service in services_list:
                    for char in service.characteristics:
                        if "write" in char.properties or "write-without-response" in char.properties:
                            writeable_chars.append((service.uuid, char))
                
                print(f"\nFound {len(writeable_chars)} writeable characteristic(s)")
                
                # Show all writeable characteristics
                print("\n" + "=" * 70)
                print("ALL WRITEABLE CHARACTERISTICS:")
                print("=" * 70)
                for i, (service_uuid, char) in enumerate(writeable_chars, 1):
                    props = []
                    if "write" in char.properties:
                        props.append("WRITE")
                    if "write-without-response" in char.properties:
                        props.append("WRITE_NO_RESPONSE")
                    print(f"{i}. {char.uuid}")
                    print(f"   Service: {service_uuid}")
                    print(f"   Properties: {', '.join(props)}")
                
                # Turn device ON first
                print("\n" + "=" * 70)
                print("STEP 1: Turn device ON and set LED count to 200")
                print("=" * 70)
                on_packet = build_on_off_packet(True)
                encrypted_on = encrypt_aes_ecb(on_packet)
                await client.write_gatt_char(WRITE_CMD_UUID, encrypted_on, response=False)
                await asyncio.sleep(1)
                
                count_packet = build_set_lamp_count_packet(200)
                encrypted_count = encrypt_aes_ecb(count_packet)
                await client.write_gatt_char(WRITE_CMD_UUID, encrypted_count, response=False)
                await asyncio.sleep(1)
                
                # Try potential segment/channel commands on each writeable characteristic
                print("\n" + "=" * 70)
                print("STEP 2: Testing potential segment/channel commands")
                print("=" * 70)
                print("Trying commands that might reset segment limits...")
                print("=" * 70)
                
                # Potential segment/channel reset commands
                # These are educated guesses based on common patterns
                test_commands = [
                    # Try setting segment count to 1 (continuous mode)
                    (bytearray.fromhex("08 53 45 47 4D 45 4E 54 01 00 00 00 00 00 00 00"), "Segment count = 1"),
                    # Try setting channel count to 200
                    (bytearray.fromhex("08 43 48 41 4E 4E 45 4C C8 00 00 00 00 00 00 00"), "Channel count = 200"),
                    # Try continuous mode command
                    (bytearray.fromhex("09 43 4F 4E 54 49 4E 55 4F 55 53 01 00 00 00 00"), "Continuous mode"),
                    # Try reset segment
                    (bytearray.fromhex("0A 52 45 53 45 54 53 45 47 4D 45 4E 54 00 00 00"), "Reset segment"),
                    # Try max LEDs = 200
                    (bytearray.fromhex("08 4D 41 58 4C 45 44 53 C8 00 00 00 00 00 00 00"), "Max LEDs = 200"),
                ]
                
                for service_uuid, char in writeable_chars:
                    print(f"\nTesting characteristic: {char.uuid}")
                    print(f"Service: {service_uuid}")
                    
                    for cmd_bytes, description in test_commands:
                        try:
                            encrypted = encrypt_aes_ecb(bytes(cmd_bytes))
                            await client.write_gatt_char(char.uuid, encrypted, response=False)
                            print(f"  ✓ Sent: {description}")
                            await asyncio.sleep(0.5)
                        except Exception as e:
                            print(f"  ✗ Failed {description}: {str(e)[:50]}")
                    
                    # After testing commands, set color to see if anything changed
                    print(f"  Setting color to test...")
                    color_packet = bytearray.fromhex("0F 53 47 4C 53 00 00 64 50 1F 1F 1F 1F 1F 1F 32")
                    encrypted_color = encrypt_aes_ecb(bytes(color_packet))
                    try:
                        await client.write_gatt_char(WRITE_CMD_UUID, encrypted_color, response=False)
                        print(f"  ✓ Color set - Check your strip!")
                        await asyncio.sleep(2)
                    except:
                        pass
                
                print("\n" + "=" * 70)
                print("TESTING COMPLETE")
                print("=" * 70)
                print("If none of these worked, the configuration might be:")
                print("  1. Stored in non-volatile memory that requires a specific reset")
                print("  2. Controlled by a command we haven't discovered yet")
                print("  3. Limited by firmware that can't be changed via BLE")
                print("\nNext steps:")
                print("  - Check if controller has a physical reset button")
                print("  - Try unplugging power for 30+ minutes")
                print("  - Contact manufacturer for reset procedure")
                
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
    asyncio.run(test_all_writeable_characteristics())

