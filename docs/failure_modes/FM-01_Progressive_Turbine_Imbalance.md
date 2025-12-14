# FM-01: Progressive Turbine Imbalance

**Category:** Mechanical Degradation

**Primary Sensors:** `sensor_1`, `sensor_4`, `sensor_5`

## Description
This failure mode represents progressive mechanical imbalance in the high-speed turbine shaft. It is typically driven by mass asymmetry, blade erosion, or thermal-induced warping.

## Trigger Conditions
- `sensor_1` < -0.65 g for ≥ 4 consecutive minutes
- `sensor_4` > 2.5 °C above baseline
- RUL decreases faster than 1.5 units/min

## Root Causes
- Thermal deformation of turbine blades
- Debris accumulation in the rotor
- Worn or misaligned shaft bearings

## Early Indicators
- Increased low-frequency vibration signatures
- Slight rise in temperature delta (`sensor_4`)
- Mild reduction in efficiency

## Operational Impact
- 5–18% reduction in turbine efficiency
- Risk of catastrophic seizure within 10–20 cycles

## Recommended Actions
- Perform shaft balance inspection
- Remove rotor casing and check for asymmetric blade wear
- Reset vibration thresholds post-maintenance
