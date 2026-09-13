from pathlib import Path
import math

import joblib
import pandas as pd
import streamlit as st


BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "model" / "final_housing_price_model.pkl"
NUMERICAL_FIELDS = ["Age", "Annual_Income", "Years_Experience"]
EDUCATION_LEVELS = ["High School", "Bachelor", "Master", "PhD"]


@st.cache_resource
def load_model():
    if not MODEL_PATH.exists():
        raise FileNotFoundError(f"The model file was not found at {MODEL_PATH}.")
    return joblib.load(MODEL_PATH)


st.set_page_config(
    page_title="Haven | Home Value Estimate", page_icon="⌂", layout="centered"
)
st.title("Get a clearer view of your home's value.")
st.write("Share a few details and receive an instant, data-informed price estimate.")

with st.form("prediction_form"):
    age = st.number_input("Age (years)", min_value=0.0, value=35.0, step=1.0)
    annual_income = st.number_input(
        "Annual income (USD)", min_value=0.0, value=65000.0, step=1000.0
    )
    years_experience = st.number_input(
        "Work experience (years)", min_value=0.0, value=10.0, step=1.0
    )
    education_level = st.selectbox("Education level", EDUCATION_LEVELS, index=1)
    city = st.text_input("City", value="New York")
    submitted = st.form_submit_button("Get my estimate", type="primary")

if submitted:
    city = city.strip()
    values = [age, annual_income, years_experience]
    if not city:
        st.error("City must be a non-empty text value.")
    elif not all(math.isfinite(value) for value in values):
        st.error("Numeric values must be finite numbers.")
    else:
        try:
            model = load_model()
            input_df = pd.DataFrame(
                [
                    {
                        "Age": age,
                        "Annual_Income": annual_income,
                        "Years_Experience": years_experience,
                        "Education_Level": education_level,
                        "City": city,
                    }
                ],
                columns=NUMERICAL_FIELDS + ["Education_Level", "City"],
            )
            prediction = float(model.predict(input_df)[0])
            st.success(f"Estimated house price: ${prediction:,.0f}")
            st.caption(
                "This automated estimate is a starting point, not a formal appraisal."
            )
        except Exception:
            st.error("Unable to generate a prediction. Check that the model file is available.")
