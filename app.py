import streamlit as st
import os
from groq import Groq

st.set_page_config(page_title="NutriPlan AI", page_icon="🥗", layout="wide")

st.title("🥗 NutriPlan AI")
st.subheader("AI-Powered Personalized Nutrition Planner")

st.write(
    "NutriPlan AI analyzes personal information, health conditions, "
    "laboratory information, food preferences, activity level and budget "
    "to suggest a nutrition goal and create a personalized meal plan."
)

st.warning(
    "This application provides AI-generated educational nutrition guidance. "
    "It does not diagnose diseases or replace a doctor or registered dietitian."
)

try:
    api_key = st.secrets["GROQ_API_KEY"]
except Exception:
    api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    st.error("Groq API key was not found. Add GROQ_API_KEY to Streamlit Secrets.")
    st.stop()

client = Groq(api_key=api_key)

st.header("👤 Personal Information")
col1, col2, col3 = st.columns(3)

with col1:
    age = st.number_input("Age", min_value=1, max_value=120, value=25)
with col2:
    height = st.number_input("Height (cm)", min_value=50.0, max_value=250.0, value=170.0)
with col3:
    weight = st.number_input("Weight (kg)", min_value=10.0, max_value=300.0, value=70.0)

gender = st.selectbox("Gender", ["Male", "Female", "Prefer not to say"])
activity_level = st.selectbox(
    "Activity Level",
    ["Sedentary", "Lightly Active", "Moderately Active", "Very Active"]
)

def calculate_bmi(height_cm, weight_kg):
    height_m = height_cm / 100
    if height_m <= 0:
        return 0
    return weight_kg / (height_m ** 2)

bmi = calculate_bmi(height, weight)
st.metric("BMI", f"{bmi:.1f}")
st.caption("BMI is a screening measure and should not be used alone to determine a person's health or nutrition goal.")

st.header("🩺 Health Information")
disease = st.multiselect(
    "Select health conditions",
    [
        "None", "Type 2 diabetes", "High blood pressure",
        "High cholesterol", "Anemia", "PCOS", "Kidney disease",
        "Liver disease", "Heart disease", "Thyroid condition", "Other"
    ],
)

other_condition = ""
if "Other" in disease:
    other_condition = st.text_input("Enter other health condition")

additional_health = st.text_area(
    "Additional health information",
    placeholder="Enter any other relevant health information."
)

st.header("🧪 Blood / Laboratory Report")
uploaded_report = st.file_uploader(
    "Upload your laboratory report",
    type=["txt", "pdf", "png", "jpg", "jpeg"],
)

report_text = ""

if uploaded_report:
    file_name = uploaded_report.name.lower()

    if file_name.endswith(".txt"):
        report_text = uploaded_report.getvalue().decode("utf-8", errors="ignore")
        st.success("Text report uploaded successfully.")
        with st.expander("View report"):
            st.text(report_text)

    elif file_name.endswith(".pdf"):
        st.success("PDF uploaded successfully.")
        st.info("This first version does not automatically extract values from PDFs. Enter important laboratory values below.")
        report_text = st.text_area(
            "Enter laboratory values",
            placeholder="""Example:
Hb: 11.2 g/dL
Fasting glucose: 120 mg/dL
Total cholesterol: 210 mg/dL""",
        )

    elif file_name.endswith((".png", ".jpg", ".jpeg")):
        st.success("Report image uploaded successfully.")
        st.image(uploaded_report, caption="Uploaded Report")
        report_text = st.text_area(
            "Enter laboratory values from the report",
            placeholder="""Example:
Hb: 11.2 g/dL
Fasting glucose: 120 mg/dL
Total cholesterol: 210 mg/dL""",
        )

st.header("🍽️ Food Preferences")
diet_type = st.selectbox(
    "Diet Type",
    ["No specific preference", "Vegetarian", "Non-vegetarian", "Vegan"],
)
favorite_foods = st.text_area("Foods you like", placeholder="Example: chicken, daal, rice, roti, eggs")
disliked_foods = st.text_area("Foods you dislike", placeholder="Example: fish, spinach")
allergies = st.text_area("Food allergies / intolerances", placeholder="Example: peanuts, lactose, gluten")

st.header("🍴 Meal Schedule")
number_of_meals = st.slider("Number of meals per day", min_value=2, max_value=6, value=3)

st.header("💰 Budget")
budget = st.selectbox("Daily food budget", ["Low budget", "Moderate budget", "Flexible budget"])
location = st.text_input("Country / Region", value="Pakistan")

def analyze_health():
    conditions = ", ".join(disease)

    prompt = f"""
You are an AI-assisted nutrition planning system.

Analyze the user's provided health information, body measurements,
activity level, laboratory information, food preferences and budget.

Recommend ONE general nutrition goal:
1. Weight loss
2. Weight gain
3. Muscle building / muscle maintenance
4. Weight maintenance
5. Professional review recommended

Age: {age}
Height: {height} cm
Weight: {weight} kg
BMI: {bmi:.1f}
Gender: {gender}
Activity level: {activity_level}

Health conditions: {conditions}
Other condition: {other_condition}
Additional health information: {additional_health}

Laboratory information:
{report_text}

Diet type: {diet_type}
Favorite foods: {favorite_foods}
Disliked foods: {disliked_foods}
Allergies: {allergies}
Number of meals: {number_of_meals}
Budget: {budget}
Location: {location}

Safety rules:
- Do not diagnose.
- Do not claim that a lab result confirms a diagnosis.
- Do not prescribe or change medication.
- Do not recommend extreme dieting.
- Do not use BMI alone.
- Respect allergies and food restrictions.
- Consider health conditions, lab information, budget and local foods.
- If information is concerning or insufficient, recommend professional review.
- Do not invent laboratory values.

Return:
## Health Status Summary
## Recommended Nutrition Goal
## Why This Goal?
## Health Considerations
## Nutrition Priorities
## Foods to Emphasize
## Foods to Limit
## Safety Flag

This is educational nutrition guidance, not medical diagnosis or treatment.
"""

    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[
            {
                "role": "system",
                "content": "You are a careful AI nutrition assistant. Provide educational nutrition guidance and never diagnose or prescribe medical treatment."
            },
            {"role": "user", "content": prompt},
        ],
        temperature=0.2,
        max_tokens=3000,
    )
    return response.choices[0].message.content

def generate_meal_plan(health_analysis):
    conditions = ", ".join(disease)

    prompt = f"""
You are an AI-assisted personalized meal planning system.

Create a practical one-day meal plan using the health assessment below.

HEALTH ANALYSIS:
{health_analysis}

USER INFORMATION:
Age: {age}
Height: {height} cm
Weight: {weight} kg
BMI: {bmi:.1f}
Gender: {gender}
Activity level: {activity_level}
Health conditions: {conditions}
Other condition: {other_condition}
Laboratory information: {report_text}

FOOD PREFERENCES:
Diet type: {diet_type}
Favorite foods: {favorite_foods}
Disliked foods: {disliked_foods}
Allergies: {allergies}

LIFESTYLE:
Number of meals: {number_of_meals}
Budget: {budget}
Location: {location}

Requirements:
- Follow the recommended nutrition goal.
- Consider health information.
- Respect allergies and intolerances.
- Include preferred foods where appropriate.
- Avoid disliked foods where practical.
- Consider budget and local food availability.
- Use simple household portions.
- Avoid extreme dieting.
- Do not prescribe medication or make unsupported medical claims.

Return:
# Personalized Diet Plan
## Recommended Goal
## Meal 1
## Meal 2
Continue according to the requested number of meals.
## Affordable Alternatives
## Shopping List
## Hydration
## Foods to Emphasize
## Foods to Limit
## Why This Plan Fits
## Professional Review

Do not present this as a medical prescription.
"""

    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[
            {
                "role": "system",
                "content": "You are a careful AI meal planning assistant. Provide practical educational meal plans and never diagnose or prescribe medical treatment."
            },
            {"role": "user", "content": prompt},
        ],
        temperature=0.3,
        max_tokens=5000,
    )
    return response.choices[0].message.content

st.markdown("---")

if st.button("🔍 Analyze Health & Recommend Goal", type="primary"):
    with st.spinner("Analyzing your health information..."):
        try:
            st.session_state.health_analysis = analyze_health()
            st.success("Health analysis completed!")
        except Exception as e:
            st.error(f"Something went wrong: {e}")

if "health_analysis" in st.session_state:
    st.markdown("---")
    st.header("🩺 AI Health & Nutrition Assessment")
    st.markdown(st.session_state.health_analysis)

    st.info("The recommended goal is based on the information provided. It is educational nutrition guidance, not a medical diagnosis.")

    if st.button("🥗 Generate Personalized Diet Plan", type="primary"):
        with st.spinner("Creating your personalized diet plan..."):
            try:
                st.session_state.meal_plan = generate_meal_plan(st.session_state.health_analysis)
                st.success("Your personalized diet plan is ready!")
            except Exception as e:
                st.error(f"Something went wrong: {e}")

if "meal_plan" in st.session_state:
    st.markdown("---")
    st.header("🍽️ Your Personalized Diet Plan")
    st.markdown(st.session_state.meal_plan)
    st.markdown("---")
    st.warning(
        "This plan is AI-generated educational guidance and is not a medical prescription. "
        "Consult a qualified healthcare professional before making major dietary changes "
        "related to a medical condition or abnormal laboratory results."
    )
