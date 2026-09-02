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
  manifold_pressure_bar: number;
  fuel_remaining_liters: number;
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
