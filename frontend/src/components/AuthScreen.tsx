"use client";

import React, { useState } from "react";
import { supabase } from "@/lib/supabase";

interface AuthScreenProps {
  onAuthenticated: (user: any) => void;
}

export default function AuthScreen({ onAuthenticated }: AuthScreenProps) {
  const [isSignUpMode, setIsSignUpMode] = useState(false);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [errorMsg, setErrorMsg] = useState("");
  const [successMsg, setSuccessMsg] = useState("");
  const [loading, setLoading] = useState(false);

  const toggleAuthMode = () => {
    setIsSignUpMode((prev) => !prev);
    setErrorMsg("");
    setSuccessMsg("");
  };

  const handleAuthSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMsg("");
    setSuccessMsg("");
    setLoading(true);

    try {
      if (isSignUpMode) {
        const { data, error } = await supabase.auth.signUp({
          email: email.trim(),
          password: password,
        });
        if (error) throw error;

        if (data.user && data.user.identities && data.user.identities.length === 0) {
          setErrorMsg("An account with this email already exists.");
        } else if (data.session) {
          onAuthenticated(data.user);
        } else {
          setSuccessMsg("Account created! Check your email to confirm, then sign in.");
          setIsSignUpMode(false);
        }
      } else {
        const { data, error } = await supabase.auth.signInWithPassword({
          email: email.trim(),
          password: password,
        });
        if (error) throw error;
        if (data.user) {
          onAuthenticated(data.user);
        }
      }
    } catch (err: any) {
      setErrorMsg(err.message || "Authentication failed. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const handleGoogleSignIn = async () => {
    try {
      const { error } = await supabase.auth.signInWithOAuth({
        provider: "google",
        options: {
          redirectTo: typeof window !== "undefined" ? window.location.origin : undefined,
        },
      });
      if (error) {
        setErrorMsg(error.message || "Google sign-in failed.");
      }
    } catch (err: any) {
      setErrorMsg(err.message || "Google sign-in failed.");
    }
  };

  return (
    <div id="auth-screen">
      <div className="auth-card">
        <div className="auth-logo">
          <div className="logo-badge">AEROTWIN</div>
          <div className="auth-logo-subtitle">Operator Authentication Required</div>
        </div>
        <h2 id="auth-title"><strong>{isSignUpMode ? "Create Account" : "Sign In to GCS"}</strong></h2>
        
        {errorMsg && (
          <div className="auth-error" style={{ display: "block" }}>
            {errorMsg}
          </div>
        )}
        
        {successMsg && (
          <div className="auth-success" style={{ display: "block" }}>
            {successMsg}
          </div>
        )}

        <form onSubmit={handleAuthSubmit} autoComplete="on">
          <div className="auth-field">
            <label htmlFor="auth-email"><strong>Email</strong></label>
            <input
              type="email"
              id="auth-email"
              placeholder="operator@example.com"
              required
              autoComplete="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />
          </div>
          <div className="auth-field">
            <label htmlFor="auth-password"><strong>Password</strong></label>
            <input
              type="password"
              id="auth-password"
              placeholder="Enter your password"
              required
              autoComplete="current-password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
          </div>
          <button
            type="submit"
            className="auth-submit-btn"
            id="auth-submit-btn"
            disabled={loading}
          >
            {loading
              ? isSignUpMode
                ? "CREATING..."
                : "SIGNING IN..."
              : isSignUpMode
              ? "CREATE ACCOUNT"
              : "SIGN IN"}
          </button>
        </form>

        <div className="auth-divider">
          <span>or</span>
        </div>

        <button
          type="button"
          className="auth-google-btn"
          id="auth-google-btn"
          onClick={handleGoogleSignIn}
        >
          <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <path
              d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92a5.06 5.06 0 0 1-2.2 3.32v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.1z"
              fill="#4285F4"
            />
            <path
              d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
              fill="#34A853"
            />
            <path
              d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
              fill="#FBBC05"
            />
            <path
              d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
              fill="#EA4335"
            />
          </svg>
          Sign in with Google
        </button>

        <div className="auth-toggle">
          <span>{isSignUpMode ? "Already have an account?" : "Don't have an account?"}</span>{" "}
          <a onClick={toggleAuthMode}>{isSignUpMode ? "Sign In" : "Sign Up"}</a>
        </div>
      </div>
    </div>
  );
}
