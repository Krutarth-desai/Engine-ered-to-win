-- ============================================================
-- AeroTwin | Sensor Diagnosis Schema Extension
-- ============================================================
-- Extends the existing telemetry_anomalies table with columns
-- for sensor-vs-engine diagnosis data.
-- Safe to re-run — uses IF NOT EXISTS throughout.
-- RLS remains enabled from the original table setup.
-- ============================================================

-- Add diagnosis columns to existing telemetry_anomalies table
ALTER TABLE public.telemetry_anomalies
  ADD COLUMN IF NOT EXISTS diagnosis_type TEXT;

ALTER TABLE public.telemetry_anomalies
  ADD COLUMN IF NOT EXISTS diagnosis_confidence FLOAT;

ALTER TABLE public.telemetry_anomalies
  ADD COLUMN IF NOT EXISTS suspected_sensor TEXT;

ALTER TABLE public.telemetry_anomalies
  ADD COLUMN IF NOT EXISTS affected_sensors JSONB;

ALTER TABLE public.telemetry_anomalies
  ADD COLUMN IF NOT EXISTS sensor_anomaly_scores JSONB;

COMMENT ON COLUMN public.telemetry_anomalies.diagnosis_type IS
  'NORMAL | POSSIBLE_SENSOR_FAILURE | POSSIBLE_ENGINE_FAILURE | UNKNOWN';

COMMENT ON COLUMN public.telemetry_anomalies.diagnosis_confidence IS
  'Confidence score for the primary diagnosis (0.0 to 1.0)';

COMMENT ON COLUMN public.telemetry_anomalies.suspected_sensor IS
  'For POSSIBLE_SENSOR_FAILURE: the suspected faulty sensor name (e.g., cht_c)';

COMMENT ON COLUMN public.telemetry_anomalies.affected_sensors IS
  'JSON array of sensor names showing anomalous readings (e.g., ["cht_c", "egt_c"])';

COMMENT ON COLUMN public.telemetry_anomalies.sensor_anomaly_scores IS
  'JSON object with per-sensor anomaly scores (e.g., {"rpm": 0.08, "cht_c": 0.94, ...})';

-- ✅ Schema extension complete
-- Note: RLS policies from supabase_complete_setup.sql remain in effect.
-- No new policies needed — existing INSERT/SELECT policies cover the new columns.
