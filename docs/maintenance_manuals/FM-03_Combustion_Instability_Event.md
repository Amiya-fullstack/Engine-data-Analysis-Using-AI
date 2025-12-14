# Maintenance Manual — FM-03: Combustion Instability Event

## Safety Precautions
- Ensure ignition system is deenergized before inspecting wiring.
- Follow thermal cooldown procedures; avoid opening hot sections.

## Tools & Equipment
- Oscilloscope or high-speed data logger
- Combustion camera or borescope
- Spark/igniter test bench
- Airflow balancing rig

## Estimated Time
- Diagnostic tests: 1–3 hours
- Repairs and cleaning: 3–6 hours

## Steps
1. Record high-speed traces of pressure and temperature (`sensor_3`, `sensor_4`) during a controlled run.
2. Run airflow harmonization tests: adjust vane angles and measure response.
3. Inspect igniter wiring and perform spark profile tests; replace faulty igniters.
4. Clean compressor intake vanes and check for debris or erosion altering flow patterns.
5. If residual gas buildup suspected, perform controlled purge and inspect fuel timing.

## Verification
- `sensor_3` oscillation amplitude reduced below 0.35 during normal cycles.
- No repeated temperature excursions (`sensor_4`) greater than 2.0 °C for 3 cycles.
- RUL trend stabilized.
