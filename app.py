from pathlib import Path
import math
import warnings

from flask import Flask, jsonify, render_template_string, request
import joblib
import pandas as pd

# Patch for scikit-learn compatibility with older saved pipelines.
try:
    from sklearn.compose._column_transformer import _RemainderColsList
except ImportError:
    from sklearn.compose import _column_transformer

    class _RemainderColsList(list):
        pass

    _column_transformer._RemainderColsList = _RemainderColsList

warnings.filterwarnings("ignore", category=UserWarning)

app = Flask(__name__)
BASE_DIR = Path(__file__).resolve().parent
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

NUMERICAL_FIELDS = ["Age", "Annual_Income", "Years_Experience"]
CATEGORICAL_FIELDS = ["Education_Level", "City"]
REQUIRED_FIELDS = NUMERICAL_FIELDS + CATEGORICAL_FIELDS

PAGE = r"""
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Haven | Home Value Estimate</title>
    <style>
      :root {
        --ink: #172033;
        --muted: #667085;
        --line: #dce3ef;
        --paper: #ffffff;
        --canvas: #f3f6fb;
        --navy: #102a43;
        --blue: #2563eb;
        --blue-dark: #1d4ed8;
        --mint: #d9f6e8;
        --shadow: 0 20px 55px rgba(24, 48, 83, .14);
      }
      * { box-sizing: border-box; }
      body {
        margin: 0;
        color: var(--ink);
        background: var(--canvas);
        font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      }
      .topbar {
        display: flex; align-items: center; justify-content: space-between;
        padding: 20px clamp(24px, 6vw, 88px); background: var(--paper);
        border-bottom: 1px solid rgba(23, 32, 51, .06);
      }
      .brand { display: flex; gap: 10px; align-items: center; font-size: 20px; font-weight: 800; letter-spacing: -.5px; }
      .brand-mark { display: grid; place-items: center; height: 34px; width: 34px; border-radius: 10px; color: white; background: var(--blue); font-size: 17px; }
      .secure { color: var(--muted); font-size: 14px; }
      .secure::before { content: "●"; color: #18a957; font-size: 10px; padding-right: 7px; }
      main { max-width: 1120px; margin: 0 auto; padding: clamp(38px, 7vw, 84px) 24px; }
      .eyebrow { margin: 0 0 12px; color: var(--blue); font-size: 12px; font-weight: 800; letter-spacing: .13em; text-transform: uppercase; }
      h1 { max-width: 700px; margin: 0; color: var(--navy); font-size: clamp(36px, 5vw, 60px); line-height: 1.04; letter-spacing: -2.3px; }
      .intro { max-width: 600px; margin: 20px 0 38px; color: var(--muted); font-size: 17px; line-height: 1.65; }
      .layout { display: grid; grid-template-columns: minmax(0, 1.55fr) minmax(270px, .8fr); gap: 24px; align-items: start; }
      .card { background: var(--paper); border: 1px solid rgba(23, 32, 51, .06); border-radius: 20px; box-shadow: var(--shadow); }
      .form-card { padding: clamp(25px, 4vw, 40px); }
      .card-heading { display: flex; align-items: baseline; justify-content: space-between; gap: 12px; margin-bottom: 28px; }
      h2 { margin: 0; font-size: 20px; letter-spacing: -.4px; }
      .card-heading span { color: var(--muted); font-size: 13px; }
      .fields { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 21px 18px; }
      .field.full { grid-column: 1 / -1; }
      label { display: block; margin-bottom: 8px; font-size: 14px; font-weight: 700; }
      .hint { color: var(--muted); font-size: 12px; font-weight: 500; }
      input, select { width: 100%; appearance: none; border: 1px solid var(--line); border-radius: 10px; padding: 13px 14px; background: #fff; color: var(--ink); font: inherit; outline: none; transition: border-color .2s, box-shadow .2s; }
      input:focus, select:focus { border-color: var(--blue); box-shadow: 0 0 0 4px rgba(37, 99, 235, .12); }
      .actions { display: flex; align-items: center; justify-content: space-between; gap: 18px; margin-top: 32px; }
      .privacy { margin: 0; max-width: 260px; color: var(--muted); font-size: 12px; line-height: 1.5; }
      button { min-width: 175px; border: 0; border-radius: 10px; padding: 14px 18px; cursor: pointer; color: white; background: var(--blue); box-shadow: 0 8px 18px rgba(37, 99, 235, .23); font: 700 15px inherit; transition: background .2s, transform .2s; }
      button:hover { background: var(--blue-dark); transform: translateY(-1px); }
      button:disabled { cursor: wait; opacity: .7; transform: none; }
      .result-card { min-height: 310px; overflow: hidden; padding: 30px; color: white; background: var(--navy); position: relative; }
      .result-card::after { content: ""; position: absolute; right: -65px; bottom: -85px; width: 240px; height: 240px; border-radius: 50%; background: rgba(88, 174, 255, .18); }
      .result-card .eyebrow { color: #9ac5ff; }
      .empty-state { position: relative; z-index: 1; margin-top: 40px; }
      .home-icon { display: grid; place-items: center; width: 46px; height: 46px; margin-bottom: 20px; border-radius: 14px; background: rgba(255,255,255,.12); font-size: 22px; }
      .empty-state p { max-width: 220px; margin: 0; color: #c8d3e1; line-height: 1.6; font-size: 14px; }
      .estimate { position: relative; z-index: 1; display: none; margin-top: 40px; }
      .estimate-label { color: #b7c9dc; font-size: 14px; }
      .estimate-value { margin: 8px 0 11px; font-size: clamp(35px, 4vw, 49px); font-weight: 800; letter-spacing: -1.7px; }
      .estimate-note { margin: 0; color: #b7c9dc; font-size: 13px; line-height: 1.55; }
      .error { display: none; margin: 20px 0 0; padding: 11px 13px; border-radius: 9px; color: #a61b1b; background: #fff0f0; font-size: 13px; }
      .footer { margin-top: 28px; color: var(--muted); font-size: 12px; text-align: center; }
      @media (max-width: 760px) {
        .topbar { padding: 18px 24px; } .secure { display: none; }
        .layout { grid-template-columns: 1fr; } .fields { grid-template-columns: 1fr; }
        .field.full { grid-column: auto; } .actions { align-items: stretch; flex-direction: column-reverse; }
        button { width: 100%; } .privacy { max-width: none; }
      }
    </style>
  </head>
  <body>
    <header class="topbar">
      <div class="brand"><span class="brand-mark">⌂</span>Haven</div>
      <div class="secure">Private estimate</div>
    </header>
    <main>
      <p class="eyebrow">Home value intelligence</p>
      <h1>Get a clearer view of your home’s value.</h1>
      <p class="intro">Share a few details and receive an instant, data-informed price estimate tailored to your profile.</p>
      <div class="layout">
        <section class="card form-card">
          <div class="card-heading"><h2>Your details</h2><span>All fields are required</span></div>
          <form id="prediction-form">
            <div class="fields">
              <div class="field"><label for="age">Age <span class="hint">(years)</span></label><input id="age" type="number" min="0" step="1" value="35" required></div>
              <div class="field"><label for="income">Annual income <span class="hint">(USD)</span></label><input id="income" type="number" min="0" step="any" value="65000" required></div>
              <div class="field"><label for="experience">Work experience <span class="hint">(years)</span></label><input id="experience" type="number" min="0" step="any" value="10" required></div>
              <div class="field"><label for="education">Education level</label><select id="education" required><option>High School</option><option selected>Bachelor</option><option>Master</option><option>PhD</option></select></div>
              <div class="field full"><label for="city">City</label><input id="city" type="text" value="New York" placeholder="e.g. New York" required></div>
            </div>
            <p id="error" class="error" role="alert"></p>
            <div class="actions"><p class="privacy">Your information is used only to calculate this estimate.</p><button id="submit" type="submit">Get my estimate</button></div>
          </form>
        </section>
        <aside class="card result-card" aria-live="polite">
          <p class="eyebrow">Your estimate</p>
          <div id="empty" class="empty-state"><div class="home-icon">⌂</div><p>Complete the form to see your estimated home price.</p></div>
          <div id="estimate" class="estimate"><div class="estimate-label">Estimated house price</div><div id="estimate-value" class="estimate-value">$0</div><p class="estimate-note">This automated estimate is a starting point, not a formal appraisal.</p></div>
        </aside>
      </div>
      <p class="footer">© 2026 Haven. Estimates are generated from the trained pricing model.</p>
    </main>
    <script>
      const form = document.getElementById('prediction-form');
      const button = document.getElementById('submit');
      const error = document.getElementById('error');
      const empty = document.getElementById('empty');
      const estimate = document.getElementById('estimate');
      const estimateValue = document.getElementById('estimate-value');
      form.addEventListener('submit', async (event) => {
        event.preventDefault(); error.style.display = 'none';
        button.disabled = true; button.textContent = 'Calculating…';
        const payload = {
          Age: document.getElementById('age').value,
          Annual_Income: document.getElementById('income').value,
          Years_Experience: document.getElementById('experience').value,
          Education_Level: document.getElementById('education').value,
          City: document.getElementById('city').value
        };
        try {
          const response = await fetch('/predict', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(payload)});
          const data = await response.json();
          if (!response.ok) throw new Error(data.error || 'Unable to calculate an estimate.');
          estimateValue.textContent = new Intl.NumberFormat('en-US', {style: 'currency', currency: 'USD', maximumFractionDigits: 0}).format(data.predicted_house_price);
          empty.style.display = 'none'; estimate.style.display = 'block';
        } catch (err) { error.textContent = err.message; error.style.display = 'block'; }
        finally { button.disabled = false; button.textContent = 'Get my estimate'; }
      });
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
        prediction = float(model.predict(input_df)[0])
        return jsonify(predicted_house_price=round(prediction, 2)), 200
    except ValueError as exc:
        return jsonify(error=str(exc)), 400
    except Exception:
        app.logger.exception("Prediction failed")
        return jsonify(error="Unable to generate a prediction."), 500


if __name__ == "__main__":
    app.run(debug=False, use_reloader=False)
