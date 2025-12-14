# FM-05: Bearing Wear Acceleration

**Category:** Mechanical Wear

**Primary Sensors:** `sensor_5` (primary), `sensor_1`, `sensor_6` (secondary)

## Description
Represents rapid degradation of shaft bearings, increasing friction and causing cascading mechanical failure.

## Trigger Conditions
- `sensor_5` < -0.75 friction index
- Correlated `sensor_1` vibration > 0.4 deviation
- `sensor_6` increases by > 0.1 compensation load

## Root Causes
- Lubricant breakdown
- Bearing surface scoring
- Overheating from chemical degradation

## Early Indicators
- Gradual downward trend in `sensor_5`
- Increased energy consumption by auxiliary pump

## Operational Impact
- Higher vibration → risk of shaft misalignment
- Imbalance onset leading to FM-01

## Recommended Actions
- Perform lubrication refresh
- Inspect bearing assembly under magnification
- Run friction calibration cycle
