import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="Employee Analytics — Demo", layout="wide")
st.title("Employee Analytics — Demo")

st.markdown("""
Simple, recruiter-friendly demo: upload a CSV or use our synthetic sample, then explore key HR KPIs.
KPIs: **Headcount**, **Attrition rate**, **Average Tenure**, **Avg Compensation**.
""")

# --- sample synthetic dataset ---
def make_sample(n=500, seed=7):
    rng = np.random.default_rng(seed)
    df = pd.DataFrame({
        "employee_id": np.arange(1, n+1),
        "department": rng.choice(["Sales","HR","IT","Finance","Ops"], size=n, p=[.28,.08,.32,.14,.18]),
        "gender": rng.choice(["F","M"], size=n, p=[.45,.55]),
        "status": rng.choice(["Active","Exited"], size=n, p=[.87,.13]),
        "tenure_years": rng.gamma(shape=2.0, scale=1.5, size=n).round(2),
        "compensation": np.round(rng.normal(42000, 9000, size=n), 0),
    })
    # clean negatives due to normal
    df["compensation"] = df["compensation"].clip(lower=18000)
    return df

st.sidebar.header("Data")
uploaded = st.sidebar.file_uploader("Upload CSV (columns: employee_id, department, status, tenure_years, compensation)", type=["csv"])
if uploaded:
    df = pd.read_csv(uploaded)
else:
    df = make_sample()

# filters
dept_options = sorted(df["department"].dropna().unique())
dept_sel = st.sidebar.multiselect("Department", dept_options, default=dept_options)

f = df[df["department"].isin(dept_sel)].copy()

# KPIs
headcount = int((f["status"]=="Active").sum())
attrition_rate = float((f["status"]=="Exited").mean()*100)
avg_tenure = float(f["tenure_years"].mean())
avg_comp = float(f["compensation"].mean())

c1,c2,c3,c4 = st.columns(4)
c1.metric("Headcount", f"{headcount:,}")
c2.metric("Attrition Rate", f"{attrition_rate:.1f}%")
c3.metric("Avg Tenure (yrs)", f"{avg_tenure:.2f}")
c4.metric("Avg Compensation (€)", f"{avg_comp:,.0f}")

# charts
st.subheader("Headcount by Department")
hc_by_dept = (f.assign(active=(f["status"]=="Active").astype(int))
                .groupby("department")["active"].sum().sort_values(ascending=False))
st.bar_chart(hc_by_dept)

st.subheader("Compensation Distribution (All Selected Departments)")
st.dataframe(f[["department","status","tenure_years","compensation"]].sample(min(10, len(f)), random_state=7))
st.caption("Upload your CSV to use real company-like data. This is a lightweight demo for recruiters.")
