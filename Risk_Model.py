import streamlit as st
import pandas as pd
import joblib

model = joblib.load('Risk_model1.joblib')

st.title('Healthcare Outcome Risk Prediction')

age = st.number_input('Age', min_value=0)
length_of_stay = st.number_input('Length of Stay (days)', min_value=0)
treatment_cost = st.number_input('Treatment Cost', min_value=0.0)
AbnormalLabCount = st.number_input('AbnormalLabCount', min_value=0)

if st.button('Predict Risk'):
    input_data = pd.DataFrame([[age, length_of_stay, treatment_cost, AbnormalLabCount]], columns=['Age', 'LengthOfStay', 'TreatmentCost', 'AbnormalLabCount'])
    risk_prediction = model.predict(input_data)[0]
    risk_probability = model.predict_proba(input_data)[0][1]

    st.write(f'Predicted Risk: {"High Risk" if risk_prediction == 1 else "Low Risk"}')
    st.write(f'Risk Probability: {round(risk_probability, 2)}')