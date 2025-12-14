# FM-02: Compressor Fuel-Air Mixing Deviation

**Category:** Combustion System Fault

**Primary Sensors:** `sensor_2`

## Description
Fault detected when the fuel–air mixture deviates from optimal ratios, impacting combustion efficiency and emissions.

## Trigger Conditions
- `sensor_2` < -0.20 deviation index
- `sensor_2` drift > 0.3 within 10 minutes

## Root Causes
- Fuel injector partial blockage
- Compressor pressure oscillation
- Sensor calibration drift

## Early Indicators
- Mild combustion instability (`sensor_3` oscillations)
- Increase in exhaust opacity
- Sluggish acceleration response

## Operational Impact
- 4–9% efficiency loss
- Increased exhaust temperature ripple

## Recommended Actions
- Inspect fuel delivery manifold
- Recalibrate mixture control system
- Replace injector if fouling detected
