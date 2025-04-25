from flask import Flask, request, jsonify
import cv2
import mediapipe as mp
import numpy as np
import joblib

# Load trained model and scaler
model = joblib.load("models/asl_model.pkl")
scaler = joblib.load("models/scaler.pkl")

# Initialize MediaPipe Hands
mp_hands = mp.solutions.hands
app = Flask(__name__)

@app.route('/predict', methods=['POST'])
def predict():
    file = request.files['image']
    image = cv2.imdecode(np.frombuffer(file.read(), np.uint8), cv2.IMREAD_COLOR)

    with mp_hands.Hands(min_detection_confidence=0.5, min_tracking_confidence=0.5) as hands:
        results = hands.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                data = []
                for landmark in hand_landmarks.landmark:
                    data.append(landmark.x)
                    data.append(landmark.y)

                X_input = scaler.transform([data])
                prediction = model.predict(X_input)[0]
                return jsonify({"prediction": prediction})

    return jsonify({"error": "No hand detected"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)