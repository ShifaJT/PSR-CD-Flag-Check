import streamlit as st
import pandas as pd
import gspread
from google.oauth2 import service_account
from datetime import datetime
from gspread.exceptions import WorksheetNotFound

# ================= PAGE CONFIG =================
st.set_page_config(
    page_title="PSR CD Flag Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ================= CSS =================
st.markdown("""
<style>
div[data-testid="stTextInput"] > div > input {
    border: 3px solid #2563eb !important;
    background-color: #eef2ff !important;
    font-weight: 600;
}
div[data-testid="stTextInput"] label {
    font-size: 1.05rem !important;
    font-weight: 700 !important;
    color: #1e3a8a !important;
}
.stButton > button {
    width: 100%;
}
.footer {
    text-align: center;
    color: #6b7280;
    font-size: 0.85rem;
    margin-top: 2rem;
    border-top: 1px solid #e5e7eb;
    padding-top: 1rem;
}
</style>
""", unsafe_allow_html=True)

# ================= SESSION STATE =================
if "data" not in st.session_state:
    st.session_state.data = None
if "last_update" not in st.session_state:
    st.session_state.last_update = None

# ================= HEADER =================
col1, col2 = st.columns([3, 1])
with col1:
    st.markdown("## PSR CD Flag Dashboard")
    st.caption("Enterprise-grade customer data lookup system")

with col2:
    st.caption("Last Updated")
    st.write(datetime.now().strftime("%d %b %Y, %H:%M"))

# ================= LOAD DATA =================
@st.cache_data(ttl=300)
def load_data():
    creds = service_account.Credentials.from_service_account_info(
        dict(st.secrets["gcp_service_account"]),
        scopes=[
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ]
    )
    client = gspread.authorize(creds)

    sheet = client.open_by_key(st.secrets["sheets"]["sheet_id"])
    sheet_name = st.secrets["sheets"].get("sheet_name", "Main Sheet")

    try:
        ws = sheet.worksheet(sheet_name)
    except WorksheetNotFound:
        ws = sheet.get_worksheet(0)

    df = pd.DataFrame(ws.get_all_records())
    df.columns = [c.strip() for c in df.columns]
    return df

# ================= SIDEBAR =================
with st.sidebar:
    st.markdown("### ⚙️ Controls")
    if st.button("🔄 Refresh Data"):
        st.cache_data.clear()
        st.session_state.data = None
        st.rerun()

# ================= INITIAL LOAD =================
if st.session_state.data is None:
    with st.spinner("Loading customer database..."):
        st.session_state.data = load_data()
        st.session_state.last_update = datetime.now()

df = st.session_state.data

# ================= SIDEBAR OVERVIEW =================
with st.sidebar:
    st.markdown("---")
    st.markdown("### 📊 Database Overview")

    st.metric("Total Customers", len(df))

    ask_image = (
        df[df["CD_flag"].str.contains("ask", case=False, na=False)].shape[0]
        if "CD_flag" in df.columns else 0
    )
    do_not_ask = (
        df[df["CD_flag"].str.contains("do not", case=False, na=False)].shape[0]
        if "CD_flag" in df.columns else 0
    )

    st.metric("Ask for Image", ask_image)
    st.metric("Do Not Ask Image", do_not_ask)

# ================= SEARCH =================
st.markdown("---")
c1, c2 = st.columns([3, 1])

with c1:
    bzid_input = st.text_input(
        "🔍 ENTER CUSTOMER BZID (Mandatory)",
        placeholder="Example: BZID-1305378359",
        key="search_input"
    )

with c2:
    st.markdown("<br>", unsafe_allow_html=True)
    search_btn = st.button("Search Database", disabled=not bool(bzid_input))

# ================= SEARCH LOGIC =================
if search_btn and bzid_input:

    bzid_col = next((c for c in df.columns if "bzid" in c.lower()), None)

    if not bzid_col:
        st.error("BZID column not found.")
    else:
        search_term = bzid_input.replace("BZID-", "").strip()
        customer_data = None

        for _, row in df.iterrows():
            if str(row[bzid_col]).replace("BZID-", "").strip() == search_term:
                customer_data = row
                break

        if customer_data is None:
            st.error("Customer not found.")
        else:
            # ✅ SAFE PSR % CONVERSION
            psr_val = pd.to_numeric(customer_data.get("psr_pct"), errors="coerce")
            psr_pct_display = f"{psr_val * 100:.2f}%" if pd.notna(psr_val) else "NA"

            # ================= COPY BLOCK =================
            ticket_text = f"""
Cluster: {customer_data.get('cluster', 'NA')}
Hub: {customer_data.get('hub', 'NA')}
CD Flag: {customer_data.get('CD_flag', 'NA')}
PSR %: {psr_pct_display}
PSR Requested GMV: {customer_data.get('psr_requested_gmv', 'NA')}
Delivered GMV: {customer_data.get('del_gmv', 'NA')}
""".strip()

            st.markdown("### 📋 Copy for Ticket Documentation")
            st.text_area(
                "Copy everything below and paste in ticket",
                ticket_text,
                height=160
            )

            # ================= COMPLETE CUSTOMER DATA =================
            st.markdown("### 📊 Complete Customer Data")

            rows = []
            for col in df.columns:
                raw_val = customer_data[col]

                if col.lower() == "psr_pct":
                    num = pd.to_numeric(raw_val, errors="coerce")
                    display_val = f"{num * 100:.2f}%" if pd.notna(num) else "NA"
                else:
                    display_val = raw_val if str(raw_val).strip() != "" else "NA"

                rows.append({
                    "Field": col.replace("_", " ").title(),
                    "Value": display_val
                })

            st.dataframe(
                pd.DataFrame(rows),
                hide_index=True,
                use_container_width=True
            )

# ================= FOOTER =================
st.markdown("""
<div class="footer">
PSR CD Flag Dashboard v1.0 • Secure enterprise data access system<br>
© 2024 Customer Intelligence Platform • All rights reserved
</div>
""", unsafe_allow_html=True)
