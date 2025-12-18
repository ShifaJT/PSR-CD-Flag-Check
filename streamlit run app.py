import streamlit as st
import pandas as pd
import gspread
from google.oauth2 import service_account
import json
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="BZID Data Lookup",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Simple CSS for clean UI
st.markdown("""
<style>
    .main-title {
        font-size: 2.5rem;
        color: #1E3A8A;
        text-align: center;
        margin-bottom: 1rem;
        font-weight: 700;
    }
    .data-card {
        background: #f8f9fa;
        border-radius: 10px;
        padding: 20px;
        margin: 10px 0;
        border-left: 4px solid #1E3A8A;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    .metric-box {
        background: white;
        border-radius: 8px;
        padding: 15px;
        margin: 5px;
        text-align: center;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    .metric-value {
        font-size: 1.8rem;
        font-weight: bold;
        color: #1E3A8A;
        margin-bottom: 5px;
    }
    .metric-label {
        font-size: 0.9rem;
        color: #666;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .flag-active {
        background-color: #fee2e2;
        color: #dc2626;
        padding: 4px 12px;
        border-radius: 20px;
        font-weight: 600;
        display: inline-block;
    }
    .flag-inactive {
        background-color: #dcfce7;
        color: #16a34a;
        padding: 4px 12px;
        border-radius: 20px;
        font-weight: 600;
        display: inline-block;
    }
    .search-box {
        background: white;
        border-radius: 10px;
        padding: 30px;
        margin: 20px 0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

# Title
st.markdown('<h1 class="main-title">🔍 BZID Data Lookup</h1>', unsafe_allow_html=True)
st.markdown('<p style="text-align: center; color: #666; margin-bottom: 30px;">Enter BZID to get complete player data instantly</p>', unsafe_allow_html=True)

# Initialize session state
if 'all_data' not in st.session_state:
    st.session_state.all_data = None
if 'last_search' not in st.session_state:
    st.session_state.last_search = None

# Sidebar for Google Sheets Configuration
with st.sidebar:
    st.markdown("### ⚙️ Google Sheets Setup")
    
    # JSON key input
    json_key = st.text_area(
        "Paste Google Service Account JSON Key:",
        height=200,
        help="Paste the complete JSON key from Google Cloud Console"
    )
    
    sheet_url = st.text_input(
        "Google Sheet URL:",
        placeholder="https://docs.google.com/spreadsheets/d/...",
        help="The full URL of your Google Sheet"
    )
    
    sheet_name = st.text_input(
        "Sheet Name:",
        value="Main Sheet",
        help="Name of the worksheet (tab) in your Google Sheet"
    )
    
    connect_btn = st.button("📥 Load Data from Google Sheets", type="primary", use_container_width=True)
    
    if connect_btn:
        if json_key and sheet_url:
            try:
                # Parse JSON key
                credentials_dict = json.loads(json_key)
                
                # Define scope
                scope = ['https://spreadsheets.google.com/feeds',
                        'https://www.googleapis.com/auth/drive']
                
                # Authenticate
                credentials = service_account.Credentials.from_service_account_info(
                    credentials_dict, scopes=scope
                )
                client = gspread.authorize(credentials)
                
                # Extract sheet ID from URL
                if 'spreadsheets/d/' in sheet_url:
                    sheet_id = sheet_url.split('spreadsheets/d/')[1].split('/')[0]
                    sheet = client.open_by_key(sheet_id)
                    
                    # Get worksheet
                    try:
                        worksheet = sheet.worksheet(sheet_name)
                    except:
                        worksheet = sheet.get_worksheet(0)  # Fallback to first sheet
                    
                    # Get all data
                    data = worksheet.get_all_records()
                    df = pd.DataFrame(data)
                    
                    if not df.empty:
                        st.session_state.all_data = df
                        st.success(f"✅ Loaded {len(df)} records from Google Sheets")
                        
                        # Show data preview
                        st.markdown("### 📊 Data Preview")
                        st.dataframe(df.head(), use_container_width=True)
                        
                        # Show column info
                        st.markdown(f"**Columns:** {', '.join(df.columns.tolist())}")
                    else:
                        st.error("No data found in the sheet")
                        
                else:
                    st.error("Invalid Google Sheets URL format")
                    
            except Exception as e:
                st.error(f"Error: {str(e)}")
        else:
            st.warning("Please enter both JSON key and Sheet URL")

# Main Search Interface
st.markdown('<div class="search-box">', unsafe_allow_html=True)

col1, col2 = st.columns([2, 1])

with col1:
    bzid_input = st.text_input(
        "Enter BZID:",
        placeholder="e.g., BZID-1305378359 or 1305378359",
        key="bzid_input"
    )

with col2:
    st.markdown("<br>", unsafe_allow_html=True)
    search_btn = st.button("🔍 Search BZID", type="primary", use_container_width=True)

st.markdown('</div>', unsafe_allow_html=True)

# Search Function
def search_bzid_data(bzid, df):
    """Search for BZID in the dataframe"""
    if df is None or df.empty:
        return None
    
    # Clean the BZID input
    bzid_clean = str(bzid).strip()
    
    # Try with BZID- prefix
    if not bzid_clean.startswith('BZID-'):
        bzid_with_prefix = f"BZID-{bzid_clean}"
    else:
        bzid_with_prefix = bzid_clean
    
    # Search in BZID column
    if 'BZID' in df.columns:
        result = df[df['BZID'] == bzid_with_prefix]
        if not result.empty:
            return result.iloc[0]
        
        # Try without prefix
        result = df[df['BZID'] == bzid_clean]
        if not result.empty:
            return result.iloc[0]
        
        # Try partial match
        result = df[df['BZID'].str.contains(bzid_clean, na=False)]
        if not result.empty:
            return result.iloc[0]
    
    return None

# Handle Search
if search_btn and bzid_input:
    if st.session_state.all_data is not None:
        with st.spinner("Searching..."):
            player_data = search_bzid_data(bzid_input, st.session_state.all_data)
            st.session_state.last_search = player_data
            
            if player_data is not None:
                st.success(f"✅ Found data for BZID: {bzid_input}")
            else:
                st.error(f"❌ No data found for BZID: {bzid_input}")
    else:
        st.warning("⚠️ Please load data from Google Sheets first")

# Display Results
if st.session_state.last_search is not None:
    player_data = st.session_state.last_search
    
    # Display in a clean card
    st.markdown('<div class="data-card">', unsafe_allow_html=True)
    
    # Header
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown(f"### 📋 Player Data - {player_data.get('BZID', 'N/A')}")
    
    with col2:
        cd_flag = player_data.get('CD_flag', 'N/A')
        flag_class = "flag-inactive" if "Do not ask" in str(cd_flag) else "flag-active"
        st.markdown(f'<span class="{flag_class}">{cd_flag}</span>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Main Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown('<div class="metric-box">', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-value">{player_data.get("cluster", "N/A")}</div>', unsafe_allow_html=True)
        st.markdown('<div class="metric-label">CLUSTER</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="metric-box">', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-value">{player_data.get("hub", "N/A")}</div>', unsafe_allow_html=True)
        st.markdown('<div class="metric-label">HUB</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        psr_gmv = player_data.get("psr_requested_gmv", 0)
        if pd.isna(psr_gmv) or psr_gmv == "":
            psr_gmv = 0
        st.markdown('<div class="metric-box">', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-value">{psr_gmv:,.2f}</div>', unsafe_allow_html=True)
        st.markdown('<div class="metric-label">PSR REQUESTED GMV</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col4:
        del_gmv = player_data.get("del_gmv", 0)
        if pd.isna(del_gmv) or del_gmv == "":
            del_gmv = 0
        st.markdown('<div class="metric-box">', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-value">{float(del_gmv):,.2f}</div>', unsafe_allow_html=True)
        st.markdown('<div class="metric-label">DELIVERED GMV</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Additional Metrics
    col5, col6, col7 = st.columns(3)
    
    with col5:
        psr_pct = player_data.get("psr_pct", "0%")
        if pd.isna(psr_pct) or psr_pct == "":
            psr_pct = "0%"
        st.markdown('<div class="metric-box">', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-value">{psr_pct}</div>', unsafe_allow_html=True)
        st.markdown('<div class="metric-label">PSR PERCENTAGE</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col6:
        # Calculate utilization if both values exist
        psr_gmv_val = float(psr_gmv) if psr_gmv != 0 else 0
        del_gmv_val = float(del_gmv) if del_gmv != 0 else 0
        utilization = (psr_gmv_val / del_gmv_val * 100) if del_gmv_val != 0 else 0
        st.markdown('<div class="metric-box">', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-value">{utilization:.1f}%</div>', unsafe_allow_html=True)
        st.markdown('<div class="metric-label">UTILIZATION</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col7:
        # Status indicator
        status = "ACTIVE" if del_gmv_val > 0 else "INACTIVE"
        status_color = "#16a34a" if status == "ACTIVE" else "#dc2626"
        st.markdown('<div class="metric-box">', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-value" style="color: {status_color};">{status}</div>', unsafe_allow_html=True)
        st.markdown('<div class="metric-label">STATUS</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Detailed Data Table
    st.markdown("### 📊 Complete Data")
    
    # Create a clean display dataframe
    display_data = pd.DataFrame([
        {"Field": "BZID", "Value": player_data.get("BZID", "N/A")},
        {"Field": "Cluster", "Value": player_data.get("cluster", "N/A")},
        {"Field": "Hub", "Value": player_data.get("hub", "N/A")},
        {"Field": "PSR Requested GMV", "Value": f"{psr_gmv:,.2f}"},
        {"Field": "Delivered GMV", "Value": f"{float(del_gmv):,.2f}"},
        {"Field": "PSR Percentage", "Value": str(psr_pct)},
        {"Field": "CD Flag", "Value": player_data.get("CD_flag", "N/A")},
        {"Field": "Utilization Rate", "Value": f"{utilization:.2f}%"},
        {"Field": "Status", "Value": status}
    ])
    
    # Display as table
    st.dataframe(
        display_data,
        column_config={
            "Field": st.column_config.Column(width="medium"),
            "Value": st.column_config.Column(width="large")
        },
        hide_index=True,
        use_container_width=True
    )
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Export Options
    with st.expander("📥 Export Data"):
        col1, col2 = st.columns(2)
        
        with col1:
            # JSON export
            json_data = player_data.to_dict() if hasattr(player_data, 'to_dict') else dict(player_data)
            st.download_button(
                label="Download as JSON",
                data=json.dumps(json_data, indent=2),
                file_name=f"{player_data.get('BZID', 'player')}_data.json",
                mime="application/json",
                use_container_width=True
            )
        
        with col2:
            # CSV export
            csv_data = pd.DataFrame([player_data]).to_csv(index=False)
            st.download_button(
                label="Download as CSV",
                data=csv_data,
                file_name=f"{player_data.get('BZID', 'player')}_data.csv",
                mime="text/csv",
                use_container_width=True
            )

# Initial State Message
elif st.session_state.all_data is None:
    st.info("""
    ### 👋 Welcome to BZID Data Lookup
    
    To get started:
    1. **Configure Google Sheets** in the sidebar
    2. Enter your Google Service Account JSON key
    3. Provide your Google Sheet URL
    4. Click "Load Data from Google Sheets"
    5. Once data is loaded, search for any BZID
    
    This tool provides instant access to player data without waiting for Metabase!
    """)

# Data Loaded but No Search Yet
elif st.session_state.all_data is not None and st.session_state.last_search is None:
    st.success(f"✅ Data loaded successfully! Ready to search {len(st.session_state.all_data)} records")
    
    # Quick Stats
    col1, col2, col3 = st.columns(3)
    
    with col1:
        unique_clusters = st.session_state.all_data['cluster'].nunique() if 'cluster' in st.session_state.all_data.columns else 0
        st.metric("Unique Clusters", unique_clusters)
    
    with col2:
        unique_hubs = st.session_state.all_data['hub'].nunique() if 'hub' in st.session_state.all_data.columns else 0
        st.metric("Unique Hubs", unique_hubs)
    
    with col3:
        active_flags = len(st.session_state.all_data[st.session_state.all_data['CD_flag'].str.contains('Do not ask', na=False)])
        st.metric("Do Not Ask Flags", active_flags)

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #666; font-size: 0.9rem;'>"
    "🔍 BZID Data Lookup • Instant access to player data • Faster than Metabase"
    "</div>",
    unsafe_allow_html=True
)
