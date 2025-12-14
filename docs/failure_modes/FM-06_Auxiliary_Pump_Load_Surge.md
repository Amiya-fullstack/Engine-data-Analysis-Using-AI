# FM-06: Auxiliary Pump Load Surge

**Category:** Support System Fault

**Primary Sensors:** `sensor_6`

## Description
Indicates abnormal increased load in the auxiliary pump, often compensating for friction, temperature anomalies, or fluid resistance.

## Trigger Conditions
- `sensor_6` > 0.20 load index

## Root Causes
- Pump cavitation
- Hydraulic line blockage
- Increased resistance due to turbine overheating

## Early Indicators
- Slight correlated rise in `sensor_4`
- Slower RUL decrement followed by sudden drop

## Operational Impact
- Reduced cooling efficiency
- Failure to maintain pressure regulation

## Recommended Actions
- Inspect hydraulic circuits
- Evaluate cooling flow rate
- Replace pump impeller if cavitation marks detected
