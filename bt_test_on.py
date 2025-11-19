#!/usr/bin/env python3
"""Test different ON commands for the device"""
import asyncio
from bleak import BleakClient

# Device address - UPDATE THIS with your device address
DEVICE_ADDRESS = "F0E047EE-ECB2-EAF3-D11B-1C52E2751387"

# The characteristic that controls power
POWER_CHAR_UUID = "d44bc439-abfd-45a2-b575-92541612960b"
POWER_SERVICE_UUID = "0000fff0-0000-1000-8000-00805f9b34fb"

async def test_on_commands():
    """Test various ON commands on the power characteristic"""
    print("=" * 70)
    print("TESTING ON COMMANDS FOR DEVICE")
    print("=" * 70)
    print(f"Device: {DEVICE_ADDRESS}")
    print(f"Characteristic: {POWER_CHAR_UUID}")
    print(f"Service: {POWER_SERVICE_UUID}")
    print("=" * 70)
    
    # Comprehensive list of ON commands to try
    on_commands = [
        # Single byte
        (b'\x01', "Single byte 0x01"),
        (b'\xFF', "Single byte 0xFF"),
        (b'\xAA', "Single byte 0xAA"),
        (b'\x55', "Single byte 0x55"),
        (b'\x80', "Single byte 0x80"),
        (bytes([1]), "bytes([1])"),
        (bytes([255]), "bytes([255])"),
        
        # Two bytes
        (b'\x01\x00', "Two bytes 0x01 0x00"),
        (b'\x00\x01', "Two bytes 0x00 0x01"),
        (b'\x01\x01', "Two bytes 0x01 0x01"),
        (b'\xFF\x00', "Two bytes 0xFF 0x00"),
        (b'\x00\xFF', "Two bytes 0x00 0xFF"),
        (bytes([1, 0]), "bytes([1, 0])"),
        (bytes([0, 1]), "bytes([0, 1])"),
        (bytes([1, 1]), "bytes([1, 1])"),
        
        # Three bytes
        (b'\x01\x00\x00', "Three bytes 0x01 0x00 0x00"),
        (b'\x00\x00\x01', "Three bytes 0x00 0x00 0x01"),
        (bytes([1, 0, 0]), "bytes([1, 0, 0])"),
        (bytes([0, 0, 1]), "bytes([0, 0, 1])"),
        
        # Four bytes
        (b'\x01\x00\x00\x00', "Four bytes 0x01 0x00 0x00 0x00"),
        (b'\x00\x00\x00\x01', "Four bytes 0x00 0x00 0x00 0x01"),
        (bytes([1, 0, 0, 0]), "bytes([1, 0, 0, 0])"),
        
        # Common LED strip ON commands
        (b'\x7E\x00\x04\xF0\x00\x01\xFF\x00\xEF', "Magic Home format ON"),
        (b'\x31\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00', "Govee format ON"),
    ]
    
    try:
        async with BleakClient(DEVICE_ADDRESS) as client:
            if client.is_connected:
                print("\n✓ Connected successfully!")
                await asyncio.sleep(1.0)
                
                # Try to read current value
                try:
                    current_value = await client.read_gatt_char(POWER_CHAR_UUID)
                    print(f"\nCurrent characteristic value: {current_value.hex()}")
                except Exception as e:
                    print(f"\nCould not read current value: {e}")
                
                print("\n" + "=" * 70)
                print("TESTING ON COMMANDS")
                print("=" * 70)
                print("Watch your device - it should turn ON when the correct command is sent!")
                print("=" * 70)
                
                for cmd_bytes, description in on_commands:
                    try:
                        print(f"\n→ Testing: {description}")
                        print(f"  Command: {cmd_bytes.hex()}")
                        
                        # Try with response first
                        try:
                            await client.write_gatt_char(POWER_CHAR_UUID, cmd_bytes, response=True)
                            print(f"  ✓ Sent (with response)")
                        except:
                            # Try without response
                            try:
                                await client.write_gatt_char(POWER_CHAR_UUID, cmd_bytes, response=False)
                                print(f"  ✓ Sent (without response)")
                            except Exception as e:
                                print(f"  ✗ Failed: {e}")
                                continue
                        
                        # Wait and check if device turned on
                        print(f"  👀 WATCH YOUR DEVICE - Did it turn ON?")
                        await asyncio.sleep(2)
                        
                        # Try to read value after write
                        try:
                            new_value = await client.read_gatt_char(POWER_CHAR_UUID)
                            print(f"  Value after write: {new_value.hex()}")
                        except:
                            pass
                        
                    except Exception as e:
                        print(f"  ✗ Error: {e}")
                
                print("\n" + "=" * 70)
                print("TESTING COMPLETE")
                print("=" * 70)
                print("If none of the commands turned the device ON, try:")
                print("1. Power cycle the device (turn off and on)")
                print("2. Check if device needs a specific initialization sequence")
                print("3. Try reading the characteristic when device is ON vs OFF")
                print("4. The ON command might require multiple writes")
                
            else:
                print("✗ Failed to connect")
    except Exception as e:
        print(f"✗ Connection failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_on_commands())

