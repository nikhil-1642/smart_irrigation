import pandas as pd
import joblib

# Load the trained model
model = joblib.load("../models/irrigation_model.pkl")

# Example input: Ensure 5 features are included (excluding soil_features)
example_features = [0.7, 1, 0.4, 2]  # Example values for soil_moisture, crop_type, rain_probability, temperature, growth_state

# Create a DataFrame with the correct feature names
input_df = pd.DataFrame(
    [example_features],
    columns=['soil_moisture', 'crop_type', 'rain_probability', 'growth_state']
)

# Predict water level, flow rate, and irrigation duration
prediction = model.predict(input_df)

# Print the predictions
print(f"Predicted Water Level: {prediction[0][0]}")
print(f"Predicted Flow Rate: {prediction[0][1]}")
print(f"Predicted Irrigation Duration: {prediction[0][2]}")
