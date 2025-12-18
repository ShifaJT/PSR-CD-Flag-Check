import streamlit as st
import pandas as pd
import gspread
from google.oauth2 import service_account
import json

# Page configuration - Simple and clean
st.set_page_config(
    page_title="BZID Lookup",
    page_icon="🔍",
    layout="centered"
)

# Minimal CSS
st.markdown("""
<style>
    .title {
        font-size: 2.5rem;
        color: #2563eb;
        text-align: center;
        margin-bottom: 1rem;
        font-weight: bold;
    }
    .search-box {
        background: white;
        border-radius: 10px;
        padding: 20px;
        margin: 20px 0;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }
    .data-card {
        background: #f8fafc;
        border-radius: 10px;
        padding: 20px;
        margin: 15px 0;
        border-left: 4px solid #2563eb;
    }
    .data-row {
        display: flex;
        justify-content: space-between;
        padding: 8px 0;
        border-bottom: 1px solid #e2e8f0;
    }
    .data-label {
        color: #64748b;
        font-weight: 600;
    }
    .data-value {
        color: #1e293b;
        font-weight: 500;
    }
    .flag-badge {
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.9rem;
        font-weight: 600;
    }
    .flag-green {
        background: #dcfce7;
        color: #16a34a;
    }
    .flag-red {
        background: #fee2e2;
        color: #dc2626;
    }
</style>
""", unsafe_allow_html=True)

# Title
st.markdown('<h1 class="title">🔍 BZID Lookup</h1>', unsafe_allow_html=True)

# Initialize session state
if 'data_loaded' not in st.session_state:
    st.session_state.data_loaded = False
    st.session_state.all_data = None

# Load Google Sheets data from secrets
def load_google_sheets():
    """Load data from Google Sheets using secrets"""
    try:
        # Check if secrets are configured
        if 'gcp_service_account' not in st.secrets:
            st.error("Google Sheets credentials not found in secrets.")
            return False
        
        # Get credentials from secrets
        credentials_dict = dict(st.secrets["gcp_service_account"])
        
        # Define scope
        scope = ['https://spreadsheets.google.com/feeds',
                'https://www.googleapis.com/auth/drive']
        
        # Create credentials
        credentials = service_account.Credentials.from_service_account_info(
            credentials_dict, scopes=scope
        )
        
        # Authorize and open sheet
        client = gspread.authorize(credentials)
        
        # Get sheet from secrets or use default
        sheet_id = st.secrets.get("sheets", {}).get("sheet_id", "")
        sheet_name = st.secrets.get("sheets", {}).get("sheet_name", "Main Sheet")
        
        if not sheet_id:
            st.error("Google Sheet ID not found in secrets.")
            return False
        
        # Open the sheet
        sheet = client.open_by_key(sheet_id)
        
        # Get the worksheet
        try:
            worksheet = sheet.worksheet(sheet_name)
        except:
            worksheet = sheet.get_worksheet(0)  # First sheet
        
        # Get all data
        data = worksheet.get_all_records()
        df = pd.DataFrame(data)
        
        if df.empty:
            st.error("No data found in the sheet.")
            return False
        
        st.session_state.all_data = df
        st.session_state.data_loaded = True
        return True
        
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return False

# Auto-load data on first run
if not st.session_state.data_loaded:
    with st.spinner("Loading data from Google Sheets..."):
        if load_google_sheets():
            st.success(f"✅ Loaded {len(st.session_state.all_data)} records")
        else:
            st.warning("Data not loaded. Check secrets configuration.")

# Search Interface
st.markdown('<div class="search-box">', unsafe_allow_html=True)

bzid_input = st.text_input(
    "**Enter BZID:**",
    placeholder="Example: 1305378359 or BZID-1305378359",
    key="bzid_input"
)

search_btn = st.button("🔍 Search", type="primary", use_container_width=True)

st.markdown('</div>', unsafe_allow_html=True)

# Search function
def search_player(bzid):
    """Search for player by BZID"""
    if st.session_state.all_data is None:
        return None
    
    # Clean the BZID
    bzid = str(bzid).strip()
    
    # Remove BZID- prefix if present in search
    if bzid.startswith('BZID-'):
        bzid = bzid[5:]
    
    # Search in the dataframe
    df = st.session_state.all_data
    
    # Try exact match
    for idx, row in df.iterrows():
        # Clean the BZID in the dataframe
        db_bzid = str(row.get('BZID', '')).strip()
        if db_bzid.startswith('BZID-'):
            db_bzid_clean = db_bzid[5:]
        else:
            db_bzid_clean = db_bzid
        
        if bzid == db_bzid_clean:
            return row
    
    return None

# Handle search
if search_btn and bzid_input:
    if st.session_state.data_loaded:
        player_data = search_player(bzid_input)
        
        if player_data is not None:
            st.markdown('<div class="data-card">', unsafe_allow_html=True)
            
            # Display all data in clean format
            st.markdown(f"### 📋 **Player Data:** {player_data.get('BZID', 'N/A')}")
            st.markdown("---")
            
            # Display all columns
            for col in st.session_state.all_data.columns:
                if col in player_data:
                    value = player_data[col]
                    
                    # Format numeric values
                    if isinstance(value, (int, float)):
                        if 'gmv' in col.lower() or 'pct' in col.lower():
                            try:
                                if 'pct' in col.lower():
                                    value = f"{float(value):.2f}%"
                                else:
                                    value = f"₹{float(value):,.2f}"
                            except:
                                pass
                    
                    # Special formatting for CD_flag
                    if col == 'CD_flag':
                        flag_class = "flag-green" if "Do not ask" in str(value) else "flag-red"
                        st.markdown(f"""
                        <div class="data-row">
                            <span class="data-label">{col}:</span>
                            <span class="flag-badge {flag_class}">{value}</span>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown(f"""
                        <div class="data-row">
                            <span class="data-label">{col}:</span>
                            <span class="data-value">{value}</span>
                        </div>
                        """, unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Optional: Show raw data
            with st.expander("📊 View Raw Data"):
                st.write(player_data.to_dict())
                
        else:
            st.error(f"❌ No data found for BZID: {bzid_input}")
            
            # Show suggestions if available
            if st.session_state.all_data is not None:
                all_bzids = []
                for bzid in st.session_state.all_data['BZID']:
                    if isinstance(bzid, str) and 'BZID-' in bzid:
                        all_bzids.append(bzid[5:])
                    else:
                        all_bzids.append(str(bzid))
                
                st.info(f"Try these BZIDs: {', '.join(all_bzids[:5])}...")
    else:
        st.warning("Please wait for data to load...")

# Display data stats if loaded
if st.session_state.data_loaded:
    st.sidebar.markdown("### 📊 Data Statistics")
    
    df = st.session_state.all_data
    
    # Basic stats
    st.sidebar.metric("Total Records", len(df))
    
    if 'cluster' in df.columns:
        unique_clusters = df['cluster'].nunique()
        st.sidebar.metric("Clusters", unique_clusters)
    
    if 'hub' in df.columns:
        unique_hubs = df['hub'].nunique()
        st.sidebar.metric("Hubs", unique_hubs)
    
    if 'CD_flag' in df.columns:
        do_not_ask_count = df['CD_flag'].str.contains('Do not ask', na=False).sum()
        st.sidebar.metric("Do Not Ask", do_not_ask_count)
    
    # Recent searches
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🔍 Quick Search")
    
    # Show first few BZIDs for quick access
    if 'BZID' in df.columns:
        sample_bzids = df['BZID'].head(5).tolist()
        for bzid in sample_bzids:
            if st.sidebar.button(f"🔎 {bzid}"):
                st.session_state.bzid_input = str(bzid)
                st.rerun()

# Simple footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #64748b; font-size: 0.9rem;'>"
    "Enter BZID → Get All Data • Instant Results"
    "</div>",
    unsafe_allow_html=True
)
