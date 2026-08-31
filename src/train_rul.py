import os
import joblib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.callbacks import EarlyStopping

# Enable clean plots
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')

def main():
    print("--- Starting RUL LSTM Training Pipeline ---")
    
    # 1. Start with the dataset
    data_path = "data/HPC_Degradation/train_FD001.txt"
    if not os.path.exists(data_path):
        # Fallback to absolute path just in case
        data_path = "c:/Users/harsh/Downloads/Engine-ered-to-win-dataset/Engine-ered-to-win-dataset/data/HPC_Degradation/train_FD001.txt"
        
    print(f"Loading data from {data_path}...")
    df = pd.read_csv(data_path, sep=r'\s+', header=None)
    
    # Standard CMAPSS column names
    columns = ["unit", "cycle", "setting1", "setting2", "setting3"] + [f"sensor_{i}" for i in range(1, 22)]
    df.columns = columns
    
    print("Dataset shape:", df.shape)
    print("Columns:", list(df.columns))
    
    # 2. Generate the RUL target
    print("Generating RUL target...")
    max_cycle = df.groupby("unit")["cycle"].max()
    df["RUL"] = df["unit"].map(max_cycle) - df["cycle"]
    df["RUL_clipped"] = df["RUL"].clip(upper=125)
    
    # 3. Select input features
    sensor_cols = [col for col in df.columns if col.startswith("sensor_")]
    print("All sensor columns:", sensor_cols)
    
    # Remove sensors with no variation
    useful_sensors = [col for col in sensor_cols if df[col].nunique() > 1]
    print(f"Useful sensors (count={len(useful_sensors)}): {useful_sensors}")
    features = useful_sensors
    
    # 4. Split by engine unit first to prevent data leakage
    print("Splitting by engine unit...")
    units = df["unit"].unique()
    train_units, temp_units = train_test_split(units, test_size=0.30, random_state=42)
    val_units, test_units = train_test_split(temp_units, test_size=0.50, random_state=42)
    
    print(f"Train Units: {len(train_units)}, Val Units: {len(val_units)}, Test Units: {len(test_units)}")
    
    train_df = df[df["unit"].isin(train_units)].copy()
    val_df = df[df["unit"].isin(val_units)].copy()
    test_df = df[df["unit"].isin(test_units)].copy()
    
    # 5. Normalize sensor values
    print("Scaling sensor values...")
    scaler = MinMaxScaler()
    train_df[features] = scaler.fit_transform(train_df[features])
    val_df[features] = scaler.transform(val_df[features])
    test_df[features] = scaler.transform(test_df[features])
    
    # Save the scaler
    os.makedirs("models", exist_ok=True)
    scaler_path = "models/rul_scaler.pkl"
    joblib.dump(scaler, scaler_path)
    print(f"Saved scaler to {scaler_path}")
    
    # 6. Create time-series windows
    WINDOW_SIZE = 30
    print(f"Creating sequences (WINDOW_SIZE={WINDOW_SIZE})...")
    
    def create_sequences(data, features, window_size=30):
        X = []
        y = []
        for unit_id, unit_data in data.groupby("unit"):
            unit_data = unit_data.sort_values("cycle")
            sensor_values = unit_data[features].values
            rul_values = unit_data["RUL_clipped"].values
            
            # Predict the RUL at index i (cycle i+1, following the last window item at index i-1)
            for i in range(window_size, len(unit_data)):
                X.append(sensor_values[i-window_size:i])
                y.append(rul_values[i])
        return np.array(X), np.array(y)
        
    X_train, y_train = create_sequences(train_df, features, WINDOW_SIZE)
    X_val, y_val = create_sequences(val_df, features, WINDOW_SIZE)
    X_test, y_test = create_sequences(test_df, features, WINDOW_SIZE)
    
    print(f"Train sequences: X={X_train.shape}, y={y_train.shape}")
    print(f"Val sequences:   X={X_val.shape}, y={y_val.shape}")
    print(f"Test sequences:  X={X_test.shape}, y={y_test.shape}")
    
    # 7. Build the LSTM
    print("Building LSTM model...")
    model = Sequential([
        LSTM(128, return_sequences=True, input_shape=(X_train.shape[1], X_train.shape[2])),
        Dropout(0.2),
        LSTM(64),
        Dropout(0.2),
        Dense(32, activation="relu"),
        Dense(1)
    ])
    
    # 8. Compile the model
    print("Compiling model...")
    model.compile(optimizer="adam", loss="mse", metrics=["mae"])
    model.summary()
    
    # 9. Train with early stopping
    print("Starting training...")
    early_stop = EarlyStopping(monitor="val_loss", patience=7, restore_best_weights=True)
    
    history = model.fit(
        X_train, y_train,
        validation_data=(X_val, y_val),
        epochs=100,
        batch_size=64,
        callbacks=[early_stop],
        verbose=1
    )
    
    # 10. Predict RUL
    print("Running predictions on test set...")
    predicted_rul = model.predict(X_test).flatten()
    
    # 11. Evaluate model
    mae = mean_absolute_error(y_test, predicted_rul)
    rmse = np.sqrt(mean_squared_error(y_test, predicted_rul))
    r2 = r2_score(y_test, predicted_rul)
    
    print("\n--- Test Set Evaluation Results ---")
    print(f"MAE  : {mae:.4f} cycles")
    print(f"RMSE : {rmse:.4f} cycles")
    print(f"R²   : {r2:.4f}")
    print("-----------------------------------\n")
    
    # 12. Plot actual vs predicted RUL
    print("Generating evaluation plot...")
    plt.figure(figsize=(12, 6))
    plt.plot(y_test[:500], label="Actual RUL", color="dodgerblue", linewidth=1.5)
    plt.plot(predicted_rul[:500], label="Predicted RUL (LSTM)", color="crimson", linestyle="--", linewidth=1.5)
    plt.xlabel("Test Sample")
    plt.ylabel("RUL (Cycles)")
    plt.title("Actual vs Predicted RUL (Test Set subset)")
    plt.legend()
    
    os.makedirs("reports", exist_ok=True)
    plot_path = "reports/rul_evaluation.png"
    plt.savefig(plot_path, dpi=300)
    plt.close()
    print(f"Saved evaluation plot to {plot_path}")
    
    # 13. Save the trained model
    model_path = "models/rul_lstm.keras"
    model.save(model_path)
    print(f"Saved trained LSTM model to {model_path}")
    print("--- RUL LSTM Pipeline Completed Successfully ---")

if __name__ == "__main__":
    main()
