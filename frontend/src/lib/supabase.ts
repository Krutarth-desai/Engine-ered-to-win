import { createClient } from "@supabase/supabase-js";

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL || "https://gpelojjclxyypvxelhat.supabase.co";
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImdwZWxvampjbHh5eXB2eGVsaGF0Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODgxOTEwMTEsImV4cCI6MjEwMzc2NzAxMX0.4iurCAi_Z4O8b8qYfBzfiDnRN4zEuXvV9R5XcFNh020";

export const supabase = createClient(supabaseUrl, supabaseAnonKey);
