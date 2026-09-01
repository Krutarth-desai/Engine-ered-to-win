# CMAPSS Exploratory Data Analysis (EDA) Summary

Based on the analysis of the NASA CMAPSS dataset (proxy for the MALE UAV aero piston engine):

1. **Proxy Justification**: Real piston-engine telemetry is unavailable, so we use the NASA CMAPSS turbofan dataset. While sensor semantics differ, the prognostics methodology (rolling-statistics, correlation-driven health scoring, RUL estimation) transfers directly to our digital twin architecture.
2. **Missing Values**: The CMAPSS dataset is clean. There are no missing values (NaNs) in the core telemetry matrices after removing trailing whitespace columns.
3. **Flatline Sensors**: Several sensors (e.g., sensors 1, 5, 10, 16, 18, 19 in FD001) exhibit near-zero variance. These are static operating parameters that provide no predictive value for degradation and are dropped automatically by our pipeline.
4. **Early-Life Distortions**: Engine degradation is barely perceptible in early operational cycles. We clipped the maximum Remaining Useful Life (RUL) to 125 cycles to prevent these flat early-life readings from distorting the health index and model training.
5. **Operating Regimes**: FD001 has a single operating condition, while other datasets (like FD002) have multiple regimes (six conditions). We handle this by clustering the 3 operational settings using KMeans and normalizing the sensors *within* each regime.
6. **Degradation Signals**: Sensors strongly correlated with RUL (both positively and negatively) show clear exponential or polynomial degradation trajectories in the final 30-50 cycles before failure.
7. **Health Index**: The composite Health Index aggregates the most highly correlated features into a single metric, with weighted-averaging results rescaled so the index truly spans [0, 1] on the training set (an earlier version clustered between ~0.66 and ~0.26 without this rescale). Validation plots confirm it trends from ~0.78 (early life) down to ~0.13 (near failure) across the fleet.
8. **Windowing Features**: Short rolling windows (size=5) for mean and variance effectively smooth sensor noise and capture the increasing signal instability that precedes mechanical failure.
