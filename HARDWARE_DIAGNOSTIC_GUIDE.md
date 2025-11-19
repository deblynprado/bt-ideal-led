# Hardware Diagnostic Guide for LED Strip

## Purpose
Determine if the issue is **hardware-related** (physical damage, power supply, connections) vs **software-related** (configuration, firmware).

## Quick Test Script

Run the comprehensive hardware test:
```bash
python3 /Users/deblynprado/Downloads/bt_test_hardware.py
```

This will:
1. Test individual LEDs beyond LED 70
2. Test LED ranges (70-200)
3. Test power supply stability

## Physical Inspection Checklist

### 1. LED Strip Physical Condition

**Visual Inspection:**
- [ ] Check for **visible damage** on the strip
- [ ] Look for **cut marks** or **scratches** on the circuit board
- [ ] Check for **burn marks** or **discoloration**
- [ ] Inspect **LEDs themselves** - any cracked or damaged LEDs?
- [ ] Check **flexibility** - strip should bend smoothly, not crack

**Connection Points:**
- [ ] Check **connector between controller and strip** - is it secure?
- [ ] Check **connector between strip segments** (if applicable)
- [ ] Look for **loose wires** or **exposed copper**
- [ ] Check for **corrosion** on connectors

### 2. Power Supply Check

**Power Supply Rating:**
- [ ] Check **voltage rating** (should match strip requirement, usually 12V or 24V)
- [ ] Check **current rating** (amperage)
  - For 200 LEDs: Typically need **10-20A** depending on LED type
  - If power supply is too weak, LEDs won't light properly
- [ ] Check **power supply label** for specifications

**Power Supply Testing:**
- [ ] Try **different power supply** (if available)
  - Use one rated for higher current
  - Use one from another identical working strip
- [ ] Check **power supply output** with multimeter (if available)
  - Should read correct voltage under load
- [ ] Check **power supply temperature** - should not be hot

**Connection:**
- [ ] Check **power supply connector** - is it secure?
- [ ] Check **power wires** - any damage or loose connections?
- [ ] Check **polarity** - positive/negative connected correctly?

### 3. Controller Check

**Physical Inspection:**
- [ ] Check controller for **visible damage**
- [ ] Check **LEDs on controller** (if any) - do they light up?
- [ ] Check **reset button** (if exists) - does it work?
- [ ] Check **Bluetooth indicator** - does it blink/light?

**Connection:**
- [ ] Check **controller-to-strip connection** - secure?
- [ ] Check **controller power connection** - secure?
- [ ] Try **reconnecting** all connections

### 4. LED Strip Segment Testing

**Test Different Segments:**
- [ ] **LEDs 1-70**: Do these work? (You said yes)
- [ ] **LEDs 71-100**: Do these respond to individual commands?
- [ ] **LEDs 101-150**: Do these respond?
- [ ] **LEDs 151-200**: Do these respond?

**How to Test:**
- Use `bt_test_hardware.py` script
- It will light individual LEDs beyond LED 70
- Watch carefully - do LEDs 71+ light up individually?

### 5. Comparison Test

**If you have another identical LED strip:**
- [ ] **Swap controllers**: Use this controller on other strip
  - If other strip works with 200 LEDs: This controller is fine
  - If other strip also limited to 70: Controller has config issue
- [ ] **Swap power supplies**: Use other strip's power supply
  - If LEDs work with other power supply: Power supply issue
  - If still limited: Not power supply issue
- [ ] **Swap strips**: Use other strip with this controller
  - If other strip works: This strip has hardware issue
  - If other strip also limited: Controller/config issue

## Interpreting Test Results

### Scenario 1: Individual LEDs 71+ DON'T Light Up
**Possible Causes:**
- ✅ **Configuration limit** (most likely) - firmware/config limiting to 70 LEDs
- ⚠️ **Hardware issue** - strip damaged at LED 70
- ⚠️ **Power supply insufficient** - can't power beyond 70 LEDs

**Next Steps:**
- Check power supply rating
- Try different power supply
- Check for physical damage at LED 70
- If no hardware issues found: Configuration/firmware problem

### Scenario 2: Individual LEDs 71+ DO Light Up
**Possible Causes:**
- ✅ **Configuration issue** (most likely) - LEDs work but config limits them
- ✅ **Firmware issue** - needs reset or update

**Next Steps:**
- This confirms it's NOT a hardware issue
- Focus on firmware update or configuration reset
- Try factory reset commands
- Contact manufacturer for reset procedure

### Scenario 3: LEDs Flicker or Dim When Testing
**Possible Causes:**
- ⚠️ **Power supply insufficient** - can't provide enough current
- ⚠️ **Loose connection** - intermittent contact
- ⚠️ **Damaged strip** - internal resistance issues

**Next Steps:**
- Check power supply rating
- Try different power supply
- Check all connections
- Look for physical damage

### Scenario 4: LEDs Work Up to Certain Count, Then Stop
**Example: Works up to 100 LEDs, stops at 101**
**Possible Causes:**
- ✅ **Segment configuration** - strip split into segments
- ✅ **Power limit** - power supply can only handle certain number
- ⚠️ **Hardware damage** - strip damaged at that point

**Next Steps:**
- Note exact LED count where it stops
- Check for physical damage at that point
- Check power supply rating
- Try different power supply

## Quick Hardware Test Procedure

1. **Run hardware test script:**
   ```bash
   python3 /Users/deblynprado/Downloads/bt_test_hardware.py
   ```

2. **Observe results:**
   - Do LEDs 71+ light up individually?
   - How many LEDs light up when count is set to 200?
   - Do LEDs flicker or dim?

3. **Physical inspection:**
   - Check strip for damage
   - Check power supply rating
   - Check all connections

4. **Comparison test (if possible):**
   - Try different power supply
   - Try different controller
   - Try different strip

## Expected Results

**If Hardware is OK:**
- Individual LEDs 71+ should light up when addressed
- Power supply should handle full brightness
- No visible damage
- Connections secure

**If Hardware has Issue:**
- LEDs 71+ don't respond at all
- Visible damage on strip
- Power supply insufficient
- Flickering/dimming under load

## Next Steps Based on Results

**If hardware test shows LEDs 71+ work:**
→ Focus on **firmware update** or **configuration reset**

**If hardware test shows LEDs 71+ don't work:**
→ Check **power supply**, **connections**, and **physical damage**
→ If all hardware is OK, it's still likely a **configuration issue**

**If unsure:**
→ Try **different power supply** first (easiest test)
→ Then try **different controller** (if available)
→ Then try **different strip** (if available)

