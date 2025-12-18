import streamlit as st
import pandas as pd
import re
import gspread
from google.oauth2.service_account import Credentials

# ---------------- CONFIG ----------------
SHEET_ID = "1J21WFryYV1pGn5bfJuk15onQVVaPscU-8Y71VhEH2DA"
SHEET_NAME = "Main Sheet"


# ---------------- HELPERS ----------------
def normalize_bzid(value):
    if pd.isna(value):
        return ""
    value = str(value)
    value = value.replace("\u00A0", "")
    value = re.sub(r"\s+", "", value)
    return value.upper().strip()


# ---------------- LOAD DATA ----------------
from googleapiclient.discovery import build

@st.cache_data(ttl=3600)
def load_data():
    creds = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=[
            "https://www.googleapis.com/auth/drive.readonly",
            "https://www.googleapis.com/auth/spreadsheets.readonly",
        ]
    )

    # 🔹 Explicit Drive access
    drive_service = build("drive", "v3", credentials=creds)

    # 🔹 This line forces Drive permission check
    drive_service.files().get(
        fileId=SHEET_ID,
        fields="id, name"
    ).execute()

    # 🔹 If above passes, Sheets access WILL work
    client = gspread.authorize(creds)
    sheet = client.open_by_key(SHEET_ID).worksheet(SHEET_NAME)

    records = sheet.get_all_records()
    df = pd.DataFrame(records)

    df["BZID_NORM"] = df["BZID"].apply(normalize_bzid)
    return df


# ---------------- UI ----------------
st.set_page_config(page_title="CD – PSR Flag Lookup")

st.title("CD – PSR Flag Lookup")
st.caption("Paste BZID carefully. Extra spaces are auto-cleaned.")

df = load_data()

bzid_input = st.text_input("Enter BZID")

if bzid_input:
    key = normalize_bzid(bzid_input)
    result = df[df["BZID_NORM"] == key]

    if result.empty:
        st.error("BZID not found. Please recheck.")
    else:
        row = result.iloc[0]

        c1, c2 = st.columns(2)
        c1.metric("Cluster", row["cluster"])
        c2.metric("Hub", row["hub"])

        st.divider()

        c3, c4, c5 = st.columns(3)
        c3.metric("PSR Requested GMV", row["psr_requested_gmv"])
        c4.metric("Delivered GMV", row["del_gmv"])
        c5.metric("PSR %", row["psr_pct"])

        st.divider()

        if row["CD_flag"] == "Ask for image":
            st.error("📸 ASK FOR IMAGE")
        else:
            st.success("✅ DO NOT ASK FOR IMAGE")
