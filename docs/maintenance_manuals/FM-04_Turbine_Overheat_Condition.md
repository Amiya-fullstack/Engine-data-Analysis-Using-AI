# Maintenance Manual — FM-04: Turbine Overheat Condition

## Safety Precautions
- Allow full cooldown before inspecting turbine internals.
- Use protective equipment for thermal inspections.

## Tools & Equipment
- Thermal imaging camera
- Airflow flowmeter
- Duct inspection tools (mirror/borescope)
- Insulation/patch kits

## Estimated Time
- Inspection and cleaning: 1–3 hours
- Repair of insulation/ducts: 2–6 hours

## Steps
1. Take thermal imagery to identify local hotspots.
2. Inspect cooling ducts and remove obstructions.
3. Verify compressor airflow; check vanes and seals.
4. Inspect turbine insulation and repair or replace damaged sections.
5. Verify fuel control to ensure no fuel-rich conditions cause excess heat.

## Verification
- `sensor_4` returns below 3.0 °C above baseline in consecutive readings.
- Auxiliary pump (`sensor_6`) returns to normal operating range.
- No new signs of thermal fatigue on blades after inspection.
