#!/usr/bin/env python3
"""Read device configuration to see what LED count is actually set

Since setting LED count doesn't change behavior, let's try to READ
the actual configuration from the device.
"""
import asyncio
from bleak import BleakClient
from Crypto.Cipher import AES

# Device address
DEVICE_ADDRESS = "7D99DED2-7D11-3D98-32A9-11223B359DA0"

# Protocol constants
SERVICE_UUID = "0000fff0-0000-1000-8000-00805f9b34fb"
WRITE_CMD_UUID = "d44bc439-abfd-45a2-b575-925416129600"
NOTIFICATION_UUID = "d44bc439-abfd-45a2-b575-925416129601"

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

notifications_received = []

def notification_handler(sender, data):
    """Handle notifications"""
    notifications_received.append({
        'sender': str(sender),
        'data': data.hex(),
        'raw': data
    })
    print(f"  📨 Notification: {data.hex()} ({len(data)} bytes)")

async def read_all_characteristics():
    """Try to read all readable characteristics"""
    print("=" * 70)
    print("READING DEVICE CONFIGURATION")
    print("=" * 70)
    print("Attempting to read LED count and other configuration values")
    print("=" * 70)
    
    try:
        async with BleakClient(DEVICE_ADDRESS, timeout=10.0) as client:
            if client.is_connected:
                print("\n✓ Connected!")
                await asyncio.sleep(1.0)
                
                services = client.services
                services_list = list(services)
                
                # Enable notifications first
                print("\n" + "=" * 70)
                print("ENABLING NOTIFICATIONS")
                print("=" * 70)
                
                for service in services_list:
                    for char in service.characteristics:
                        if "notify" in char.properties or "indicate" in char.properties:
                            try:
                                await client.start_notify(char.uuid, notification_handler)
                                print(f"✓ Enabled notifications for {char.uuid}")
                            except Exception as e:
                                print(f"✗ Failed to enable {char.uuid}: {e}")
                
                await asyncio.sleep(0.5)
                
                # Try to read all readable characteristics
                print("\n" + "=" * 70)
                print("READING READABLE CHARACTERISTICS")
                print("=" * 70)
                
                for service in services_list:
                    print(f"\nService: {service.uuid}")
                    for char in service.characteristics:
                        if "read" in char.properties:
                            try:
                                value = await client.read_gatt_char(char.uuid)
                                print(f"  {char.uuid}:")
                                print(f"    Hex: {value.hex()}")
                                print(f"    Bytes: {list(value)}")
                                
                                # Try to interpret as LED count
                                if len(value) >= 2:
                                    # Try little-endian uint16
                                    le_uint16 = int.from_bytes(value[:2], byteorder='little')
                                    # Try big-endian uint16
                                    be_uint16 = int.from_bytes(value[:2], byteorder='big')
                                    print(f"    As uint16 LE: {le_uint16}")
                                    print(f"    As uint16 BE: {be_uint16}")
                                
                                if len(value) >= 4:
                                    # Try uint32
                                    le_uint32 = int.from_bytes(value[:4], byteorder='little')
                                    be_uint32 = int.from_bytes(value[:4], byteorder='big')
                                    print(f"    As uint32 LE: {le_uint32}")
                                    print(f"    As uint32 BE: {be_uint32}")
                                
                                # Check if value looks like LED count (around 70 or 200)
                                if len(value) >= 2:
                                    if le_uint16 in [70, 71, 72, 200] or be_uint16 in [70, 71, 72, 200]:
                                        print(f"    ⚠️  Possible LED count!")
                                
                            except Exception as e:
                                print(f"  {char.uuid}: ✗ Cannot read - {str(e)[:50]}")
                
                # Try requesting LED count via command
                print("\n" + "=" * 70)
                print("REQUESTING LED COUNT VIA COMMAND")
                print("=" * 70)
                
                # Try various read commands
                read_commands = [
                    (bytearray.fromhex("03 4C 45 44 00 00 00 00 00 00 00 00 00 00 00 00"), "Read LED count"),
                    (bytearray.fromhex("03 4C 41 4D 50 00 00 00 00 00 00 00 00 00 00 00"), "Read LAMP count"),
                    (bytearray.fromhex("03 43 4F 4E 46 49 47 00 00 00 00 00 00 00 00"), "Read CONFIG"),
                    (bytearray.fromhex("03 53 45 47 4D 45 4E 54 00 00 00 00 00 00 00"), "Read SEGMENT"),
                ]
                
                for cmd_bytes, desc in read_commands:
                    try:
                        print(f"\nSending: {desc}")
                        encrypted = encrypt_aes_ecb(bytes(cmd_bytes))
                        await client.write_gatt_char(WRITE_CMD_UUID, encrypted, response=False)
                        await asyncio.sleep(2)  # Wait for notification
                    except Exception as e:
                        print(f"  ✗ Failed: {e}")
                
                # Show notifications
                if notifications_received:
                    print("\n" + "=" * 70)
                    print("NOTIFICATIONS RECEIVED:")
                    print("=" * 70)
                    for i, notif in enumerate(notifications_received, 1):
                        print(f"\nNotification {i}:")
                        print(f"  From: {notif['sender']}")
                        print(f"  Hex: {notif['data']}")
                        print(f"  Bytes: {list(notif['raw'])}")
                        
                        # Try to interpret
                        data = notif['raw']
                        if len(data) >= 2:
                            le_16 = int.from_bytes(data[:2], byteorder='little')
                            be_16 = int.from_bytes(data[:2], byteorder='big')
                            if le_16 in [70, 71, 72, 200] or be_16 in [70, 71, 72, 200]:
                                print(f"  ⚠️  Possible LED count: LE={le_16}, BE={be_16}")
                else:
                    print("\n⚠ No notifications received")
                
                print("\n" + "=" * 70)
                print("ANALYSIS")
                print("=" * 70)
                print("Based on your test results:")
                print("  1. Individual LED commands don't work beyond LED 70")
                print("  2. LED count setting is ignored (always same LEDs)")
                print("  3. This strongly suggests a FIRMWARE/CONFIGURATION issue")
                print("\nThe device appears to have a hard limit set to ~70 LEDs")
                print("and is ignoring our commands to change it.")
                print("\nNext steps:")
                print("  - Firmware update is likely needed")
                print("  - Or manufacturer reset procedure")
                print("  - Or try extended power cycle (24+ hours)")
                
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
    asyncio.run(read_all_characteristics())

