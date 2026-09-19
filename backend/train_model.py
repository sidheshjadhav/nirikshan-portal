"""
Trains 3 models on the synthetic infra project dataset:
1. Delay regressor -> predicts delay_months
2. Cost overrun regressor -> predicts cost_overrun_pct
3. Risk classifier -> predicts risk_label (Low/Medium/High)
Saves models + encoders as .pkl files for the FastAPI backend to load.
"""
import pandas as pd
import numpy as np
import joblib
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, accuracy_score, f1_score

df = pd.read_csv("dataset.csv")

# ---- Feature engineering ----
cat_cols = ["sector", "state", "implementing_agency"]
encoders = {}
df_enc = df.copy()
for col in cat_cols:
    le = LabelEncoder()
    df_enc[col + "_enc"] = le.fit_transform(df_enc[col])
    encoders[col] = le

feature_cols = [
    "sector_enc", "state_enc", "implementing_agency_enc",
    "original_cost_crore", "planned_duration_months",
    "physical_progress_pct", "expenditure_pct", "fund_utilization_pct",
    "milestones_total", "milestones_completed"
]

X = df_enc[feature_cols]

# ---- Model 1: Delay prediction (regression, months) ----
y_delay = df_enc["delay_months"]
X_train, X_test, y_train, y_test = train_test_split(X, y_delay, test_size=0.2, random_state=42)
delay_model = RandomForestRegressor(n_estimators=200, max_depth=10, random_state=42)
delay_model.fit(X_train, y_train)
pred = delay_model.predict(X_test)
print(f"[Delay Model] MAE: {mean_absolute_error(y_test, pred):.2f} months")

# ---- Model 2: Cost overrun prediction (regression, %) ----
y_cost = df_enc["cost_overrun_pct"]
X_train, X_test, y_train, y_test = train_test_split(X, y_cost, test_size=0.2, random_state=42)
cost_model = RandomForestRegressor(n_estimators=200, max_depth=10, random_state=42)
cost_model.fit(X_train, y_train)
pred = cost_model.predict(X_test)
print(f"[Cost Overrun Model] MAE: {mean_absolute_error(y_test, pred):.2f}%")

# ---- Model 3: Risk classification (Low/Medium/High) ----
risk_le = LabelEncoder()
y_risk = risk_le.fit_transform(df_enc["risk_label"])
X_train, X_test, y_train, y_test = train_test_split(X, y_risk, test_size=0.2, random_state=42, stratify=y_risk)
risk_model = RandomForestClassifier(n_estimators=200, max_depth=10, random_state=42, class_weight="balanced")
risk_model.fit(X_train, y_train)
pred = risk_model.predict(X_test)
print(f"[Risk Model] Accuracy: {accuracy_score(y_test, pred):.2f}, F1(macro): {f1_score(y_test, pred, average='macro'):.2f}")

# ---- Feature importance (for explainability in the UI) ----
importances = dict(zip(feature_cols, risk_model.feature_importances_.round(3)))
print("Risk model feature importances:", importances)

# ---- Save everything ----
joblib.dump(delay_model, "models/delay_model.pkl")
joblib.dump(cost_model, "models/cost_model.pkl")
joblib.dump(risk_model, "models/risk_model.pkl")
joblib.dump(encoders, "models/encoders.pkl")
joblib.dump(risk_le, "models/risk_label_encoder.pkl")
joblib.dump(feature_cols, "models/feature_cols.pkl")
joblib.dump(importances, "models/feature_importances.pkl")

print("\nAll models saved to models/ directory.")
