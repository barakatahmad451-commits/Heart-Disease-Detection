from flask import Flask, render_template, request, jsonify
import pickle
import numpy as np
from datetime import datetime

# FIX: Added template_folder='.' so Flask finds index.html in the main folder
app = Flask(__name__, template_folder='.')

# Load model and preprocessing files
model = pickle.load(open('knn_model.pkl', 'rb'))
scaler = pickle.load(open('scaler.pkl', 'rb'))
features = pickle.load(open('feature_columns.pkl', 'rb'))

FEATURE_INFO = {
    'Age': {'range': '18-100', 'unit': 'years', 'description': 'Patient age', 'normal_min': 18, 'normal_max': 65},
    'Sex_M': {'range': 'M/F', 'unit': 'binary', 'description': 'Patient sex (1=Male, 0=Female)', 'category': True},
    'ChestPainType_ATA': {'range': '0-1', 'unit': 'type', 'description': 'Atypical angina (1=Yes)', 'category': True},
    'ChestPainType_NAP': {'range': '0-1', 'unit': 'type', 'description': 'Non-anginal pain (1=Yes)', 'category': True},
    'ChestPainType_TA': {'range': '0-1', 'unit': 'type', 'description': 'Typical angina (1=Yes)', 'category': True},
    'RestingBP': {'range': '90-200', 'unit': 'mmHg', 'description': 'Resting blood pressure', 'normal_min': 90, 'normal_max': 120},
    'Cholesterol': {'range': '100-400', 'unit': 'mg/dL', 'description': 'Serum cholesterol', 'normal_min': 0, 'normal_max': 200},
    'FastingBS': {'range': '0-1', 'unit': 'binary', 'description': 'Fasting blood sugar > 120 mg/dL', 'category': True},
    'RestingECG_Normal': {'range': '0-1', 'unit': 'type', 'description': 'Resting ECG - Normal', 'category': True},
    'RestingECG_ST': {'range': '0-1', 'unit': 'type', 'description': 'Resting ECG - ST-T Abnormality', 'category': True},
    'MaxHR': {'range': '60-220', 'unit': 'bpm', 'description': 'Maximum heart rate achieved', 'normal_min': 120, 'normal_max': 200},
    'ExerciseAngina_Y': {'range': '0-1', 'unit': 'binary', 'description': 'Exercise induced angina (1=Yes)', 'category': True},
    'Oldpeak': {'range': '0-6.2', 'unit': 'mV', 'description': 'ST depression induced by exercise', 'normal_min': 0, 'normal_max': 1},
    'ST_Slope_Flat': {'range': '0-1', 'unit': 'type', 'description': 'ST segment slope - Flat (1=Yes)', 'category': True},
    'ST_Slope_Up': {'range': '0-1', 'unit': 'type', 'description': 'ST segment slope - Upsloping (1=Yes)', 'category': True},
}

@app.route('/')
def home():
    return render_template('index.html', features=features, feature_info=FEATURE_INFO)

@app.route('/predict', methods=['POST'])
def predict():
    try:
        values = []
        input_dict = {}

        for f in features:
            try:
                val = float(request.form.get(f, 0))
            except (ValueError, TypeError):
                val = 0
            values.append(val)
            input_dict[f] = val

        final_input = np.array(values).reshape(1, -1)
        final_input_scaled = scaler.transform(final_input)

        prediction = model.predict(final_input_scaled)[0]
        
        distances, indices = model.kneighbors(final_input_scaled)
        confidence = 1 - (distances[0].mean() / distances[0].max()) if distances[0].max() > 0 else 0.5
        confidence = min(100, max(0, confidence * 100))

        risk_score = calculate_risk_score(input_dict)

        result = "Heart Disease Detected" if prediction == 1 else "No Heart Disease Detected"

        return render_template(
            'index.html',
            features=features,
            feature_info=FEATURE_INFO,
            prediction=result,
            confidence=round(confidence, 1),
            risk_score=round(risk_score, 1),
            input_values=input_dict,
            timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        )
    except Exception as e:
        print(f"Error in predict: {str(e)}")
        return render_template(
            'index.html',
            features=features,
            feature_info=FEATURE_INFO,
            prediction="Error occurred during analysis"
        ), 400

def calculate_risk_score(input_dict):
    risk_score = 50
    if 'Age' in input_dict:
        age = input_dict['Age']
        if age > 65: risk_score += (age - 65) * 0.5
        elif age < 40: risk_score -= min(10, (40 - age) * 0.2)
    if 'RestingBP' in input_dict:
        bp = input_dict['RestingBP']
        if bp > 140: risk_score += (bp - 140) * 0.3
        elif bp < 90: risk_score += 10
    if 'Cholesterol' in input_dict:
        chol = input_dict['Cholesterol']
        if chol > 240: risk_score += (chol - 240) * 0.1
    if 'MaxHR' in input_dict:
        max_hr = input_dict['MaxHR']
        if max_hr < 100: risk_score += (100 - max_hr) * 0.2
        elif max_hr > 180: risk_score -= 5
    if 'Oldpeak' in input_dict:
        oldpeak = input_dict['Oldpeak']
        if oldpeak > 2: risk_score += oldpeak * 5
    return max(0, min(100, risk_score))

if __name__ == "__main__":
    app.run(debug=True)