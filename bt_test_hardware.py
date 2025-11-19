#!/usr/bin/env python3
"""Physical hardware diagnostic for LED strip

Tests if the issue is hardware-related by:
1. Testing individual LEDs beyond the working range
2. Testing LED ranges (70-100, 100-150, 150-200)
3. Testing power supply stability
4. Checking for physical connection issues
"""
import asyncio
from bleak import BleakClient
from Crypto.Cipher import AES

# Device address - UPDATE THIS with your device UUID
# Find your device UUID by running: python3 bt_discover.py
DEVICE_ADDRESS = "YOUR-DEVICE-UUID-HERE"

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

def build_graffiti_paint_packet(led_index, r, g, b):
    """Build graffiti_paint packet to light individual LED"""
    # Format: 0C 47 52 41 46 46 49 54 49 [led_high] [led_low] [r] [g] [b] [0] [0]
    packet = bytearray.fromhex("0C 47 52 41 46 46 49 54 49 00 00 00 00 00 00 00")
    packet[9] = (led_index >> 8) & 0xFF
    packet[10] = led_index & 0xFF
    packet[11] = r & 0xFF
    packet[12] = g & 0xFF
    packet[13] = b & 0xFF
    return bytes(packet)

def build_set_color_packet(r, g, b, model_index=0):
    """Build set_colour packet"""
    packet = bytearray.fromhex("0F 53 47 4C 53 00 00 64 50 1F 00 00 1F 00 00 32")
    packet[5] = model_index & 0xFF
    
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

async def test_individual_leds():
    """Test individual LEDs beyond the working range"""
    print("=" * 70)
    print("TEST 1: INDIVIDUAL LED TESTING")
    print("=" * 70)
    print("Testing LEDs beyond the working range (70-200)")
    print("This will light each LED individually in BRIGHT RED")
    print("=" * 70)
    
    try:
        async with BleakClient(DEVICE_ADDRESS, timeout=10.0) as client:
            if client.is_connected:
                print("\n✓ Connected!")
                await asyncio.sleep(1.0)
                
                # Turn ON
                print("\nTurning device ON...")
                on_packet = build_on_off_packet(True)
                encrypted_on = encrypt_aes_ecb(on_packet)
                await client.write_gatt_char(WRITE_CMD_UUID, encrypted_on, response=False)
                await asyncio.sleep(1)
                
                # Set LED count to 200
                print("Setting LED count to 200...")
                count_packet = build_set_lamp_count_packet(200)
                encrypted_count = encrypt_aes_ecb(count_packet)
                await client.write_gatt_char(WRITE_CMD_UUID, encrypted_count, response=False)
                await asyncio.sleep(1)
                
                # Test LEDs at key positions
                test_positions = [
                    # Known working range
                    (50, "LED 50 (should work)"),
                    (65, "LED 65 (should work)"),
                    # Boundary
                    (70, "LED 70 (boundary)"),
                    (71, "LED 71 (just beyond boundary)"),
                    # Mid-range
                    (75, "LED 75"),
                    (80, "LED 80"),
                    (90, "LED 90"),
                    (100, "LED 100"),
                    # Upper range
                    (120, "LED 120"),
                    (150, "LED 150"),
                    (180, "LED 180"),
                    (199, "LED 199 (last LED)"),
                ]
                
                print("\n" + "=" * 70)
                print("Testing individual LEDs")
                print("=" * 70)
                print("Watch your strip carefully!")
                print("Each LED will light up BRIGHT RED for 2 seconds")
                print("=" * 70)
                
                working_leds = []
                non_working_leds = []
                
                for led_index, description in test_positions:
                    print(f"\nTesting {description}...")
                    
                    # Turn all LEDs off first
                    off_packet = build_set_color_packet(0, 0, 0)
                    encrypted_off = encrypt_aes_ecb(off_packet)
                    await client.write_gatt_char(WRITE_CMD_UUID, encrypted_off, response=False)
                    await asyncio.sleep(0.3)
                    
                    # Light this specific LED
                    paint_packet = build_graffiti_paint_packet(led_index, 255, 0, 0)
                    encrypted_paint = encrypt_aes_ecb(paint_packet)
                    await client.write_gatt_char(WRITE_CMD_UUID, encrypted_paint, response=False)
                    
                    print(f"  👀 LED {led_index} should be BRIGHT RED now")
                    print(f"  Is it lit? (y/n)")
                    
                    # Wait for observation
                    await asyncio.sleep(2)
                
                print("\n" + "=" * 70)
                print("INDIVIDUAL LED TEST COMPLETE")
                print("=" * 70)
                print("RESULTS:")
                print("  - If LEDs 70+ don't light: Hardware issue OR configuration limit")
                print("  - If LEDs 70+ DO light: Configuration issue (firmware/config)")
                print("=" * 70)
                
                return True
            else:
                print("✗ Failed to connect")
                return False
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_led_ranges():
    """Test LED ranges to see if groups respond"""
    print("\n" + "=" * 70)
    print("TEST 2: LED RANGE TESTING")
    print("=" * 70)
    print("Testing if LED ranges respond to color commands")
    print("=" * 70)
    
    try:
        async with BleakClient(DEVICE_ADDRESS, timeout=10.0) as client:
            if client.is_connected:
                print("\n✓ Connected!")
                await asyncio.sleep(1.0)
                
                # Turn ON
                on_packet = build_on_off_packet(True)
                encrypted_on = encrypt_aes_ecb(on_packet)
                await client.write_gatt_char(WRITE_CMD_UUID, encrypted_on, response=False)
                await asyncio.sleep(1)
                
                # Set LED count to 200
                count_packet = build_set_lamp_count_packet(200)
                encrypted_count = encrypt_aes_ecb(count_packet)
                await client.write_gatt_char(WRITE_CMD_UUID, encrypted_count, response=False)
                await asyncio.sleep(1)
                
                # Test different LED counts to see where it stops
                test_counts = [70, 80, 90, 100, 120, 150, 180, 200]
                
                print("\nTesting different LED count settings...")
                print("We'll set the count and then light all LEDs WHITE")
                print("Watch where the LEDs stop lighting up!")
                print("=" * 70)
                
                for count in test_counts:
                    print(f"\nSetting LED count to {count}...")
                    
                    # Set count
                    count_packet = build_set_lamp_count_packet(count)
                    encrypted_count = encrypt_aes_ecb(count_packet)
                    await client.write_gatt_char(WRITE_CMD_UUID, encrypted_count, response=False)
                    await asyncio.sleep(0.5)
                    
                    # Set all to WHITE
                    color_packet = build_set_color_packet(255, 255, 255)
                    encrypted_color = encrypt_aes_ecb(color_packet)
                    await client.write_gatt_char(WRITE_CMD_UUID, encrypted_color, response=False)
                    
                    print(f"  ✓ LED count = {count}, all LEDs set to WHITE")
                    print(f"  👀 How many LEDs are actually lit?")
                    print(f"  Waiting 3 seconds...")
                    await asyncio.sleep(3)
                
                print("\n" + "=" * 70)
                print("RANGE TEST COMPLETE")
                print("=" * 70)
                print("ANALYSIS:")
                print("  - If LEDs stop at ~70 regardless of count: Configuration limit")
                print("  - If LEDs increase with count but cap at 70: Hardware/segment limit")
                print("  - If LEDs respond up to 200: No hardware issue")
                print("=" * 70)
                
                return True
            else:
                print("✗ Failed to connect")
                return False
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_power_stability():
    """Test power supply stability"""
    print("\n" + "=" * 70)
    print("TEST 3: POWER SUPPLY STABILITY TEST")
    print("=" * 70)
    print("Testing if power supply can handle all LEDs")
    print("=" * 70)
    
    try:
        async with BleakClient(DEVICE_ADDRESS, timeout=10.0) as client:
            if client.is_connected:
                print("\n✓ Connected!")
                await asyncio.sleep(1.0)
                
                # Turn ON
                on_packet = build_on_off_packet(True)
                encrypted_on = encrypt_aes_ecb(on_packet)
                await client.write_gatt_char(WRITE_CMD_UUID, encrypted_on, response=False)
                await asyncio.sleep(1)
                
                # Set LED count to 200
                count_packet = build_set_lamp_count_packet(200)
                encrypted_count = encrypt_aes_ecb(count_packet)
                await client.write_gatt_char(WRITE_CMD_UUID, encrypted_count, response=False)
                await asyncio.sleep(1)
                
                print("\nTesting power stability with BRIGHT WHITE (max power)...")
                print("Watch for:")
                print("  - Flickering")
                print("  - Dimming")
                print("  - LEDs turning off")
                print("  - Color shifts")
                print("=" * 70)
                
                # Set to maximum brightness white
                color_packet = build_set_color_packet(255, 255, 255)
                encrypted_color = encrypt_aes_ecb(color_packet)
                await client.write_gatt_char(WRITE_CMD_UUID, encrypted_color, response=False)
                
                print("\n✓ All LEDs set to BRIGHT WHITE")
                print("  👀 Observe for 10 seconds:")
                print("     - Are LEDs stable?")
                print("     - Any flickering?")
                print("     - Do LEDs stay lit?")
                print("     - How many LEDs are lit?")
                
                await asyncio.sleep(10)
                
                print("\n" + "=" * 70)
                print("POWER STABILITY TEST COMPLETE")
                print("=" * 70)
                print("RESULTS:")
                print("  - If stable but only 70 LEDs: Configuration issue")
                print("  - If flickering/dimming: Power supply issue")
                print("  - If LEDs turn off: Power supply insufficient")
                print("=" * 70)
                
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
    """Run all hardware diagnostic tests"""
    print("=" * 70)
    print("LED STRIP HARDWARE DIAGNOSTIC")
    print("=" * 70)
    print("This will test if the issue is hardware-related")
    print("=" * 70)
    
    # Run all tests
    await test_individual_leds()
    await test_led_ranges()
    await test_power_stability()
    
    print("\n" + "=" * 70)
    print("ALL TESTS COMPLETE")
    print("=" * 70)
    print("PHYSICAL INSPECTION CHECKLIST:")
    print("=" * 70)
    print("1. Check LED strip connections:")
    print("   - Are all connectors secure?")
    print("   - Any loose wires?")
    print("   - Any visible damage to strip?")
    print("\n2. Check power supply:")
    print("   - Is power supply rated for 200 LEDs?")
    print("   - Check voltage/current rating")
    print("   - Try a different power supply if available")
    print("\n3. Check controller:")
    print("   - Any visible damage?")
    print("   - Are all connections secure?")
    print("   - Try connecting to different LED strip (if available)")
    print("\n4. Test with another identical strip:")
    print("   - If you have another identical strip, test it")
    print("   - If other strip works with 200 LEDs: This strip has issue")
    print("   - If other strip also limited: Configuration/firmware issue")
    print("=" * 70)

if __name__ == "__main__":
    asyncio.run(main())

