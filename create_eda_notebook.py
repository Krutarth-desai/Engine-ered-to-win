import nbformat as nbf

nb = nbf.v4.new_notebook()

cells = []

# Title
cells.append(nbf.v4.new_markdown_cell(
"""# CMAPSS Data & Feature Engineering Pipeline
**SIH Problem Statement 54 (Team AeroTwin) - Person 1**

This notebook performs Exploratory Data Analysis (EDA) on the NASA CMAPSS turbofan degradation dataset (used here as a proxy for our MALE UAV aero piston engine). While sensor semantics differ, the prognostics methodology—rolling-statistics feature engineering, correlation-driven health scoring, and RUL estimation—transfers directly to the digital twin architecture.

This notebook uses the `src.health_pipeline` module so logic stays reusable."""
))

# Setup
cells.append(nbf.v4.new_code_cell(
"""import os
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Add src to path
sys.path.append(os.path.abspath('src'))
from health_pipeline import process_dataset, load_and_validate, detect_flatline_sensors

plt.style.use('seaborn-v0_8-whitegrid')"""
))

# Load Data
cells.append(nbf.v4.new_markdown_cell("## 1. Load Data & Validation\nLoading FD001. Our pipeline assigns 26 standard column names, computes RUL (clipped at 125 cycles early-life max to prevent distortion), and checks for missing values."))
cells.append(nbf.v4.new_code_cell(
"""train_df, test_df = load_and_validate('FD001', data_dir='data')
display(train_df.head())"""
))

# Flatlines
cells.append(nbf.v4.new_markdown_cell("## 2. Identify Near-Zero-Variance (Flatline) Sensors\nSensors that do not change over time offer no predictive value. We automatically detect and drop them."))
cells.append(nbf.v4.new_code_cell(
"""flatlines = detect_flatline_sensors(train_df)
print(f"Flatline sensors to drop: {flatlines}")
train_df.drop(columns=flatlines, inplace=True)
test_df.drop(columns=flatlines, inplace=True)"""
))

# Distributions
cells.append(nbf.v4.new_markdown_cell("## 3. Sensor Distributions\nLet's visualize the distribution of a few retained sensors to understand their ranges."))
cells.append(nbf.v4.new_code_cell(
"""sensors = [c for c in train_df.columns if c.startswith('sensor_')][:6]
fig, axes = plt.subplots(2, 3, figsize=(15, 8))
for i, ax in enumerate(axes.flatten()):
    if i < len(sensors):
        sns.histplot(train_df[sensors[i]], bins=30, kde=True, ax=ax)
        ax.set_title(f'Distribution of {sensors[i]}')
plt.tight_layout()
os.makedirs('reports/eda_plots', exist_ok=True)
plt.savefig('reports/eda_plots/sensor_distributions.png')
plt.show()"""
))

# Degradation
cells.append(nbf.v4.new_markdown_cell("## 4. Degradation Curves\nLet's look at how sensor 2 degrades over time for the first 5 engines. The color changes as it approaches failure (RUL = 0)."))
cells.append(nbf.v4.new_code_cell(
"""fig, ax = plt.subplots(figsize=(10, 6))
for unit_id in range(1, 6):
    unit_data = train_df[train_df['unit'] == unit_id]
    scatter = ax.scatter(unit_data['cycle'], unit_data['sensor_2'], 
                         c=unit_data['RUL_clipped'], cmap='viridis_r', alpha=0.7)

plt.colorbar(scatter, label='RUL (Clipped)')
plt.xlabel('Cycle (Time)')
plt.ylabel('Sensor 2 Value')
plt.title('Sensor 2 Degradation over Time (Units 1-5)')
plt.savefig('reports/eda_plots/degradation_curves.png')
plt.show()"""
))

# Correlation
cells.append(nbf.v4.new_markdown_cell("## 5. Correlation Heatmap\nWhich sensors are most correlated with the Remaining Useful Life (RUL)?"))
cells.append(nbf.v4.new_code_cell(
"""corr_cols = [c for c in train_df.columns if c.startswith('sensor_')] + ['RUL_clipped']
corr_matrix = train_df[corr_cols].corr()

plt.figure(figsize=(12, 10))
sns.heatmap(corr_matrix, annot=False, cmap='coolwarm', center=0)
plt.title('Sensor Correlation with RUL')
plt.savefig('reports/eda_plots/correlation_heatmap.png')
plt.show()

# Ranked Table
rul_corrs = corr_matrix['RUL_clipped'].drop('RUL_clipped').abs().sort_values(ascending=False)
display(rul_corrs.to_frame('Absolute Correlation with RUL'))"""
))

# Run Pipeline
cells.append(nbf.v4.new_markdown_cell("## 6. Run Full Pipeline\nNow we execute the reusable pipeline, which handles Operating Regimes (KMeans), Feature Engineering (Rolling stats), and computes the Health Index. It exports the dataset for downstream modeling."))
cells.append(nbf.v4.new_code_cell(
"""# Process FD001 completely
processed_train, processed_test, hi_model = process_dataset('FD001')"""
))

# Health Index Validation
cells.append(nbf.v4.new_markdown_cell("## 7. Health Index Validation\nThe Health Index should trend from ~1 (healthy) to 0 (failure). Let's plot the average Health Index vs. Normalized Life Percentage across all engines."))
cells.append(nbf.v4.new_code_cell(
"""# Normalize life percentage per unit
def assign_life_pct(df):
    max_cycles = df.groupby('unit')['cycle'].max()
    df = df.merge(max_cycles.rename('max_cycle'), on='unit')
    df['life_pct'] = (df['cycle'] / df['max_cycle']) * 100
    df.drop(columns='max_cycle', inplace=True)
    return df

processed_train = assign_life_pct(processed_train)

# Bin into 5% intervals
processed_train['life_pct_bin'] = (processed_train['life_pct'] // 5) * 5
hi_trend = processed_train.groupby('life_pct_bin')['health_index'].mean()

plt.figure(figsize=(8, 5))
plt.plot(hi_trend.index, hi_trend.values, marker='o', linewidth=2)
plt.xlabel('Life Percentage (%)')
plt.ylabel('Average Health Index [0-1]')
plt.title('Validation: Health Index vs Life Percentage')
plt.grid(True)
plt.savefig('reports/eda_plots/health_index_validation.png')
plt.show()"""
))

nb['cells'] = cells

with open('01_data_pipeline_eda.ipynb', 'w', encoding='utf-8') as f:
    nbf.write(nb, f)

print("Notebook generated successfully!")
