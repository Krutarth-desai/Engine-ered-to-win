import os
import json
import pickle
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler, MinMaxScaler

# Standard CMAPSS column names
COL_NAMES = ['unit', 'cycle', 'op_setting_1', 'op_setting_2', 'op_setting_3'] + \
            [f'sensor_{i}' for i in range(1, 22)]

def load_and_validate(dataset_name, data_dir="data"):
    """
    Loads train, test, and RUL data for the given CMAPSS dataset.
    Returns (train_df, test_df)
    """
    # 1. Load data
    train_path = os.path.join(data_dir, dataset_name, f"train_{dataset_name}.txt")
    test_path = os.path.join(data_dir, dataset_name, f"test_{dataset_name}.txt")
    rul_path = os.path.join(data_dir, dataset_name, f"RUL_{dataset_name}.txt")
    
    # Check if we reorganized it into HPC_Degradation and HPC_and_Fan_Degradation
    if dataset_name in ["FD001", "FD002"]:
        folder = "HPC_Degradation"
    else:
        folder = "HPC_and_Fan_Degradation"
        
    alt_train_path = os.path.join(data_dir, folder, f"train_{dataset_name}.txt")
    if os.path.exists(alt_train_path):
        train_path = alt_train_path
        test_path = os.path.join(data_dir, folder, f"test_{dataset_name}.txt")
        rul_path = os.path.join(data_dir, folder, f"RUL_{dataset_name}.txt")
    
    train_df = pd.read_csv(train_path, sep=r'\s+', header=None)
    test_df = pd.read_csv(test_path, sep=r'\s+', header=None)
    rul_df = pd.read_csv(rul_path, sep=r'\s+', header=None, names=['true_rul'])
    
    # Drop trailing NaN columns (due to trailing spaces)
    train_df.dropna(axis=1, how='all', inplace=True)
    test_df.dropna(axis=1, how='all', inplace=True)
    
    train_df.columns = COL_NAMES
    test_df.columns = COL_NAMES
    
    # Force float for op settings and sensors to avoid LossySetitemError during scaling
    float_cols = [c for c in COL_NAMES if c not in ['unit', 'cycle']]
    train_df[float_cols] = train_df[float_cols].astype(float)
    test_df[float_cols] = test_df[float_cols].astype(float)
    
    print(f"[{dataset_name}] Train shape: {train_df.shape}, Test shape: {test_df.shape}")
    print(f"[{dataset_name}] Train missing values: {train_df.isna().sum().sum()}")
    print(f"[{dataset_name}] Test missing values: {test_df.isna().sum().sum()}")
    assert train_df.isna().sum().sum() == 0, "Unexpected NaNs in train"
    assert test_df.isna().sum().sum() == 0, "Unexpected NaNs in test"
    
    # 2. RUL Computation
    R_EARLY = 125
    
    # Train RUL
    train_max = train_df.groupby('unit')['cycle'].max().reset_index()
    train_max.rename(columns={'cycle': 'max_cycle'}, inplace=True)
    train_df = train_df.merge(train_max, on='unit')
    train_df['RUL'] = train_df['max_cycle'] - train_df['cycle']
    train_df['RUL_clipped'] = train_df['RUL'].clip(upper=R_EARLY)
    train_df.drop(columns=['max_cycle'], inplace=True)
    
    # Test RUL
    test_max = test_df.groupby('unit')['cycle'].max().reset_index()
    test_max.rename(columns={'cycle': 'max_cycle'}, inplace=True)
    rul_df['unit'] = rul_df.index + 1
    test_max = test_max.merge(rul_df, on='unit')
    test_max['absolute_max_cycle'] = test_max['max_cycle'] + test_max['true_rul']
    
    test_df = test_df.merge(test_max[['unit', 'absolute_max_cycle']], on='unit')
    test_df['RUL'] = test_df['absolute_max_cycle'] - test_df['cycle']
    test_df['RUL_clipped'] = test_df['RUL'].clip(upper=R_EARLY)
    test_df.drop(columns=['absolute_max_cycle'], inplace=True)
    
    return train_df, test_df

def detect_flatline_sensors(df, threshold=1e-4):
    """Auto-detect near-zero-variance ('flatline') sensors."""
    sensors = [c for c in df.columns if c.startswith('sensor_')]
    stds = df[sensors].std()
    flatlines = stds[stds < threshold].index.tolist()
    return flatlines

def handle_operating_regimes(train_df, test_df):
    """
    Detects distinct operating regimes via KMeans.
    Normalizes sensors within each regime.
    """
    # Detect number of distinct regimes using op_setting_1
    n_regimes = train_df['op_setting_1'].round(1).nunique()
    print(f"Detected {n_regimes} operating regimes.")
    
    kmeans = KMeans(n_clusters=n_regimes, random_state=42, n_init=10)
    op_cols = ['op_setting_1', 'op_setting_2', 'op_setting_3']
    
    train_df['regime_id'] = kmeans.fit_predict(train_df[op_cols])
    test_df['regime_id'] = kmeans.predict(test_df[op_cols])
    
    sensors = [c for c in train_df.columns if c.startswith('sensor_')]
    
    # Standard scale per regime
    scalers = {}
    for r in range(n_regimes):
        mask_tr = train_df['regime_id'] == r
        mask_te = test_df['regime_id'] == r
        
        scaler = StandardScaler()
        if mask_tr.sum() > 0:
            train_df.loc[mask_tr, sensors] = scaler.fit_transform(train_df.loc[mask_tr, sensors])
            if mask_te.sum() > 0:
                test_df.loc[mask_te, sensors] = scaler.transform(test_df.loc[mask_te, sensors])
            scalers[r] = scaler
            
    return train_df, test_df, kmeans, scalers

def feature_engineering(df, window=5):
    """
    Rolling window (mean, std, rate of change) computed per engine unit.
    """
    df = df.sort_values(['unit', 'cycle'])
    sensors = [c for c in df.columns if c.startswith('sensor_')]
    
    grouped = df.groupby('unit')[sensors]
    
    # Mean
    roll_mean = grouped.rolling(window, min_periods=1).mean().reset_index(level=0, drop=True)
    roll_mean.columns = [f"{c}_roll_mean" for c in sensors]
    
    # Std
    roll_std = grouped.rolling(window, min_periods=2).std().reset_index(level=0, drop=True)
    roll_std.fillna(0, inplace=True)
    roll_std.columns = [f"{c}_roll_std" for c in sensors]
    
    # Rate of change
    diff = grouped.diff(window-1).reset_index(level=0, drop=True) / (window - 1)
    diff_1 = grouped.diff(1).reset_index(level=0, drop=True)
    diff = diff.fillna(diff_1).fillna(0)
    diff.columns = [f"{c}_roc" for c in sensors]
    
    # Concat
    df = pd.concat([df, roll_mean, roll_std, diff], axis=1)
    return df

def fit_health_index_model(train_df, feature_cols):
    """
    Compute correlations, weights, and fit MinMaxScaler for the Health Index.
    """
    corrs = train_df[feature_cols].apply(lambda x: x.corr(train_df['RUL_clipped'])).fillna(0)
    
    weights_dict = {}
    signs_dict = {}
    total_abs_corr = corrs.abs().sum() or 1
        
    for feat in feature_cols:
        c = corrs[feat]
        signs_dict[feat] = 1 if c > 0 else -1
        weights_dict[feat] = abs(c) / total_abs_corr
        
    temp_df = train_df[feature_cols].copy()
    for feat in feature_cols:
        temp_df[feat] = temp_df[feat] * signs_dict[feat]
        
    scaler = MinMaxScaler(feature_range=(0, 1))
    scaler.fit(temp_df)

    # Weighted-averaging ~45 individually-scaled features regresses toward the
    # middle of [0,1] (most rows won't have every feature agree at once), so the
    # raw weighted sum rarely reaches the true extremes. Fit a second, final
    # rescale on the train-set weighted sum itself so the *output* HI actually
    # spans [0,1] as intended, rather than only the per-feature inputs.
    scaled_vals = scaler.transform(temp_df)
    scaled_df = pd.DataFrame(scaled_vals, columns=feature_cols, index=train_df.index)
    weights_series = pd.Series(weights_dict)
    raw_hi = (scaled_df * weights_series).sum(axis=1)
    hi_min, hi_max = float(raw_hi.min()), float(raw_hi.max())

    return {
        'weights': weights_dict,
        'signs': signs_dict,
        'scaler': scaler,
        'features': feature_cols,
        'hi_min': hi_min,
        'hi_max': hi_max,
    }

def compute_health_index(df, model, manual_weights=None):
    """
    Computes health index given raw/windowed df and the fitted model.
    """
    feature_cols = model['features']
    temp_df = df[feature_cols].copy()
    
    for feat in feature_cols:
        temp_df[feat] = temp_df[feat] * model['signs'][feat]
        
    scaled_vals = model['scaler'].transform(temp_df)
    scaled_df = pd.DataFrame(scaled_vals, columns=feature_cols, index=df.index)
    
    weights = manual_weights if manual_weights is not None else model['weights']
    
    hi = pd.Series(0.0, index=df.index)
    for feat in feature_cols:
        hi += scaled_df[feat] * weights[feat]

    # Rescale using the bounds fit on train (see fit_health_index_model) so the
    # index actually spans [0,1] instead of clustering near 0.5. Test/live rows
    # can fall slightly outside the train-observed range, hence the clip after.
    hi_min = model.get('hi_min', 0.0)
    hi_max = model.get('hi_max', 1.0)
    if hi_max > hi_min:
        hi = (hi - hi_min) / (hi_max - hi_min)

    return hi.clip(0, 1)

def process_dataset(dataset_name, data_dir="data", output_dir="data/processed", models_dir="models"):
    """
    Full pipeline execution for a single dataset.
    """
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(models_dir, exist_ok=True)
    
    train_df, test_df = load_and_validate(dataset_name, data_dir)
    
    flatlines = detect_flatline_sensors(train_df)
    print(f"[{dataset_name}] Dropping flatline sensors: {flatlines}")
    train_df.drop(columns=flatlines, inplace=True)
    test_df.drop(columns=flatlines, inplace=True)
    
    train_df, test_df, kmeans_model, regime_scalers = handle_operating_regimes(train_df, test_df)
    
    train_df = feature_engineering(train_df)
    test_df = feature_engineering(test_df)
    
    kept_sensors = [c for c in train_df.columns if c.startswith('sensor_') and not ('_roll_' in c or '_roc' in c)]
    roll_cols = [c for c in train_df.columns if '_roll_' in c or '_roc' in c]
    all_features = kept_sensors + roll_cols
    
    hi_model = fit_health_index_model(train_df, all_features)
    train_df['health_index'] = compute_health_index(train_df, hi_model)
    test_df['health_index'] = compute_health_index(test_df, hi_model)
    
    with open(os.path.join(models_dir, f"{dataset_name}_scaler.pkl"), "wb") as f:
        pickle.dump({'kmeans': kmeans_model, 'regime_scalers': regime_scalers, 'hi_scaler': hi_model['scaler'],
                     'hi_min': hi_model['hi_min'], 'hi_max': hi_model['hi_max']}, f)

    with open(os.path.join(models_dir, f"{dataset_name}_health_index_weights.json"), "w") as f:
        json.dump({'weights': hi_model['weights'], 'signs': hi_model['signs'],
                    'hi_min': hi_model['hi_min'], 'hi_max': hi_model['hi_max']}, f, indent=4)
        
    train_out = os.path.join(output_dir, f"train_{dataset_name}_processed")
    test_out = os.path.join(output_dir, f"test_{dataset_name}_processed")
    
    train_df.to_parquet(train_out + ".parquet", index=False)
    train_df.to_csv(train_out + ".csv", index=False)
    test_df.to_parquet(test_out + ".parquet", index=False)
    test_df.to_csv(test_out + ".csv", index=False)
    
    print(f"[{dataset_name}] Pipeline completed successfully.")
    print(f"Output rows - Train: {len(train_df)}, Test: {len(test_df)}")
    print(f"Health Index Range - Train: [{train_df['health_index'].min():.4f}, {train_df['health_index'].max():.4f}]")
    
    return train_df, test_df, hi_model

if __name__ == "__main__":
    process_dataset("FD001")
