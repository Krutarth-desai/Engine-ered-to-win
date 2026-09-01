-- ============================================================
-- AeroTwin | Predictive Maintenance Supabase Schema
-- ============================================================
-- This script creates the tables for logging ML anomalies 
-- and predictive maintenance recommendations.

-- 1. TELEMETRY ANOMALIES TABLE
CREATE TABLE IF NOT EXISTS public.telemetry_anomalies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    engine_id TEXT NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT now(),
    anomaly_score FLOAT NOT NULL,
    severity TEXT NOT NULL,
    fault_type TEXT,
    evidence TEXT,
    treatment_action TEXT,
    prevention_action TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Enable RLS
ALTER TABLE public.telemetry_anomalies ENABLE ROW LEVEL SECURITY;

-- Allow authenticated users to insert anomalies (from client side or server via service role)
DROP POLICY IF EXISTS "Authenticated users can insert anomalies" ON public.telemetry_anomalies;
CREATE POLICY "Authenticated users can insert anomalies"
    ON public.telemetry_anomalies
    FOR INSERT
    TO authenticated
    WITH CHECK (true);

-- Allow authenticated users to view anomalies
DROP POLICY IF EXISTS "Authenticated users can view anomalies" ON public.telemetry_anomalies;
CREATE POLICY "Authenticated users can view anomalies"
    ON public.telemetry_anomalies
    FOR SELECT
    TO authenticated
    USING (true);

-- ✅ DONE
