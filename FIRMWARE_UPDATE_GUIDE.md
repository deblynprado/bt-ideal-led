# Firmware Update Guide for iDeal LED Controller

## Current Situation
- Only ~70 of 200 LEDs are working
- Configuration appears to be stuck in "parallel" mode
- Standard BLE commands don't reset the configuration
- Firmware update might reset to factory defaults

## Method 1: Check Current Firmware Version

Run this script to check your firmware version:
```bash
python3 /Users/deblynprado/Downloads/bt_check_firmware.py
```

This will:
- Show all BLE services (including OTA if available)
- Request firmware version from device
- Display any version information received

## Method 2: Use Manufacturer's App

### Steps:
1. **Open iDeal LED app** on your phone/tablet
2. **Connect to your device** (ISP-3C575D)
3. **Look for these menu options:**
   - Settings → About → Firmware Version
   - Settings → Device Settings → Firmware Update
   - Settings → Advanced → Update Firmware
   - Device Info → Check for Updates
   - Help → Firmware Update

4. **If update available:**
   - Follow app instructions
   - Keep device powered during update
   - Don't disconnect during update

## Method 3: Manufacturer Website

1. **Find manufacturer name:**
   - Check device label/sticker
   - Check app store listing for developer name
   - Check packaging/manual

2. **Search for:**
   - "[Manufacturer] LED controller firmware"
   - "[Manufacturer] firmware update"
   - "[Manufacturer] support downloads"

3. **Look for:**
   - Firmware download files (.bin, .hex, .fw)
   - Update tools/software
   - Instructions for your model

## Method 4: Contact Manufacturer Support

**What to ask:**
- "How do I update firmware on model [your model]?"
- "How do I factory reset the LED count configuration?"
- "My device is stuck in parallel mode, how do I reset it?"
- "Can you provide firmware update file and instructions?"

**Information to provide:**
- Device model number
- Current firmware version (from app)
- Problem description (only 70 LEDs working, was 200)
- What you've tried

## Method 5: Physical Reset (If Available)

**Check controller for:**
- Small reset button (may be recessed)
- Pinhole reset button (use paperclip)
- Jumper pins for reset
- Reset switch

**If found:**
- Power OFF device
- Press and hold reset button
- Power ON while holding reset
- Hold for 10-30 seconds
- Release and wait for reset

## Method 6: Extended Power Cycle

Some devices reset after extended power loss:

1. **Unplug device completely**
2. **Wait 24-48 hours** (not just minutes)
3. **Plug back in**
4. **Test if configuration reset**

## Method 7: OTA Update via BLE (If Supported)

If the device supports OTA (Over-The-Air) updates, you might be able to:
- Use manufacturer's update tool
- Use BLE update protocol
- Requires firmware file from manufacturer

**Check if OTA is available:**
- Look for service UUID containing "ae00" or "fe59"
- Check manufacturer documentation
- Contact support

## Method 8: Alternative: Use Different App Version

Sometimes different app versions have different reset options:

1. **Uninstall current iDeal LED app**
2. **Download older/newer version** (if available)
3. **Try reset options in different version**
4. **Some apps have "Delete Device" option that resets it**

## Troubleshooting

**If firmware update fails:**
- Ensure stable power supply
- Keep device close during update
- Don't disconnect Bluetooth
- Try update multiple times

**If no firmware update available:**
- Ask manufacturer for factory reset procedure
- Ask if they can provide custom firmware
- Consider if device is under warranty

## Important Notes

⚠️ **WARNING:**
- Firmware updates can brick device if done incorrectly
- Always follow manufacturer instructions
- Backup settings if possible
- Ensure stable power during update

## Next Steps

1. Run `bt_check_firmware.py` to check current version
2. Check iDeal LED app for update options
3. Contact manufacturer support
4. Try physical reset if available
5. Consider warranty replacement if still under warranty

