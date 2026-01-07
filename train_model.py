"""
Train a simple AI model to predict programming test marks (0-10)
from code/output features.  Produces ai_model.pkl for Flask app.
"""

import pandas as pd
import pickle
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score

# -----------------------------------------------------
# 1. Load dataset
# -----------------------------------------------------
print("📥 Loading ai_training_data.csv ...")
df = pd.read_csv("ai_training_data.csv")

# Basic sanity check
print(df.head())

X = df[["similarity_score", "keyword_ratio", "comment_ratio", "avg_line_length", "error_flag"]]
y = df["marks"]

# -----------------------------------------------------
# 2. Split into train/test
# -----------------------------------------------------
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# -----------------------------------------------------
# 3. Train Random Forest model
# -----------------------------------------------------
print("🧠 Training RandomForestRegressor ...")
model = RandomForestRegressor(n_estimators=120, max_depth=6, random_state=42)
model.fit(X_train, y_train)

# -----------------------------------------------------
# 4. Evaluate model
# -----------------------------------------------------
pred = model.predict(X_test)
mae = mean_absolute_error(y_test, pred)
r2 = r2_score(y_test, pred)

print(f"✅ Training complete!  MAE={mae:.2f},  R²={r2:.2f}")

# -----------------------------------------------------
# 5. Save model
# -----------------------------------------------------
with open("ai_model.pkl", "wb") as f:
    pickle.dump(model, f)

print("💾 Saved ai_model.pkl successfully.")

# -----------------------------------------------------
# 6. Quick sanity prediction
# -----------------------------------------------------
sample = [[0.9, 0.25, 0.05, 27, 0]]  # good code, no errors
print("🔍 Example prediction for sample:", model.predict(sample))
