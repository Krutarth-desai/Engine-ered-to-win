"use client";

import React from "react";
import { FeatureContribution } from "../types/telemetry";

interface FeatureContributionPanelProps {
  features: FeatureContribution[];
}

export default function FeatureContributionPanel({ features }: FeatureContributionPanelProps) {
  // Ensure we have sorted features
  const sortedFeatures = [...features].sort((a, b) => b.score - a.score);

  return (
    <div className="panel feature-contribution-panel">
      <div className="panel-header">
        <div className="panel-title">
          <span className="panel-icon">📊</span>
          TOP CONTRIBUTING FEATURES (EXPLAINABLE PHM)
        </div>
        <span className="explainable-badge">SHAP / GRADIENT ATTRIBUTION</span>
      </div>

      <div className="feature-columns-split">
        {/* Left: Feature Importance Bar Rankings */}
        <div className="feature-bars-list">
          {sortedFeatures.map((feat) => {
            const pct = Math.min(100, Math.max(8, feat.score * 320));
            const isTop = feat.score >= 0.18;

            return (
              <div key={feat.name} className="feature-bar-row">
                <div className="feature-info-line">
                  <span className="feat-name">
                    {feat.direction === "UP" && <span className="feat-arrow up">↑</span>}
                    {feat.direction === "DOWN" && <span className="feat-arrow down">↓</span>}
                    {feat.direction === "STABLE" && <span className="feat-arrow stable">→</span>}
                    {feat.name}
                  </span>
                  <span className="feat-score font-mono">
                    {feat.score.toFixed(3)}
                  </span>
                </div>

                <div className="feat-track">
                  <div
                    className={`feat-fill ${isTop ? "fill-top" : "fill-normal"}`}
                    style={{ width: `${pct}%` }}
                  />
                </div>
              </div>
            );
          })}
        </div>

        {/* Right: Feature Impact Diagnostic Guide */}
        <div className="feature-impact-guide">
          <div className="guide-title">
            <span className="guide-icon">💡</span>
            FEATURE IMPACT GUIDE
          </div>

          <div className="guide-items">
            <div className="guide-item">
              <span className="guide-bullet text-amber">↑ EGT + CHT</span>
              <span className="guide-arrow">→</span>
              <span className="guide-desc">increases cylinder &amp; valve thermal stress</span>
            </div>

            <div className="guide-item">
              <span className="guide-bullet text-pink">↑ Vibration</span>
              <span className="guide-arrow">→</span>
              <span className="guide-desc">indicates bearing &amp; mechanical train wear</span>
            </div>

            <div className="guide-item">
              <span className="guide-bullet text-cyan">↓ Oil Pressure</span>
              <span className="guide-arrow">→</span>
              <span className="guide-desc">indicates hydrodynamic lubrication breakdown</span>
            </div>

            <div className="guide-item guide-item-summary">
              <span className="guide-bullet text-red">Combined Multi-Stress</span>
              <span className="guide-arrow">→</span>
              <span className="guide-desc font-bold text-red">accelerates RUL decay curve</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
