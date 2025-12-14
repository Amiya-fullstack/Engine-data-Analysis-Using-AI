# Engine Specification & Diagnostic Rules

## Sensors and Definitions
- **sensor_1**: Vibration index (g). Measures shaft/turbine vibration; negative values indicate specific axis offset in this dataset.
- **sensor_2**: Fuel–air mixture deviation index (unitless deviation index). Negative values indicate leaner mixture.
- **sensor_3**: Combustion pressure/oscillation amplitude (unitless).
- **sensor_4**: Temperature delta (°C) relative to baseline. Used to detect overheating and thermal events.
- **sensor_5**: Bearing friction index (unitless); lower (more negative) values indicate increased friction/wear.
- **sensor_6**: Auxiliary pump load index (unitless), indicates pump effort/compensation load.

## Trigger Thresholds (as extracted from `engine_spec_data.doc`)
- **FM-01 (Progressive Turbine Imbalance):**
  - `sensor_1` < -0.65 g for ≥ 4 consecutive minutes
  - `sensor_4` > 2.5 °C above baseline
  - RUL decreasing faster than 1.5 units/min

- **FM-02 (Compressor Fuel-Air Mixing Deviation):**
  - `sensor_2` < -0.20 deviation index
  - `sensor_2` drift > 0.3 within 10 minutes

- **FM-03 (Combustion Instability):**
  - `sensor_3` oscillation amplitude > 0.35
  - `sensor_4` > 2.0 °C for ≥ 3 cycles

- **FM-04 (Turbine Overheat):**
  - `sensor_4` > 3.0 °C for 2+ consecutive readings

- **FM-05 (Bearing Wear Acceleration):**
  - `sensor_5` < -0.75 friction index
  - correlated `sensor_1` vibration > 0.4 deviation
  - `sensor_6` increases by > 0.1 compensation load

- **FM-06 (Auxiliary Pump Load Surge):**
  - `sensor_6` > 0.20 load index

## Diagnostic Rule Guidance
- Treat consecutive time windows and cycles carefully: where the spec uses "consecutive minutes" or "consecutive readings", implement detection with sliding-window aggregation (time-series windowing) and minimum count thresholds.
- Use a combination of absolute thresholds (e.g., `sensor_4` > 3.0 °C) and rate-based triggers (e.g., RUL decline > 1.5 units/min); both should be able to trigger alerts but may have different severity levels.
- Correlation checks: for cross-sensor conditions (e.g., `sensor_5` + `sensor_1` correlation), compute short-term correlation coefficients or rule-based co-occurrence (both exceed thresholds within a short window).

## Sampling & Window Recommendations
- Sampling frequency should capture high-frequency vibration phenomena; recommended ≥ 1 Hz with capability to capture higher-rate oscillations if present.
- For minute-based conditions (e.g., ≥ 4 consecutive minutes), use sliding windows with sample-count-based thresholds (e.g., 4 samples at 1 Hz) or time-based aggregation if sampling varies.
- For cycle-based rules (e.g., 3 cycles), define a cycle detection procedure based on periodic signals (e.g., combustion cycles per revolution) and count anomalies across cycles.

## Integration Notes
- Store raw sensor streams and precomputed feature windows (e.g., short-time RMS, amplitude envelopes) to speed up online diagnostics.
- Maintain a baseline profile for each unit to compute delta-based thresholds (`sensor_4` above baseline).
- Log detected events with timestamps, supporting raw windows, and pre/post-maintenance baselines for auditability.

## Mapping: FM → Actions
- Each FM should map to a maintenance ticket with severity (High/Medium/Low), suggested immediate actions (as per maintenance manuals), and suggested observation/verification steps.

---

*Document generated from `data_sources/engine_spec_data.doc`. If the operational environment uses different units or sampling rates, adapt thresholds appropriately and validate against historical failure data.*