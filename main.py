from pathlib import Path
import math
import pickle
import warnings
import sys

from flask import Flask, jsonify, render_template_string, request
import joblib
import pandas as pd

# Patch for sklearn compatibility
try:
    from sklearn.compose._column_transformer import _RemainderColsList
except ImportError:
    # Define the missing class for backward compatibility
    from sklearn.compose import _column_transformer
    class _RemainderColsList(list):
        pass
    _column_transformer._RemainderColsList = _RemainderColsList

# Suppress sklearn version warnings
warnings.filterwarnings('ignore', category=UserWarning)

app = Flask(__name__)
BASE_DIR = Path(__file__).resolve().parent

# Model files are stored in the model/ directory
MODEL_PATH = BASE_DIR / "model" / "final_housing_price_model.pkl"
SCALER_PATH = BASE_DIR / "model" / "housing_standard_scaler.joblib"

try:
    model = joblib.load(MODEL_PATH)
    scaler = joblib.load(SCALER_PATH)
except FileNotFoundError as exc:
    raise RuntimeError(
        "Model files were not found. Place final_housing_price_model.pkl and "
        "housing_standard_scaler.joblib in the model/ directory."
    ) from exc


# These fields match the housing dataset used for training.
NUMERICAL_FIELDS = ["Age", "Annual_Income", "Years_Experience"]
CATEGORICAL_FIELDS = ["Education_Level", "City"]
REQUIRED_FIELDS = NUMERICAL_FIELDS + CATEGORICAL_FIELDS

PAGE = """
<!doctype html>
<html>
  <head><title>Housing Price Predictor</title></head>
  <body>
    <h1>Housing Price Predictor</h1>
    <p>Enter a JSON object, then select Predict.</p>
    <textarea id="payload" rows="12" cols="60">{
  "Age": 35,
  "Annual_Income": 65000,
  "Years_Experience": 10,
  "Education_Level": "Bachelor",
  "City": "New York"
}</textarea><br><br>
    <button onclick="predictPrice()">Predict</button>
    <pre id="result"></pre>
    <script>
      async function predictPrice() {
        const result = document.getElementById('result');
        try {
          const payload = JSON.parse(document.getElementById('payload').value);
          const response = await fetch('/predict', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(payload)
          });
          result.textContent = JSON.stringify(await response.json(), null, 2);
        } catch (error) {
          result.textContent = 'Invalid JSON: ' + error.message;
        }
      }
    </script>
  </body>
</html>
"""


def validate_and_prepare(payload):
    """Validate JSON data and return a one-row DataFrame for the model."""
    if not isinstance(payload, dict):
        raise ValueError("The JSON body must be an object.")

    missing_fields = [field for field in REQUIRED_FIELDS if field not in payload]
    if missing_fields:
        raise ValueError(f"Missing required field(s): {', '.join(missing_fields)}.")

    cleaned = {}
    for field in NUMERICAL_FIELDS:
        try:
            value = float(payload[field])
        except (TypeError, ValueError):
            raise ValueError(f"'{field}' must be a valid number.")
        if not math.isfinite(value):
            raise ValueError(f"'{field}' must be a finite number.")
        cleaned[field] = value

    for field in CATEGORICAL_FIELDS:
        value = payload[field]
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"'{field}' must be a non-empty text value.")
        cleaned[field] = value.strip()

    return pd.DataFrame([cleaned], columns=REQUIRED_FIELDS)


@app.get("/")
def home():
    return render_template_string(PAGE)


@app.post("/predict")
def predict():
    try:
        payload = request.get_json(silent=True)
        if payload is None:
            return jsonify(error="Send a valid JSON request body."), 400

        input_df = validate_and_prepare(payload)

        # The saved best_model is a scikit-learn Pipeline. Its preprocessor
        # applies the fitted StandardScaler and OneHotEncoder before predicting.
        # `scaler` is loaded at startup as required, but is not applied again:
        # transforming twice would produce an incorrect prediction.
        prediction = float(model.predict(input_df)[0])

        return jsonify(predicted_house_price=round(prediction, 2)), 200

    except ValueError as exc:
        return jsonify(error=str(exc)), 400
    except Exception:
        app.logger.exception("Prediction failed")
        return jsonify(error="Unable to generate a prediction."), 500


if __name__ == "__main__":
    app.run(debug=True)
