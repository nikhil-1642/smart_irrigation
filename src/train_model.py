import pandas as pd
import joblib
from sklearn.ensemble import RandomForestRegressor
from sklearn.multioutput import MultiOutputRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error

# Load the preprocessed data
df = pd.read_csv("../dataset/cleaned_dataset.csv")

# Features and targets (excluding soil_features)
X = df[['soil_moisture', 'crop_type', 'rain_probability', 'growth_state']]
y = df[['water_level', 'flow_rate', 'irrigation_duration']]

# Split the data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train a multi-output model
model = MultiOutputRegressor(RandomForestRegressor(random_state=42))
model.fit(X_train, y_train)

# Evaluate the model
y_pred = model.predict(X_test)
mse = mean_squared_error(y_test, y_pred, multioutput='raw_values')
print(f"Mean Squared Errors: {mse}")

# Save the trained model
joblib.dump(model, "../models/irrigation_model.pkl")
print("Model saved to '../models/irrigation_model.pkl'")
