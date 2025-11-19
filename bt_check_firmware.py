#!/usr/bin/env python3
"""Check firmware version and OTA update capabilities

This script checks if the device supports firmware updates and shows
the current firmware version.
"""
import asyncio
from bleak import BleakClient
from Crypto.Cipher import AES

# Device address - UPDATE THIS with your device UUID
# Find your device UUID by running: python3 bt_discover.py
DEVICE_ADDRESS = "YOUR-DEVICE-UUID-HERE"

# Protocol constants
SERVICE_UUID = "0000fff0-0000-1000-8000-00805f9b34fb"
WRITE_CMD_UUID = "d44bc439-abfd-45a2-b575-925416129600"
NOTIFICATION_UUID = "d44bc439-abfd-45a2-b575-925416129601"
OTA_SERVICE_UUID = "0000ae00-0000-1000-8000-00805f9b34fb"  # OTA service (if exists)

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

# Store notifications
notifications = []

def notification_handler(sender, data):
    """Handle notifications"""
    notifications.append({
        'sender': str(sender),
        'data': data.hex(),
        'timestamp': asyncio.get_event_loop().time()
    })
    print(f"  📨 Notification from {sender}: {data.hex()}")

async def check_firmware():
    """Check firmware version and OTA capabilities"""
    print("=" * 70)
    print("CHECKING FIRMWARE VERSION AND OTA CAPABILITIES")
    print("=" * 70)
    
    try:
        async with BleakClient(DEVICE_ADDRESS, timeout=10.0) as client:
            if client.is_connected:
                print("\n✓ Connected!")
                await asyncio.sleep(1.0)
                
                services = client.services
                services_list = list(services)
                
                print(f"\nFound {len(services_list)} service(s):")
                for service in services_list:
                    print(f"  - {service.uuid}")
                    if "ae00" in str(service.uuid).lower():
                        print(f"    ⚠ OTA Service detected!")
                
                # Enable notifications to receive version info
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
                
                # Try to get version
                print("\n" + "=" * 70)
                print("REQUESTING FIRMWARE VERSION")
                print("=" * 70)
                
                # Version request commands from the repo
                version_commands = [
                    (bytearray.fromhex("03 56 45 00 00 00 00 00 00 00 00 00 00 00 00 00"), "PCB Version"),
                    (bytearray.fromhex("03 56 45 01 00 00 00 00 00 00 00 00 00 00 00 00"), "Firmware Version"),
                ]
                
                for cmd_bytes, desc in version_commands:
                    try:
                        print(f"\nRequesting {desc}...")
                        encrypted = encrypt_aes_ecb(bytes(cmd_bytes))
                        await client.write_gatt_char(WRITE_CMD_UUID, encrypted, response=False)
                        await asyncio.sleep(2)  # Wait for notification
                    except Exception as e:
                        print(f"  ✗ Failed: {e}")
                
                # Show notifications received
                if notifications:
                    print("\n" + "=" * 70)
                    print("NOTIFICATIONS RECEIVED:")
                    print("=" * 70)
                    for notif in notifications:
                        print(f"  From {notif['sender']}: {notif['data']}")
                else:
                    print("\n⚠ No version notifications received")
                    print("  Device might not support version queries via BLE")
                
                print("\n" + "=" * 70)
                print("FIRMWARE UPDATE OPTIONS")
                print("=" * 70)
                print("1. MANUFACTURER'S APP:")
                print("   - Open iDeal LED app")
                print("   - Look for 'Settings' → 'Firmware Update' or 'About'")
                print("   - Check for 'Update' or 'Upgrade' options")
                print("\n2. MANUFACTURER WEBSITE:")
                print("   - Visit manufacturer's website")
                print("   - Look for firmware downloads")
                print("   - Check if they provide update tools")
                print("\n3. CONTACT MANUFACTURER:")
                print("   - Ask for firmware reset procedure")
                print("   - Request firmware update file")
                print("   - Ask about factory reset command")
                print("\n4. PHYSICAL RESET:")
                print("   - Check controller for reset button")
                print("   - Look for small pinhole reset button")
                print("   - Check manual for reset procedure")
                print("\n5. EXTENDED POWER CYCLE:")
                print("   - Unplug power for 24+ hours")
                print("   - Some devices reset after extended power loss")
                
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
    asyncio.run(check_firmware())

