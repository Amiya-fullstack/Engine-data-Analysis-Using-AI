# FM-04: Turbine Overheat Condition

**Category:** Thermal Overload

**Primary Sensors:** `sensor_4`

## Description
Occurs when turbine temperature rises above safe thresholds due to operational overload, airflow restriction, or cooling inefficiency.

## Trigger Conditions
- `sensor_4` > 3.0 °C for 2+ consecutive readings

## Root Causes
- Cooling duct obstruction
- Reduced airflow from compressor
- Excessive combustion heat due to fuel-rich conditions

## Early Indicators
- Spike in `sensor_4` without corresponding `sensor_1` vibration increase
- Rising auxiliary pump load (`sensor_6`)

## Operational Impact
- Accelerated blade oxidation
- Potential micro-cracking in turbine housing

## Recommended Actions
- Inspect cooling ducts for blockages
- Verify airflow through compressor stage
- Inspect turbine insulation integrity
