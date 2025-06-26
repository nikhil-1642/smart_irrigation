from flask import Flask, request, jsonify, render_template, redirect, url_for
import joblib
import os
from twilio.rest import Client
from dotenv import load_dotenv

# Set new Twilio environment variables
os.environ['TWILIO_SID'] = 'ACc66877a8b6aac89ff43d16b7a464cd8a'
os.environ['TWILIO_TOKEN'] = '34e2328717ab6db33517e31a4b6bcc81'

# Initialize Flask app
app = Flask(__name__, template_folder="templates")

# Load environment variables from .env file (if used)
load_dotenv()

# Fetch Twilio credentials from environment
account_sid = os.environ.get('TWILIO_SID')
auth_token = os.environ.get('TWILIO_TOKEN')

# Twilio phone numbers
FROM_PHONE = '+18157064622'  # New Twilio number
TO_PHONE = '+919390286430'  # Verified recipient number

# Initialize Twilio client
twilio_client = Client(account_sid, auth_token)

# Load ML model
model = joblib.load("models/irrigation_model.pkl")

# Store last result in memory
last_result = {}

# Crop image mapping
CROP_IMAGES = {
    0: "https://th.bing.com/th/id/OSK.HEROaKdW7RE_8FY7hJnS7-ooHKGDnIfzqQBWaflbZNnmPVs?rs=1&pid=ImgDetMain",  # Wheat
    1: "https://th.bing.com/th/id/OSK.HEROLbGWcWlMjKDB2Geaet3buRLU-VqPCMkjm_OSK1v9a44?rs=1&pid=ImgDetMain",  # Corn
    2: "https://th.bing.com/th/id/OIP.AURbxhrt5_nfLbY80oZcegHaGo?w=480&h=430&rs=1&pid=ImgDetMain",           # Rice
    3: "https://th.bing.com/th/id/OSK.HERO1WrT3DU4pMlyrnZP26ylYzThkBl8giD3eI9e8fx8068?rs=1&pid=ImgDetMain",   # Soybean
    4: "https://th.bing.com/th/id/OSK.HERONsSodSiNLXSohgdk6Jo7yFF-PK1yNNuVWJrKyKz-h2E?rs=1&pid=ImgDetMain",   # Barley
}

# Function to make a call and speak an alert
def make_call_and_speak_alert(twilio_number, recipient_number, message):
    try:
        call = twilio_client.calls.create(
            to=recipient_number,
            from_=twilio_number,
            twiml=f'<Response><Say>{message}</Say></Response>'
        )
        print(f"Call initiated! Call SID: {call.sid}")
    except Exception as e:
        print(f"Failed to make the call: {str(e)}")

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/predict', methods=['POST'])
def predict():
    global last_result
    try:
        data = request.get_json()
        soil_moisture = data.get('soil_moisture')
        crop_type = int(data.get('crop_type', 0))
        rain_probability = data.get('rain_probability')
        growth_state = data.get('growth_state')

        # Input validation
        if None in [soil_moisture, crop_type, rain_probability, growth_state]:
            return jsonify({"error": "All fields are required!"}), 400

        # Case 1: Rain probability = 100%
        if rain_probability == 100:
            message = "Rain probability is 100%. Irrigation is not recommended at this time."
            sms = twilio_client.messages.create(body=message, from_=FROM_PHONE, to=TO_PHONE)
            make_call_and_speak_alert(FROM_PHONE, TO_PHONE, message)

            last_result = {
                "water_level": 0,
                "flow_rate": 0,
                "irrigation_duration": 0,
                "crop_image": CROP_IMAGES.get(crop_type),
                "sms_status": f"Message sent! SID: {sms.sid}",
                "call_status": f"Call initiated! SID: {sms.sid}",
                "note": "Irrigation not recommended due to 100% rain probability."
            }
            return jsonify(last_result)

        # Case 2: Soil moisture = 100%
        if soil_moisture == 100:
            message = "Soil moisture is at 100%. Irrigation not required at this time."
            sms = twilio_client.messages.create(body=message, from_=FROM_PHONE, to=TO_PHONE)
            make_call_and_speak_alert(FROM_PHONE, TO_PHONE, message)

            last_result = {
                "water_level": 0,
                "flow_rate": 0,
                "irrigation_duration": 0,
                "crop_image": CROP_IMAGES.get(crop_type),
                "sms_status": f"Message sent! SID: {sms.sid}",
                "call_status": f"Call initiated! SID: {sms.sid}",
                "note": "No irrigation performed due to 100% soil moisture."
            }
            return jsonify(last_result)

        # Predict with ML model
        features = [soil_moisture, crop_type, rain_probability, growth_state]
        prediction = model.predict([features])[0]
        water_level, flow_rate, irrigation_duration = prediction

        message_body = (
            f"Irrigation Prediction Results:\n"
            f"Water Level: {water_level:.4f}\n"
            f"Flow Rate: {flow_rate:.4f}\n"
            f"Irrigation Duration: {irrigation_duration:.4f} minutes"
        )

        sms = twilio_client.messages.create(body=message_body, from_=FROM_PHONE, to=TO_PHONE)
        make_call_and_speak_alert(FROM_PHONE, TO_PHONE, message_body)

        last_result = {
            "water_level": water_level,
            "flow_rate": flow_rate,
            "irrigation_duration": irrigation_duration,
            "crop_image": CROP_IMAGES.get(crop_type),
            "sms_status": f"Message sent! SID: {sms.sid}",
            "call_status": f"Call initiated! SID: {sms.sid}"
        }

        return jsonify(last_result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/stop_timer', methods=['POST'])
def stop_timer():
    try:
        message = "Your field was not irrigated, the bore was turned off."
        sms = twilio_client.messages.create(body=message, from_=FROM_PHONE, to=TO_PHONE)
        make_call_and_speak_alert(FROM_PHONE, TO_PHONE, message)
        return jsonify({
            "status": "Alert sent",
            "sms_status": f"Message sent! SID: {sms.sid}",
            "call_status": "Call initiated!"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/send_status_sms', methods=['POST'])
def send_status_sms():
    try:
        data = request.get_json()
        message = data.get("message", "Irrigation status update.")
        sms = twilio_client.messages.create(body=message, from_=FROM_PHONE, to=TO_PHONE)
        return jsonify({"status": "Message sent", "sid": sms.sid})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/result')
def result():
    if not last_result:
        return redirect(url_for('home'))
    return render_template("result.html", result=last_result)

if __name__ == '__main__':
    app.run(debug=True)
