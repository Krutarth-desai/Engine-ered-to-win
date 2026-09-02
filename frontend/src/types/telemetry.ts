export interface SensorDiagnosis {
  diagnosis_type: "NORMAL" | "POSSIBLE_SENSOR_FAILURE" | "POSSIBLE_ENGINE_FAILURE" | "UNKNOWN" | string;
  sensor_fault_confidence: number;
  engine_fault_confidence: number;
  persistence_count: number;
  suspected_sensor?: string | null;
  affected_sensors?: string[];
  sensor_scores?: Record<string, number>;
  evidence?: string;
}

export interface TelemetryData {
  timestamp: string;
  engine_id: string;
  rpm: number;
  cht_c: number;
  egt_c: number;
  oil_pressure_bar: number;
  oil_temperature_c: number;
  fuel_flow_lh: number;
  vibration_g: number;
  manifold_pressure_bar?: number;
  fuel_remaining_liters?: number;
  battery_voltage_v: number;
  injection_timing_deg: number;
  health_index: number;
  rul: number;
  fault_label: string;
  status?: string;
  severity?: string;
  fault?: string;
  evidence?: string;
  treatment?: string;
  prevention?: string;
  anomaly_score?: number;
  sensor_diagnosis?: SensorDiagnosis;
}

export interface RulTickData {
  type: "rul_tick";
  unit: number;
  cycle: number;
  actual_rul: number;
  predicted_rul: number | null;
}

export interface RulEngineListMsg {
  type: "engine_list";
  units: number[];
}

export interface RulResetMsg {
  type: "reset";
  unit: number;
}

export interface SensorItem {
  key: string;
  name: string;
  value: number;
  unit: string;
  min: number;
  max: number;
  status: "NORMAL" | "CAUTION" | "ALERT";
  trend: "UP" | "DOWN" | "STABLE";
  progressPct: number;
}

export interface PrognosticsData {
  predicted_rul: number;
  actual_rul: number;
  remaining_time_str: string;
  current_cycle: number;
  max_useful_life: number;
  rul_unclipped: number;
  rul_clipped: number;
  degradation_trend: "Increasing" | "Stable" | "Accelerating" | "Decreasing";
  confidence: number;
  abs_error: number;
  model_mae: number;
  window_size: number;
  sensor_count: number;
}

export interface RiskData {
  level: "LOW" | "MEDIUM" | "HIGH" | "CRITICAL";
  anomaly: "NORMAL" | "CAUTION" | "ALERT";
  action: string;
  status_label?: string;
  guidance?: string;
}

export interface FeatureContribution {
  name: string;
  score: number; // 0.0 to 1.0
  impact: string;
  direction: "UP" | "DOWN" | "STABLE";
}

export interface TrendHistoryPoint {
  cycle: number;
  egt: number;
  oil_pressure: number;
  vibration: number;
  health_index: number;
}

export interface TrajectoryPoint {
  cycle: number;
  actual_rul: number;
  predicted_rul: number;
}

export interface PhmAlertItem {
  id: string;
  level: "NORMAL" | "INFO" | "CAUTION" | "ALERT";
  title: string;
  message: string;
  time_ago: string;
  timestamp: string;
}

export interface UnifiedTelemetryPayload {
  cycle: number;
  timestamp: string;
  vehicle: {
    vehicle_id: string;
    mission_id: string;
    altitude: number;
    throttle: number;
    update_rate: number;
  };
  sensors: Record<string, SensorItem>;
  sensor_list: SensorItem[];
  prognostics: PrognosticsData;
  health_index: number;
  risk: RiskData;
  contributing_features: FeatureContribution[];
  recent_trends: {
    points: TrendHistoryPoint[];
    deltas: {
      egt_delta: number;
      oil_pressure_delta: number;
      vibration_delta: number;
      health_delta: number;
    };
  };
  trajectory: TrajectoryPoint[];
  alerts: PhmAlertItem[];
  fault_label: string;
  scenario: string;
  sensor_diagnosis?: SensorDiagnosis;
  rpm?: number;
  cht_c?: number;
  egt_c?: number;
  oil_pressure_bar?: number;
  oil_temperature_c?: number;
  fuel_flow_lh?: number;
  vibration_g?: number;
  battery_voltage_v?: number;
  injection_timing_deg?: number;
}
