import pandas as pd
import numpy as np
import joblib
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC

# Load dataset
df = pd.read_csv("asl_dataset.csv")

# Split features and labels
X = df.drop(columns=["label"]).values
y = df["label"].values

# Normalize data
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Train/test split
X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42)

# Train model (Support Vector Machine - SVM)
model = SVC(kernel="linear")
model.fit(X_train, y_train)

# Save model and scaler
joblib.dump(model, "models/asl_model.pkl")
joblib.dump(scaler, "models/scaler.pkl")

print("✅ Model trained and saved!")