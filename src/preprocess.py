import pandas as pd
from sklearn.preprocessing import LabelEncoder, MinMaxScaler

def preprocess_data(file_path):
    # Load the dataset
    df = pd.read_csv(file_path)

    # Handle missing values (if any)
    df.fillna(0, inplace=True)

    # Encode categorical features
    label_encoder_crop = LabelEncoder()
    label_encoder_growth = LabelEncoder()
    df['crop_type'] = label_encoder_crop.fit_transform(df['crop_type'])
    df['growth_state'] = label_encoder_growth.fit_transform(df['growth_state'])

    # Scale numerical features (excluding soil_features)
    scaler = MinMaxScaler()
    df[['soil_moisture', 'rain_probability', 'temperature']] = scaler.fit_transform(
        df[['soil_moisture', 'rain_probability', 'temperature']]
    )

    return df

if __name__ == "__main__":
    # Preprocess the dataset
    file_path = "../dataset/irrigation_dataset.csv"  # Replace with your dataset path
    clean_data = preprocess_data(file_path)

    # Save the cleaned dataset
    clean_data.to_csv("../dataset/cleaned_dataset.csv", index=False)
    print("Data preprocessing complete. Cleaned dataset saved.")
