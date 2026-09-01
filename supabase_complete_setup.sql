-- ============================================================
-- AeroTwin | Complete Supabase Setup Schema
-- ============================================================
-- This script contains ALL necessary tables, triggers, and RLS 
-- policies for the AeroTwin project (Profiles & Anomalies).
-- Safe to re-run — uses IF NOT EXISTS / OR REPLACE throughout.
-- ============================================================


-- ──────────────────────────────────────────────────────────────
-- PART 1: AUTHENTICATION & PROFILES
-- ──────────────────────────────────────────────────────────────

-- 1. CREATE THE PROFILES TABLE
CREATE TABLE IF NOT EXISTS public.profiles (
  id         UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
  full_name  TEXT,
  email      TEXT,
  avatar_url TEXT,
  role       TEXT NOT NULL DEFAULT 'viewer',
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

COMMENT ON TABLE public.profiles IS 'Application profiles for AeroTwin GCS operators. Linked 1:1 with auth.users.';

-- 2. ENABLE ROW LEVEL SECURITY
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;

-- 3. RLS POLICIES
DROP POLICY IF EXISTS "Users can view own profile" ON public.profiles;
CREATE POLICY "Users can view own profile"
  ON public.profiles
  FOR SELECT
  TO authenticated
  USING (auth.uid() = id);

DROP POLICY IF EXISTS "Users can update own profile" ON public.profiles;
CREATE POLICY "Users can update own profile"
  ON public.profiles
  FOR UPDATE
  TO authenticated
  USING  (auth.uid() = id)
  WITH CHECK (auth.uid() = id);

DROP POLICY IF EXISTS "Users can insert own profile" ON public.profiles;
CREATE POLICY "Users can insert own profile"
  ON public.profiles
  FOR INSERT
  TO authenticated
  WITH CHECK (auth.uid() = id);

-- 4. AUTO-CREATE PROFILE ON SIGNUP
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = ''
AS $$
BEGIN
  INSERT INTO public.profiles (id, full_name, email, avatar_url)
  VALUES (
    NEW.id,
    COALESCE(
      NEW.raw_user_meta_data ->> 'full_name',
      NEW.raw_user_meta_data ->> 'name',
      ''
    ),
    COALESCE(
      NEW.raw_user_meta_data ->> 'email',
      NEW.email,
      ''
    ),
    COALESCE(
      NEW.raw_user_meta_data ->> 'avatar_url',
      NEW.raw_user_meta_data ->> 'picture',
      ''
    )
  );
  RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW
  EXECUTE FUNCTION public.handle_new_user();

-- 5. PROTECT ROLE COLUMN
CREATE OR REPLACE FUNCTION public.protect_role_column()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
  IF NEW.role IS DISTINCT FROM OLD.role THEN
    NEW.role := OLD.role;
  END IF;
  RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS on_profile_role_protect ON public.profiles;
CREATE TRIGGER on_profile_role_protect
  BEFORE UPDATE ON public.profiles
  FOR EACH ROW
  EXECUTE FUNCTION public.protect_role_column();

-- 6. AUTO-UPDATE updated_at
CREATE OR REPLACE FUNCTION public.set_updated_at()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS on_profile_updated ON public.profiles;
CREATE TRIGGER on_profile_updated
  BEFORE UPDATE ON public.profiles
  FOR EACH ROW
  EXECUTE FUNCTION public.set_updated_at();


-- ──────────────────────────────────────────────────────────────
-- PART 2: PREDICTIVE MAINTENANCE / ML ANOMALIES
-- ──────────────────────────────────────────────────────────────

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

-- 2. ENABLE RLS
ALTER TABLE public.telemetry_anomalies ENABLE ROW LEVEL SECURITY;

-- 3. RLS POLICIES
DROP POLICY IF EXISTS "Authenticated users can insert anomalies" ON public.telemetry_anomalies;
CREATE POLICY "Authenticated users can insert anomalies"
    ON public.telemetry_anomalies
    FOR INSERT
    TO authenticated
    WITH CHECK (true);

DROP POLICY IF EXISTS "Authenticated users can view anomalies" ON public.telemetry_anomalies;
CREATE POLICY "Authenticated users can view anomalies"
    ON public.telemetry_anomalies
    FOR SELECT
    TO authenticated
    USING (true);


-- ──────────────────────────────────────────────────────────────
-- PART 3: NASA CMAPSS HISTORICAL DATA
-- ──────────────────────────────────────────────────────────────

-- 1. NASA DATASET TABLE
CREATE TABLE IF NOT EXISTS public.nasa_cmapss_telemetry (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    dataset_id TEXT NOT NULL,
    unit INT NOT NULL,
    cycle INT NOT NULL,
    setting1 FLOAT,
    setting2 FLOAT,
    setting3 FLOAT,
    sensor_1 FLOAT,
    sensor_2 FLOAT,
    sensor_3 FLOAT,
    sensor_4 FLOAT,
    sensor_5 FLOAT,
    sensor_6 FLOAT,
    sensor_7 FLOAT,
    sensor_8 FLOAT,
    sensor_9 FLOAT,
    sensor_10 FLOAT,
    sensor_11 FLOAT,
    sensor_12 FLOAT,
    sensor_13 FLOAT,
    sensor_14 FLOAT,
    sensor_15 FLOAT,
    sensor_16 FLOAT,
    sensor_17 FLOAT,
    sensor_18 FLOAT,
    sensor_19 FLOAT,
    sensor_20 FLOAT,
    sensor_21 FLOAT
);

-- 2. ENABLE RLS
ALTER TABLE public.nasa_cmapss_telemetry ENABLE ROW LEVEL SECURITY;

-- 3. RLS POLICIES
DROP POLICY IF EXISTS "Authenticated users can view nasa data" ON public.nasa_cmapss_telemetry;
CREATE POLICY "Authenticated users can view nasa data"
    ON public.nasa_cmapss_telemetry
    FOR SELECT
    TO authenticated
    USING (true);

DROP POLICY IF EXISTS "Authenticated users can insert nasa data" ON public.nasa_cmapss_telemetry;
CREATE POLICY "Authenticated users can insert nasa data"
    ON public.nasa_cmapss_telemetry
    FOR INSERT
    TO authenticated
    WITH CHECK (true);

-- ✅ COMPLETE SETUP DONE
