import streamlit as st
import pandas as pd
import gspread
from google.oauth2 import service_account
from datetime import datetime

# Page configuration - Professional and clean
st.set_page_config(
    page_title="PSR CD Flag Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================
# CSS (ONLY small additions)
# ==========================
st.markdown("""
<style>
    :root {
        --primary: #2563eb;
        --primary-dark: #1d4ed8;
        --success: #10b981;
        --warning: #f59e0b;
        --danger: #ef4444;
        --gray-50: #f9fafb;
        --gray-100: #f3f4f6;
        --gray-200: #e5e7eb;
        --gray-700: #374151;
        --gray-900: #111827;
    }

    /* ===== FIX #2: Highlight BZID input ===== */
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
        background: var(--primary) !important;
        color: white !important;
        border-radius: 8px !important;
        padding: 0.75rem 2rem !important;
        width: 100%;
    }

    .footer {
        text-align: center;
        color: #6b7280;
        font-size: 0.85rem;
        margin-top: 3rem;
        border-top: 1px solid #e5e7eb;
        padding-top: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# ==========================
# Session State
# ==========================
if "data" not in st.session_state:
    st.session_state.data = None

if "last_update" not in st.session_state:
    st.session_state.last_update = None

# ==========================
# Header
# ==========================
col1, col2 = st.columns([3, 1])

with col1:
    st.markdown("## PSR CD Flag Dashboard")
    st.caption("Enterprise-grade customer data lookup system")

with col2:
    st.caption("Last Updated")
    st.write(datetime.now().strftime("%d %b %Y, %H:%M"))

# ==========================
# Load Data
# ==========================
@st.cache_data(ttl=300)
def load_data():
    creds_dict = dict(st.secrets["gcp_service_account"])
    credentials = service_account.Credentials.from_service_account_info(
        creds_dict,
        scopes=[
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ]
    )
    client = gspread.authorize(credentials)

    sheet = client.open_by_key(st.secrets["sheets"]["sheet_id"])
    sheet_name = st.secrets["sheets"].get("sheet_name", "CD-PSR Flag")
    worksheet = sheet.worksheet(sheet_name)

    df = pd.DataFrame(worksheet.get_all_records())
    df.columns = [c.strip() for c in df.columns]
    return df

# Initial load
if st.session_state.data is None:
    with st.spinner("Loading customer database..."):
        st.session_state.data = load_data()
        st.session_state.last_update = datetime.now()
        st.success(f"Database loaded successfully: {len(st.session_state.data)} records")

df = st.session_state.data

# ==========================
# Search Section
# ==========================
st.markdown("---")
col1, col2 = st.columns([3, 1])

with col1:
    bzid_input = st.text_input(
        "🔍 ENTER CUSTOMER BZID (Mandatory)",
        placeholder="Example: BZID-1305378359",
        key="search_input",
        help="Copy BZID from ticket and paste here"
    )

with col2:
    st.markdown("<br>", unsafe_allow_html=True)
    search_btn = st.button(
        "Search Database",
        use_container_width=True,
        disabled=not bool(bzid_input)
    )

# ==========================
# ===== FIX #1: Search ONLY on button click =====
# ==========================
if search_btn and bzid_input and df is not None:

    bzid_col = next((c for c in df.columns if "bzid" in c.lower()), None)

    if not bzid_col:
        st.error("BZID column not found in database.")
    else:
        search_term = bzid_input.strip().replace("BZID-", "")
        customer_data = None

        for _, row in df.iterrows():
            cell = str(row[bzid_col]).replace("BZID-", "").strip()
            if cell == search_term:
                customer_data = row
                break

        if customer_data is None:
            st.error(f"Customer with BZID '{bzid_input}' not found.")
        else:
            st.success("Customer record found")

            # ==========================
            # Customer Summary
            # ==========================
            st.markdown("### 📋 Customer Profile")

            col1, col2, col3 = st.columns(3)

            with col1:
                st.write(f"**BZID:** {customer_data[bzid_col]}")
                st.write(f"**Cluster:** {customer_data.get('cluster', 'NA')}")

            with col2:
                st.write(f"**Hub:** {customer_data.get('hub', 'NA')}")
                st.write(f"**CD Flag:** {customer_data.get('CD_flag', 'NA')}")

            with col3:
                if "psr_pct" in df.columns:
                    st.metric("PSR %", f"{customer_data.get('psr_pct', 0):.2%}")

            # ==========================
            # ===== FIX #3: Copy-paste block =====
            # ==========================
            ticket_text = f"""
BZID: {customer_data[bzid_col]}
Cluster: {customer_data.get('cluster', 'NA')}
Hub: {customer_data.get('hub', 'NA')}
CD Flag: {customer_data.get('CD_flag', 'NA')}
PSR %: {customer_data.get('psr_pct', 'NA')}
PSR Requested GMV: {customer_data.get('psr_requested_gmv', 'NA')}
Delivered GMV: {customer_data.get('del_gmv', 'NA')}
""".strip()

            st.markdown("### 📋 Copy for Ticket Documentation")

            st.text_area(
                "Copy everything below and paste in ticket",
                ticket_text,
                height=180
            )

            # ==========================
            # Detailed Data (unchanged)
            # ==========================
            st.markdown("### 📊 Complete Customer Data")
            full_data = []
            for col in df.columns:
                val = customer_data[col]
                if pd.isna(val) or str(val).strip() == "":
                    continue
                full_data.append({
                    "Field": col.replace("_", " ").title(),
                    "Value": val
                })

            st.dataframe(
                pd.DataFrame(full_data),
                hide_index=True,
                use_container_width=True
            )

# ==========================
# Footer
# ==========================
st.markdown("""
<div class="footer">
    PSR CD Flag Dashboard v1.0 • Secure enterprise data access system<br>
    © 2024 Customer Intelligence Platform • All rights reserved
</div>
""", unsafe_allow_html=True)
