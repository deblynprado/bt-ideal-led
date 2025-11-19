#!/usr/bin/env python3
"""Simple ON/OFF control for iDeal LED lights

Usage:
    python3 bt_led_control.py on    # Turn device ON
    python3 bt_led_control.py off   # Turn device OFF
"""
import asyncio
import sys
from bleak import BleakClient
from Crypto.Cipher import AES

# Device address - UPDATE THIS with your device UUID
DEVICE_ADDRESS = "F0E047EE-ECB2-EAF3-D11B-1C52E2751387"

# Protocol constants from https://github.com/8none1/idealLED
SERVICE_UUID = "0000fff0-0000-1000-8000-00805f9b34fb"
WRITE_CMD_UUID = "d44bc439-abfd-45a2-b575-925416129600"  # The correct one that works!

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
    """
    Build LED count configuration packet
    
    Format: 09 4C 41 4D 50 4E 00 [high] [low] [high] [low] 00 00 00 00 00 00
            LED count encoded as big-endian 16-bit, duplicated
    """
    packet = bytearray.fromhex("09 4C 41 4D 50 4E 00 32 00 32 00 00 00 00 00 00")
    high = (count >> 8) & 0xFF
    low = count & 0xFF
    packet[6] = high
    packet[7] = low
    packet[8] = high
    packet[9] = low
    return bytes(packet)

async def control_led(state):
    """Turn LED strip ON or OFF"""
    state_str = "ON" if state else "OFF"
    print(f"Connecting to device: {DEVICE_ADDRESS}")
    print("Make sure the device is:")
    print("  - Powered ON")
    print("  - Within Bluetooth range")
    print("  - Not connected to another device")
    
    try:
        # Increase timeout to 10 seconds
        async with BleakClient(DEVICE_ADDRESS, timeout=10.0) as client:
            print("  Connecting...")
            if client.is_connected:
                print(f"✓ Connected!")
                await asyncio.sleep(1.0)  # Wait for services to be ready
                
                # Build and encrypt the command
                packet = build_on_off_packet(state)
                encrypted = encrypt_aes_ecb(packet)
                
                print(f"Sending {state_str} command...")
                print(f"  Plain packet: {packet.hex()}")
                print(f"  Encrypted: {encrypted.hex()}")
                
                # Send the command - device responds with 3 blinks then executes
                success = False
                
                # Try with response first
                try:
                    await client.write_gatt_char(WRITE_CMD_UUID, encrypted, response=True)
                    print(f"✓ Sent with response")
                    success = True
                except Exception as e1:
                    # Fall back to without response
                    try:
                        await client.write_gatt_char(WRITE_CMD_UUID, encrypted, response=False)
                        print(f"✓ Sent without response")
                        success = True
                    except Exception as e2:
                        print(f"✗ Failed to send: {e2}")
                        return False
                
                if not success:
                    return False
                
                print(f"✓ Command sent! Device will blink 3 times, then {state_str.lower()}...")
                print(f"  (This is normal - the device acknowledges commands with blinking)")
                return True
            else:
                print("✗ Failed to connect - device not responding")
                return False
    except asyncio.TimeoutError:
        print("\n✗ Connection timeout!")
        print("\nTroubleshooting:")
        print("  1. Make sure the device is powered ON")
        print("  2. Move the device closer to your computer")
        print("  3. Check if device is connected to another device (phone, etc.)")
        print("  4. Try power cycling the device (turn off and on)")
        print("  5. Run discovery to verify device is visible:")
        print("     python3 bt_discover.py")
        return False
    except Exception as e:
        print(f"\n✗ Error: {e}")
        print("\nTroubleshooting:")
        print("  1. Verify device UUID is correct")
        print("  2. Make sure device is powered ON and in range")
        print("  3. Try running discovery: python3 bt_discover.py")
        return False

async def set_led_count(count):
    """Set the LED count on the device"""
    if count < 1 or count > 1000:
        print(f"Error: LED count must be between 1 and 1000 (got {count})")
        return False
    
    print(f"Setting LED count to {count}...")
    print(f"Connecting to device: {DEVICE_ADDRESS}")
    
    try:
        async with BleakClient(DEVICE_ADDRESS, timeout=10.0) as client:
            if client.is_connected:
                print(f"✓ Connected!")
                await asyncio.sleep(1.0)
                
                # Build the LED count packet
                packet = build_set_lamp_count_packet(count)
                encrypted = encrypt_aes_ecb(packet)
                
                print(f"Sending LED count command...")
                print(f"  Plain packet: {packet.hex()}")
                print(f"  Encrypted: {encrypted.hex()}")
                
                # Send command
                try:
                    await client.write_gatt_char(WRITE_CMD_UUID, encrypted, response=True)
                    print(f"✓ Sent with response")
                except:
                    await client.write_gatt_char(WRITE_CMD_UUID, encrypted, response=False)
                    print(f"✓ Sent without response")
                
                print(f"\n✓ LED count set to {count}!")
                print(f"  Device will blink 3 times to acknowledge")
                print(f"  All {count} LEDs should now be active")
                return True
            else:
                print("✗ Failed to connect")
                return False
    except asyncio.TimeoutError:
        print("\n✗ Connection timeout!")
        print("Make sure device is powered ON and within range")
        return False
    except Exception as e:
        print(f"\n✗ Error: {e}")
        return False

async def main():
    """Main function"""
    if len(sys.argv) < 2:
        print("Usage: python3 bt_led_control.py [on|off|count <number>]")
        print("\nExamples:")
        print("  python3 bt_led_control.py on")
        print("  python3 bt_led_control.py off")
        print("  python3 bt_led_control.py count 200    # Set LED count to 200")
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    if command == "on":
        await control_led(True)
    elif command == "off":
        await control_led(False)
    elif command == "count":
        if len(sys.argv) < 3:
            print("Error: count command requires a number")
            print("Usage: python3 bt_led_control.py count <number>")
            print("Example: python3 bt_led_control.py count 200")
            sys.exit(1)
        try:
            count = int(sys.argv[2])
            await set_led_count(count)
        except ValueError:
            print(f"Error: '{sys.argv[2]}' is not a valid number")
            sys.exit(1)
    else:
        print(f"Error: Unknown command '{command}'")
        print("Use 'on', 'off', or 'count <number>'")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())

