-- ============================================================
-- AeroTwin | public.profiles table for Supabase Auth
-- ============================================================
-- This script creates a profiles table that mirrors auth.users,
-- automatically populates it on signup (including Google OAuth),
-- and locks it down with Row Level Security.
-- Safe to re-run — uses IF NOT EXISTS / OR REPLACE throughout.
-- ============================================================


-- ──────────────────────────────────────────────────────────────
-- 1. CREATE THE PROFILES TABLE
-- ──────────────────────────────────────────────────────────────

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


-- ──────────────────────────────────────────────────────────────
-- 2. ENABLE ROW LEVEL SECURITY
-- ──────────────────────────────────────────────────────────────

ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;


-- ──────────────────────────────────────────────────────────────
-- 3. RLS POLICIES
-- ──────────────────────────────────────────────────────────────

-- Users can read only their own profile
DROP POLICY IF EXISTS "Users can view own profile" ON public.profiles;
CREATE POLICY "Users can view own profile"
  ON public.profiles
  FOR SELECT
  TO authenticated
  USING (auth.uid() = id);

-- Users can update only their own profile
DROP POLICY IF EXISTS "Users can update own profile" ON public.profiles;
CREATE POLICY "Users can update own profile"
  ON public.profiles
  FOR UPDATE
  TO authenticated
  USING  (auth.uid() = id)
  WITH CHECK (auth.uid() = id);

-- Users can insert their own profile (needed for client-side upsert fallback)
DROP POLICY IF EXISTS "Users can insert own profile" ON public.profiles;
CREATE POLICY "Users can insert own profile"
  ON public.profiles
  FOR INSERT
  TO authenticated
  WITH CHECK (auth.uid() = id);


-- ──────────────────────────────────────────────────────────────
-- 4. AUTO-CREATE PROFILE ON SIGNUP (trigger on auth.users)
-- ──────────────────────────────────────────────────────────────

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


-- ──────────────────────────────────────────────────────────────
-- 5. PROTECT THE ROLE COLUMN FROM CLIENT-SIDE CHANGES
-- ──────────────────────────────────────────────────────────────

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


-- ──────────────────────────────────────────────────────────────
-- 6. AUTO-UPDATE updated_at ON ROW CHANGE
-- ──────────────────────────────────────────────────────────────

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


-- ✅ DONE
