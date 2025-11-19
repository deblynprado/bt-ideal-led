#!/usr/bin/env python3
"""Read the power characteristic value when device is ON vs OFF"""
import asyncio
from bleak import BleakClient

# Device address - UPDATE THIS
DEVICE_ADDRESS = "F0E047EE-ECB2-EAF3-D11B-1C52E2751387"

# The characteristic that controls power
POWER_CHAR_UUID = "d44bc439-abfd-45a2-b575-92541612960b"

async def read_state():
    """Read the characteristic value in different states"""
    print("=" * 70)
    print("READING DEVICE STATE")
    print("=" * 70)
    print(f"Device: {DEVICE_ADDRESS}")
    print(f"Characteristic: {POWER_CHAR_UUID}")
    print("=" * 70)
    
    try:
        async with BleakClient(DEVICE_ADDRESS) as client:
            if client.is_connected:
                print("\n✓ Connected successfully!")
                await asyncio.sleep(1.0)
                
                print("\n" + "=" * 70)
                print("STEP 1: Read value when device is OFF")
                print("=" * 70)
                print("Make sure your device is OFF, then press Enter...")
                input()
                
                try:
                    value_off = await client.read_gatt_char(POWER_CHAR_UUID)
                    print(f"Value when OFF: {value_off.hex()}")
                    print(f"  As bytes: {list(value_off)}")
                    print(f"  Length: {len(value_off)} bytes")
                    
                    # Interpret as numbers
                    if len(value_off) == 1:
                        print(f"  As uint8: {value_off[0]}")
                    elif len(value_off) == 2:
                        le = int.from_bytes(value_off, 'little')
                        be = int.from_bytes(value_off, 'big')
                        print(f"  As uint16 LE: {le}, BE: {be}")
                    elif len(value_off) >= 4:
                        le = int.from_bytes(value_off[:4], 'little')
                        be = int.from_bytes(value_off[:4], 'big')
                        print(f"  As uint32 LE: {le}, BE: {be}")
                        
                except Exception as e:
                    print(f"✗ Could not read: {e}")
                    value_off = None
                
                print("\n" + "=" * 70)
                print("STEP 2: Turn device ON manually")
                print("=" * 70)
                print("Turn your device ON using its physical button/switch")
                print("Then press Enter to read the value when ON...")
                input()
                
                try:
                    value_on = await client.read_gatt_char(POWER_CHAR_UUID)
                    print(f"Value when ON: {value_on.hex()}")
                    print(f"  As bytes: {list(value_on)}")
                    print(f"  Length: {len(value_on)} bytes")
                    
                    # Interpret as numbers
                    if len(value_on) == 1:
                        print(f"  As uint8: {value_on[0]}")
                    elif len(value_on) == 2:
                        le = int.from_bytes(value_on, 'little')
                        be = int.from_bytes(value_on, 'big')
                        print(f"  As uint16 LE: {le}, BE: {be}")
                    elif len(value_on) >= 4:
                        le = int.from_bytes(value_on[:4], 'little')
                        be = int.from_bytes(value_on[:4], 'big')
                        print(f"  As uint32 LE: {le}, BE: {be}")
                        
                except Exception as e:
                    print(f"✗ Could not read: {e}")
                    value_on = None
                
                # Compare values
                if value_off and value_on:
                    print("\n" + "=" * 70)
                    print("COMPARISON")
                    print("=" * 70)
                    print(f"OFF: {value_off.hex()}")
                    print(f"ON:  {value_on.hex()}")
                    
                    if value_off != value_on:
                        print("\n✓ Values are different!")
                        print("The ON command should be the value shown when device is ON")
                        print(f"Try writing: {value_on.hex()}")
                    else:
                        print("\n⚠ Values are the same - characteristic might not reflect state")
                
            else:
                print("✗ Failed to connect")
    except Exception as e:
        print(f"✗ Connection failed: {e}")

if __name__ == "__main__":
    asyncio.run(read_state())

