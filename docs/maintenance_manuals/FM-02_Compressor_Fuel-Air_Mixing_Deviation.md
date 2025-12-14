# Maintenance Manual — FM-02: Compressor Fuel-Air Mixing Deviation

## Safety Precautions
- Work in a well-ventilated area; control ignition sources.
- Isolate fuel supply and depressurize the system before component work.

## Tools & Equipment
- Fuel pressure gauge and flow meter
- Injector cleaning kit / ultrasonic cleaner
- Gas analyzer (for exhaust composition)
- Calibration bench for mixture control

## Estimated Time
- Inspection & calibration: 1–3 hours
- Injector replacement/cleaning: 2–4 hours

## Steps
1. Put the engine into safe service mode and isolate fuel lines.
2. Inspect fuel injectors and manifold for signs of fouling; remove and clean with ultrasonic cleaner if necessary.
3. Check compressor pressure stability and correct any oscillation sources (e.g., leaking seals).
4. Recalibrate the mixture control system to factory settings.
5. Run a controlled ramp and use gas analyzer to verify exhaust composition is within spec.
6. If fouling or irreparable injector damage is found, replace injectors and re-test.

## Verification
- `sensor_2` returns to within ±0.1 of baseline deviation index.
- No drift > 0.3 within 10 minutes during steady-state tests.
- Combustion stability (`sensor_3`) shows no significant oscillations.
