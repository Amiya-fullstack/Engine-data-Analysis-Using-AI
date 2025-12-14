# FM-03: Combustion Instability Event

**Category:** Thermal/Fluid Dynamic Fault

**Primary Sensors:** `sensor_3`, `sensor_4`

## Description
Represents unstable combustion leading to fluctuating pressure and temperature cycles inside the combustion chamber.

## Trigger Conditions
- `sensor_3` oscillation amplitude > 0.35
- `sensor_4` > 2.0 °C for ≥ 3 cycles

## Root Causes
- Distorted airflow patterns
- Residual gas buildup
- Malfunctioning igniter sequence

## Early Indicators
- Rapid RUL decline (> 2 units/min)
- Irregular turbine temperature deltas
- Audible irregular combustion pulses

## Operational Impact
- Thermal fatigue to turbine blades
- Accelerated mechanical wear

## Recommended Actions
- Run airflow harmonization test
- Inspect igniter wiring and spark profile
- Clean compressor intake vanes
