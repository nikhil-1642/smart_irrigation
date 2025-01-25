from flask import Flask, request, jsonify, render_template
import joblib

# Initialize the Flask app
app = Flask(__name__, template_folder="templates")

# Load the trained model
model = joblib.load("models/irrigation_model.pkl")

# Route to serve the HTML form
@app.route('/')
def home():
    return render_template("index.html")

# Route for predictions
@app.route('/predict', methods=['POST'])
def predict():
    try:
        # Get JSON data from the request
        data = request.json
        
        # Extract features
        soil_moisture = data.get('soil_moisture')
        crop_type = data.get('crop_type')
        rain_probability = data.get('rain_probability')
        growth_state = data.get('growth_state')
        
        # Ensure all inputs are provided
        if None in [soil_moisture, crop_type, rain_probability, growth_state]:
            return jsonify({"error": "All fields are required!"}), 400
        
        # Prepare the feature vector
        example_features = [soil_moisture, crop_type, rain_probability, growth_state]
        
        # Predict using the loaded model
        prediction = model.predict([example_features])
        water_level, flow_rate, irrigation_duration = prediction[0]
        
        # Return the predictions
        return jsonify({
            "water_level": water_level,
            "flow_rate": flow_rate,
            "irrigation_duration": irrigation_duration
        })
    except Exception as e:
        # Handle errors and return a message
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
