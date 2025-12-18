import streamlit as st
import pandas as pd
import gspread
from google.oauth2 import service_account

# Page setup
st.set_page_config(page_title="BZID Lookup", layout="centered")
st.title("🔍 BZID Lookup")

# Load Google Sheets
@st.cache_data
def load_data():
    try:
        creds_dict = dict(st.secrets["gcp_service_account"])
        creds = service_account.Credentials.from_service_account_info(
            creds_dict,
            scopes=['https://spreadsheets.google.com/feeds',
                   'https://www.googleapis.com/auth/drive']
        )
        client = gspread.authorize(creds)
        
        sheet = client.open_by_key(st.secrets["sheets"]["sheet_id"])
        worksheet = sheet.worksheet(st.secrets["sheets"]["sheet_name"])
        
        data = worksheet.get_all_records()
        return pd.DataFrame(data)
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return pd.DataFrame()

# Load data
df = load_data()
st.success(f"✅ Loaded {len(df)} records")

# Search
bzid = st.text_input("Enter BZID:", placeholder="1305378359")
if bzid:
    # Search logic
    if 'BZID' in df.columns:
        # Try different formats
        search_id = str(bzid).strip()
        if search_id.startswith('BZID-'):
            search_id = search_id[5:]
        
        # Search
        result = None
        for idx, row in df.iterrows():
            db_bzid = str(row['BZID']).strip()
            if db_bzid.endswith(search_id) or search_id in db_bzid:
                result = row
                break
        
        if result is not None:
            st.write("### 📋 Player Data")
            for col in df.columns:
                st.write(f"**{col}:** {result[col]}")
        else:
            st.error("BZID not found")
