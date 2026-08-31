# Feature Dictionary: CMAPSS Processed Dataset

This dictionary describes every output column in the `train_FD00X_processed.parquet` and `test_FD00X_processed.parquet` files.

| Column Name | Type | Source | Description | Imputation / Notes |
| :--- | :--- | :--- | :--- | :--- |
| `unit` | Integer | Raw | Engine unit ID | Sequential ID (1 to N). |
| `cycle` | Integer | Raw | Current operational cycle (time step) | Sorted in ascending order per unit. |
| `op_setting_1-3` | Float | Raw | The three operational settings | Not scaled globally, but used to determine the `regime_id`. |
| `sensor_[X]` | Float | Raw (Scaled) | Cleaned sensor readings | Zero-variance sensors (flatlines) are dropped. The remaining are MinMax scaled per operating regime. |
| `RUL` | Float | Derived | True Remaining Useful Life | `max(cycle) - current_cycle` (Train) or `true_rul + max(cycle) - current_cycle` (Test). |
| `RUL_clipped` | Float | Derived | Early-life clipped RUL | Clipped at `R_early = 125`. Early life is considered perfectly healthy. |
| `regime_id` | Integer | Derived | Operating Regime cluster ID | Generated via KMeans clustering on the 3 op settings. Used for regime-specific normalization. |
| `sensor_[X]_roll_mean` | Float | Derived | Rolling Mean of sensor X | Window size = 5. Computed per engine unit. Uses `min_periods=1` for early cycles. |
| `sensor_[X]_roll_std` | Float | Derived | Rolling Std Dev of sensor X | Window size = 5. Computed per engine unit. First cycle is filled with 0. |
| `sensor_[X]_roc` | Float | Derived | Rate of Change (Gradient) | Approximated as the diff over the window size divided by the window size. First cycle is 0. |
| `health_index` | Float | Derived | Composite Engine Health Score | Weighted combination of normalized features based on their correlation to `RUL_clipped`. Bounded to strictly [0.0, 1.0]. |

### Exported Artifacts
* **`models/FD00X_scaler.pkl`**: Contains the fitted KMeans model for operating regimes, the regime-specific `StandardScaler` instances, and the global `MinMaxScaler` for the health index.
* **`models/FD00X_health_index_weights.json`**: Contains the exact weights and sign-correction factors used to compute the health index.
