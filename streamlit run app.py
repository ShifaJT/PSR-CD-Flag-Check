import streamlit as st
import pandas as pd
import re

SHEET_ID = "1J21WFryYV1pGn5bfJuk15onQVVaPscU-8Y71VhEH2DA"
SHEET_NAME = "Main Sheet"

SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=0"


# -----------------------------
# Helpers
# -----------------------------
def normalize_bzid(value):
    if pd.isna(value):
        return ""
    value = str(value)
    value = value.replace("\u00A0", "")
    value = re.sub(r"\s+", "", value)
    return value.upper().strip()


# -----------------------------
# Load & Cache Data
# -----------------------------
@st.cache_data(ttl=3600)
def load_data():
    df = pd.read_csv(SHEET_URL)
    df["BZID_NORM"] = df["BZID"].apply(normalize_bzid)
    return df


# -----------------------------
# UI
# -----------------------------
st.set_page_config(
    page_title="CD – PSR Flag Lookup",
    layout="centered"
)

st.title("CD – PSR Flag Lookup")
st.caption("Paste BZID carefully. Extra spaces are auto-cleaned.")

df = load_data()

bzid_input = st.text_input(
    "Enter BZID",
    placeholder="e.g. BZID-1304457049"
)

if bzid_input:
    search_key = normalize_bzid(bzid_input)
    result = df[df["BZID_NORM"] == search_key]

    if result.empty:
        st.error("BZID not found. Please recheck.")
    else:
        row = result.iloc[0]

        col1, col2 = st.columns(2)
        col1.metric("Cluster", row["cluster"])
        col2.metric("Hub", row["hub"])

        st.divider()

        col3, col4, col5 = st.columns(3)
        col3.metric("PSR Requested GMV", row["psr_requested_gmv"])
        col4.metric("Delivered GMV", row["del_gmv"])
        col5.metric("PSR %", row["psr_pct"])

        st.divider()

        if row["CD_flag"] == "Ask for image":
            st.error("📸 ASK FOR IMAGE")
        else:
            st.success("✅ DO NOT ASK FOR IMAGE")
