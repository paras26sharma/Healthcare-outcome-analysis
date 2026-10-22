import streamlit as st
import pandas as pd
import joblib
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

# ---------------------------------------------------------
# Healthcare Outcome Risk Prediction - Interactive Dashboard
# Keep this file in the same folder as Risk_model1.joblib
# and patients.csv. Optional: labs.csv, diagnoses.csv,
# outcomes.csv.
# ---------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent

st.set_page_config(
    page_title="Healthcare Risk Analytics",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom styling
st.markdown(
    """
    <style>
    /* dark blue mix background */
    .stApp { background: linear-gradient(135deg, #08162d 0%, #12315c 50%, #1b4b82 100%); }
    header[data-testid="stHeader"] { background: transparent; }
    [data-testid="stSidebar"] { background: linear-gradient(180deg, #0a1d3a 0%, #123a6b 100%); }
    [data-testid="stSidebar"] label, [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] p { color: #ffffff !important; }

    .main-title { font-size: 2.15rem; font-weight: 800; color: #ffffff; margin-bottom: 0; }
    .subtitle { color: #b9cde6; margin-top: 0.2rem; margin-bottom: 1.2rem; }
    h1, h2, h3, h4, .stMarkdown, .stCaption, .section-note { color: #ffffff; }

    /* KPI cards: white card, bold black text */
    div[data-testid="stMetric"] {
        background: #ffffff; border: 1px solid #9fc1e8; padding: 16px;
        border-radius: 14px; box-shadow: 0 4px 16px rgba(0,0,0,0.35);
    }
    div[data-testid="stMetricLabel"], div[data-testid="stMetricLabel"] * {
        color: #000000 !important; font-weight: 700 !important;
    }
    div[data-testid="stMetricValue"], div[data-testid="stMetricValue"] * {
        color: #000000 !important; font-weight: 800 !important;
    }

    /* inputs, dropdowns, search box */
    div[data-baseweb="select"] > div, div[data-baseweb="input"] > div,
    .stTextInput input, .stNumberInput input {
        background-color: #0f2a4d !important; color: #ffffff !important;
        border: 1px solid #3a6ea5 !important;
    }
    span[data-baseweb="tag"] { background-color: #2f80ed !important; color: #ffffff !important; }

    /* tabs */
    button[data-baseweb="tab"] p { color: #ffffff !important; font-weight: 600; }

    /* chart and table panels */
    [data-testid="stPlotlyChart"] {
        background: rgba(255,255,255,0.06); border-radius: 12px; padding: 6px;
    }
    [data-testid="stDataFrame"] { border: 1px solid #3a6ea5; border-radius: 10px; }
    

    /* KPI labels: dark and always visible */
    /* KPI labels: dark and always visible */
div[data-testid="stMetric"] label,
div[data-testid="stMetric"] label *,
div[data-testid="stMetricLabel"],
div[data-testid="stMetricLabel"] *,
div[data-testid="stMetricLabel"] p,
div[data-testid="stMetric"] [data-testid="stMarkdownContainer"],
div[data-testid="stMetric"] [data-testid="stMarkdownContainer"] * {
    color: #000000 !important;
    -webkit-text-fill-color: #000000 !important;
    opacity: 1 !important;
    font-weight: 700 !important;
    white-space: normal !important;
    overflow: visible !important;
    text-overflow: clip !important;
}

/* KPI values: bold black, no "..." cut-off */
div[data-testid="stMetricValue"],
div[data-testid="stMetricValue"] * {
    color: #000000 !important;
    -webkit-text-fill-color: #000000 !important;
    font-weight: 800 !important;
    font-size: 1.6rem !important;
    white-space: normal !important;
    overflow: visible !important;
    text-overflow: clip !important;
}


/* pointer cursor on dropdowns, hide the blinking typing caret */
div[data-baseweb="select"],
div[data-baseweb="select"] * {
    cursor: pointer !important;
}
div[data-baseweb="select"] input {
    caret-color: transparent !important;
}

/* KPI cards and titles: normal arrow, no text selection */
div[data-testid="stMetric"],
div[data-testid="stMetric"] *,
.main-title, .subtitle {
    cursor: default !important;
    user-select: none !important;
    -webkit-user-select: none !important;
}

/* tabs and buttons: hand cursor */
button[data-baseweb="tab"], .stButton button, .stDownloadButton button,
[data-testid="stFormSubmitButton"] button {
    cursor: pointer !important;
}

    </style>
    """,
    unsafe_allow_html=True,
)



def load_csv(filename):
    path = BASE_DIR / filename
    if path.exists():
        try:
            return pd.read_csv(path)
        except Exception as exc:
            st.warning(f"Could not read {filename}: {exc}")
    return pd.DataFrame()


def standardize_columns(df):
    """Normalize common column names while preserving original data."""
    df = df.copy()
    df.columns = [str(c).strip() for c in df.columns]
    aliases = {
        "Length of stay": "LengthOfStay",
        "LengthOfStay": "LengthOfStay",
        "TreatmentCost": "TreatmentCost",
        "Risk Score": "Risk Score",
        "OutcomeName": "OutcomeName",
        "DiagnosisName": "DiagnosisName",
    }
    return df.rename(columns={c: aliases[c] for c in df.columns if c in aliases})


patients = standardize_columns(load_csv("patients.csv"))
labs = load_csv("labs.csv")

st.markdown('<div class="main-title">🏥 Healthcare Risk Analytics</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="subtitle">Patient outcomes, risk patterns, treatment costs, and ML-based risk prediction</div>',
    unsafe_allow_html=True,
)

if patients.empty:
    st.error("patients.csv was not found or could not be read. Put patients.csv in the same folder as this Python file.")
    st.stop()

# Clean fields used in filters/charts without changing the source file.
for col in ["Age", "TreatmentCost", "LengthOfStay", "Risk Score", "OutcomeName", "DiagnosisName", "Gender"]:
    if col not in patients.columns:
        if col == "LengthOfStay" and "Length of stay" in patients.columns:
            patients["LengthOfStay"] = patients["Length of stay"]
        elif col in ["Risk Score", "OutcomeName", "DiagnosisName", "Gender"]:
            patients[col] = "Unknown"
        else:
            patients[col] = 0

for col in ["Age", "TreatmentCost", "LengthOfStay"]:
    patients[col] = pd.to_numeric(patients[col], errors="coerce")

patients["Risk Score"] = patients["Risk Score"].fillna("Unknown").astype(str)
patients["OutcomeName"] = patients["OutcomeName"].fillna("Unknown").astype(str)
patients["DiagnosisName"] = patients["DiagnosisName"].fillna("Unknown").astype(str)
patients["Gender"] = patients["Gender"].fillna("Unknown").astype(str)

# Sidebar filters
st.sidebar.header("🔎 Dashboard Filters")
diagnoses = sorted(patients["DiagnosisName"].dropna().unique().tolist())
outcomes = sorted(patients["OutcomeName"].dropna().unique().tolist())
genders = sorted(patients["Gender"].dropna().unique().tolist())
risks = sorted(patients["Risk Score"].dropna().unique().tolist())

selected_diagnoses = st.sidebar.multiselect("Diagnosis", diagnoses, default=diagnoses)
selected_outcomes = st.sidebar.multiselect("Outcome", outcomes, default=outcomes)
selected_genders = st.sidebar.multiselect("Gender", genders, default=genders)
selected_risks = st.sidebar.multiselect("Risk level", risks, default=risks)

age_min = int(patients["Age"].min()) if patients["Age"].notna().any() else 0
age_max = int(patients["Age"].max()) if patients["Age"].notna().any() else 100
if age_min == age_max:
    age_range = (age_min, age_max)
else:
    age_range = st.sidebar.slider("Patient age range", age_min, age_max, (age_min, age_max))

filtered = patients[
    patients["DiagnosisName"].isin(selected_diagnoses)
    & patients["OutcomeName"].isin(selected_outcomes)
    & patients["Gender"].isin(selected_genders)
    & patients["Risk Score"].isin(selected_risks)
    & patients["Age"].between(age_range[0], age_range[1], inclusive="both")
].copy()

# KPI cards
total_patients = len(filtered)
high_risk_count = filtered["Risk Score"].str.contains("high", case=False, na=False).sum()
avg_age = filtered["Age"].mean() if total_patients else 0
total_cost = filtered["TreatmentCost"].sum() if total_patients else 0
recovered_count = filtered["OutcomeName"].str.contains("recover", case=False, na=False).sum()

k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Patients", f"{total_patients:,}")
k2.metric("High-risk patients", f"{high_risk_count:,}")
k3.metric("Average age", f"{avg_age:.1f} years" if total_patients else "—")
k4.metric("Total treatment cost", f"₹{total_cost:,.0f}")
k5.metric("Recovered", f"{recovered_count:,}")


st.divider()

overview_tab, diagnosis_tab, patient_tab, prediction_tab = st.tabs(
    ["📊 Overview", "🩺 Diagnosis & Labs", "👥 Patient Explorer", "🤖 Predict Risk"]
)

with overview_tab:
    st.subheader("Patient and outcome overview")
    if filtered.empty:
        st.info("No patients match the selected filters. Adjust the filters in the sidebar.")
    else:
        c1, c2 = st.columns(2)
        risk_counts = filtered["Risk Score"].value_counts().rename_axis("Risk Level").reset_index(name="Patients")
        risk_fig = px.pie(
            risk_counts, names="Risk Level", values="Patients", hole=0.58,
            title="Risk Level Distribution", color="Risk Level",
            color_discrete_map={"High Risk": "#e45756", "Low Risk": "#2a9d8f", "Unknown": "#9aa7b2"},
        )
        risk_fig.update_traces(textposition="inside", textinfo="percent+label")
        risk_fig.update_layout(legend_title_text="", margin=dict(t=60, b=20, l=10, r=10))
        c1.plotly_chart(risk_fig, use_container_width=True)

        outcome_counts = filtered["OutcomeName"].value_counts().rename_axis("Outcome").reset_index(name="Patients")
        outcome_fig = px.bar(
            outcome_counts, x="Outcome", y="Patients", color="Outcome",
            title="Patient Outcomes", text="Patients",
            color_discrete_sequence=px.colors.qualitative.Safe,
        )
        outcome_fig.update_traces(textposition="outside")
        outcome_fig.update_layout(showlegend=False, margin=dict(t=60, b=20, l=10, r=10))
        c2.plotly_chart(outcome_fig, use_container_width=True)

        c3, c4 = st.columns(2)
        cost_by_diagnosis = (
            filtered.groupby("DiagnosisName", as_index=False)["TreatmentCost"]
            .sum().sort_values("TreatmentCost", ascending=False)
        )
        cost_fig = px.bar(
            cost_by_diagnosis, x="DiagnosisName", y="TreatmentCost",
            title="Total Treatment Cost by Diagnosis", color="TreatmentCost",
            color_continuous_scale="Blues", hover_data={"TreatmentCost": ":,.2f"},
        )
        cost_fig.update_layout(xaxis_title="", yaxis_title="Treatment cost", coloraxis_showscale=False,
                               margin=dict(t=60, b=20, l=10, r=10))
        c3.plotly_chart(cost_fig, use_container_width=True)

        age_fig = px.histogram(
            filtered, x="Age", color="Risk Score", nbins=15,
            title="Age Distribution by Risk Level", barmode="overlay", opacity=0.78,
            color_discrete_map={"High Risk": "#e45756", "Low Risk": "#2a9d8f", "Unknown": "#9aa7b2"},
        )
        age_fig.update_layout(margin=dict(t=60, b=20, l=10, r=10))
        c4.plotly_chart(age_fig, use_container_width=True)

        stay_fig = px.scatter(
            filtered, x="LengthOfStay", y="TreatmentCost", color="Risk Score",
            size="Age", hover_name="Name" if "Name" in filtered.columns else None,
            hover_data=["DiagnosisName", "OutcomeName"],
            title="Length of Stay vs Treatment Cost",
            color_discrete_map={"High Risk": "#e45756", "Low Risk": "#2a9d8f", "Unknown": "#9aa7b2"},
        )
        stay_fig.update_layout(xaxis_title="Length of stay (days)", yaxis_title="Treatment cost",
                               margin=dict(t=60, b=20, l=10, r=10))
        st.plotly_chart(stay_fig, use_container_width=True)

with diagnosis_tab:
    st.subheader("Diagnosis and laboratory analysis")
    if not filtered.empty:
        diagnosis_summary = (
            filtered.groupby("DiagnosisName", as_index=False)
            .agg(Patients=("DiagnosisName", "size"), AverageCost=("TreatmentCost", "mean"),
                 AverageStay=("LengthOfStay", "mean"))
            .sort_values("Patients", ascending=False)
        )
        c1, c2 = st.columns(2)
        dx_fig = px.bar(
            diagnosis_summary, x="DiagnosisName", y="Patients", color="Patients",
            title="Patients by Diagnosis", text="Patients", color_continuous_scale="Teal",
        )
        dx_fig.update_layout(xaxis_title="", coloraxis_showscale=False, margin=dict(t=60, b=20, l=10, r=10))
        c1.plotly_chart(dx_fig, use_container_width=True)

        stay_by_dx = px.bar(
            diagnosis_summary, x="DiagnosisName", y="AverageStay",
            title="Average Length of Stay by Diagnosis", color="AverageStay",
            color_continuous_scale="Purples",
        )
        stay_by_dx.update_layout(xaxis_title="", yaxis_title="Average days", coloraxis_showscale=False,
                                 margin=dict(t=60, b=20, l=10, r=10))
        c2.plotly_chart(stay_by_dx, use_container_width=True)
        st.markdown("**Diagnosis summary**")
        display_summary = diagnosis_summary.rename(columns={
            "DiagnosisName": "Diagnosis", "Patients": "Patients",
            "AverageCost": "Average treatment cost", "AverageStay": "Average stay (days)"
        })
        st.dataframe(display_summary, use_container_width=True, hide_index=True)

    if not labs.empty and {"PatientID", "TestName", "Result"}.issubset(labs.columns):
        st.markdown("**Laboratory results**")
        available_tests = sorted(labs["TestName"].dropna().astype(str).unique().tolist())
        chosen_test = st.selectbox("Choose a lab test", available_tests)
        lab_data = labs[labs["TestName"].astype(str) == chosen_test].copy()
        lab_data["Result"] = pd.to_numeric(lab_data["Result"], errors="coerce")
        lab_data = lab_data.dropna(subset=["Result"])
        if not lab_data.empty:
            lab_fig = px.histogram(
                lab_data, x="Result", nbins=20, marginal="box",
                title=f"Distribution of {chosen_test} Results",
                labels={"Result": "Lab result", "count": "Number of tests"},
            )
            lab_fig.update_layout(margin=dict(t=60, b=20, l=10, r=10))
            st.plotly_chart(lab_fig, use_container_width=True)
            st.caption("The lab chart shows the distribution of recorded results. Clinical interpretation requires the relevant test-specific reference range.")
    else:
        st.info("Optional lab charts require labs.csv with PatientID, TestName, and Result columns.")

with patient_tab:
    st.subheader("Patient Explorer")
    search_text = st.text_input("Search by patient name or ID", placeholder="Type a name or patient ID...")
    patient_view = filtered.copy()
    if search_text.strip():
        term = search_text.strip().lower()
        if "Name" in patient_view.columns:
            name_match = patient_view["Name"].astype(str).str.lower().str.contains(term, na=False)
        else:
            name_match = pd.Series(False, index=patient_view.index)
        if "PatientID" in patient_view.columns:
            id_match = patient_view["PatientID"].astype(str).str.contains(term, na=False)
        else:
            id_match = pd.Series(False, index=patient_view.index)
        patient_view = patient_view[name_match | id_match]

    preferred_cols = [
        "PatientID", "Name", "Age", "Gender", "DiagnosisName", "OutcomeName",
        "LengthOfStay", "TreatmentCost", "Risk Score"
    ]
    display_cols = [c for c in preferred_cols if c in patient_view.columns]
    st.dataframe(patient_view[display_cols], use_container_width=True, hide_index=True)
    csv_data = patient_view[display_cols].to_csv(index=False).encode("utf-8")
    st.download_button(
        "⬇️ Download filtered patient data (CSV)",
        data=csv_data,
        file_name="filtered_healthcare_patients.csv",
        mime="text/csv",
    )

with prediction_tab:
    st.subheader("Machine-learning risk prediction")
    st.markdown(
        "Enter the patient's details and select **Predict Risk**."
    )
    model_path = BASE_DIR / "Risk_model1.joblib"
    if not model_path.exists():
        st.error("Risk_model1.joblib was not found. Put the trained model file in the same folder as this app.")
    else:
        try:
            model = joblib.load(model_path)
            with st.form("risk_prediction_form"):
                p1, p2 = st.columns(2)
                age = p1.number_input("Age (years)", min_value=0, max_value=120, value=45, step=1)
                length_of_stay = p2.number_input("Length of stay (days)", min_value=0, max_value=365, value=5, step=1)
                treatment_cost = p1.number_input("Treatment cost (₹)", min_value=0.0, value=5000.0, step=500.0)
                abnormal_lab_count = p2.number_input("Abnormal lab count", min_value=0, max_value=100, value=1, step=1)
                submitted = st.form_submit_button("🔍 Predict Risk", use_container_width=True)

            if submitted:
                input_data = pd.DataFrame(
                    [[age, length_of_stay, treatment_cost, abnormal_lab_count]],
                    columns=["Age", "LengthOfStay", "TreatmentCost", "AbnormalLabCount"],
                )
                prediction = model.predict(input_data)[0]
                risk_label = "High Risk" if str(prediction) in ["1", "1.0", "High Risk"] else "Low Risk"

                probability = None
                if hasattr(model, "predict_proba"):
                    probabilities = model.predict_proba(input_data)[0]
                    classes = list(getattr(model, "classes_", []))
                    if len(classes) == len(probabilities):
                        high_class_index = next(
                            (i for i, cls in enumerate(classes) if str(cls).lower() in ["1", "1.0", "high risk"]),
                            len(probabilities) - 1,
                        )
                    else:
                        high_class_index = len(probabilities) - 1
                    probability = float(probabilities[high_class_index])

                if risk_label == "High Risk":
                    st.error("⚠️ Model prediction: HIGH RISK")
                else:
                    st.success("✅ Model prediction: LOW RISK")

                if probability is not None:
                    m1, m2 = st.columns([1, 2])
                    m1.metric("Estimated high-risk probability", f"{probability:.1%}")
                    gauge = go.Figure(go.Indicator(
                        mode="gauge+number",
                        value=probability * 100,
                        number={"suffix": "%"},
                        title={"text": "Model risk probability"},
                        gauge={"axis": {"range": [0, 100]},
                               "bar": {"color": "#e45756" if probability >= 0.5 else "#2a9d8f"},
                               "steps": [
                                   {"range": [0, 35], "color": "#d8f3e8"},
                                   {"range": [35, 65], "color": "#fff0c2"},
                                   {"range": [65, 100], "color": "#f8d7da"},
                               ]},
                    ))
                    gauge.update_layout(height=260, margin=dict(t=50, b=10, l=25, r=25))
                    m2.plotly_chart(gauge, use_container_width=True)
                st.caption("Probability interpretation depends on the model's training data and may not reflect actual clinical risk. Always consult a healthcare professional for medical advice.")
        except Exception as exc:
            st.error(f"The model could not be loaded or prediction failed: {exc}")
            st.info("Confirm that Risk_model1.joblib matches the four input features used by this app.")

st.divider()
st.caption("Healthcare Risk Analytics")
