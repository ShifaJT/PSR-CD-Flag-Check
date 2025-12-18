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

# Professional CSS
st.markdown("""
<style>
    /* Professional color scheme */
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
    
    .main-title {
        font-size: 2.5rem;
        color: var(--gray-900);
        font-weight: 700;
        margin-bottom: 0.5rem;
        letter-spacing: -0.025em;
    }
    
    .subtitle {
        color: var(--gray-700);
        font-size: 1.1rem;
        margin-bottom: 2rem;
        font-weight: 400;
    }
    
    /* Header with logo */
    .header-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 12px;
        margin-bottom: 2rem;
        color: white;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    
    /* Search container */
    .search-container {
        background: white;
        border-radius: 12px;
        padding: 2rem;
        margin: 2rem 0;
        border: 1px solid var(--gray-200);
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
    }
    
    .search-input {
        background: var(--gray-50) !important;
        border: 2px solid var(--gray-200) !important;
        border-radius: 8px !important;
        padding: 1rem 1.5rem !important;
        font-size: 1rem !important;
        color: var(--gray-900) !important;
        transition: all 0.2s !important;
    }
    
    .search-input:focus {
        border-color: var(--primary) !important;
        box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1) !important;
    }
    
    /* Primary button */
    .stButton > button {
        background: var(--primary) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.75rem 2rem !important;
        font-size: 1rem !important;
        font-weight: 500 !important;
        transition: all 0.2s !important;
        width: 100%;
    }
    
    .stButton > button:hover {
        background: var(--primary-dark) !important;
        transform: translateY(-1px);
        box-shadow: 0 4px 6px -1px rgba(37, 99, 235, 0.2);
    }
    
    /* Data card */
    .data-card {
        background: white;
        border-radius: 12px;
        padding: 2rem;
        margin: 1.5rem 0;
        border: 1px solid var(--gray-200);
        box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
    }
    
    .data-card-header {
        border-bottom: 1px solid var(--gray-200);
        padding-bottom: 1rem;
        margin-bottom: 1.5rem;
    }
    
    /* Status badges */
    .status-badge {
        display: inline-flex;
        align-items: center;
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.875rem;
        font-weight: 500;
        gap: 0.25rem;
    }
    
    .status-success {
        background-color: #dcfce7;
        color: #166534;
    }
    
    .status-warning {
        background-color: #fef3c7;
        color: #92400e;
    }
    
    .status-neutral {
        background-color: var(--gray-100);
        color: var(--gray-700);
    }
    
    /* Metric cards */
    .metric-container {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1rem;
        margin: 1.5rem 0;
    }
    
    .metric-card {
        background: white;
        border-radius: 8px;
        padding: 1.5rem;
        border: 1px solid var(--gray-200);
        text-align: center;
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: var(--gray-900);
        margin-bottom: 0.25rem;
    }
    
    .metric-label {
        font-size: 0.875rem;
        color: var(--gray-700);
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    /* Data table styling */
    .data-table {
        width: 100%;
        border-collapse: separate;
        border-spacing: 0;
    }
    
    .data-table th {
        background: var(--gray-50);
        padding: 0.75rem 1rem;
        text-align: left;
        font-weight: 600;
        color: var(--gray-700);
        border-bottom: 1px solid var(--gray-200);
        font-size: 0.875rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    .data-table td {
        padding: 1rem;
        border-bottom: 1px solid var(--gray-200);
        color: var(--gray-700);
    }
    
    .data-table tr:hover {
        background: var(--gray-50);
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.5rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px !important;
        padding: 0.75rem 1.5rem !important;
        font-weight: 500 !important;
    }
    
    /* Footer */
    .footer {
        text-align: center;
        color: var(--gray-500);
        font-size: 0.875rem;
        margin-top: 3rem;
        padding-top: 1rem;
        border-top: 1px solid var(--gray-200);
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'data' not in st.session_state:
    st.session_state.data = None
if 'last_update' not in st.session_state:
    st.session_state.last_update = None
if 'search_history' not in st.session_state:
    st.session_state.search_history = []

# Professional header
col1, col2 = st.columns([3, 1])
with col1:
    st.markdown('<h1 class="main-title">PSR CD Flag Dashboard</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Enterprise-grade customer data lookup system</p>', unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div style="text-align: right; padding-top: 0.5rem;">
        <div style="font-size: 0.875rem; color: #6b7280;">Last Updated</div>
        <div style="font-weight: 500; color: #111827;">{datetime.now().strftime('%d %b %Y, %H:%M')}</div>
    </div>
    """, unsafe_allow_html=True)

# Load data function
@st.cache_data(ttl=300)
def load_data():
    try:
        creds_dict = dict(st.secrets["gcp_service_account"])
        
        credentials = service_account.Credentials.from_service_account_info(
            creds_dict,
            scopes=[
                'https://www.googleapis.com/auth/spreadsheets',
                'https://www.googleapis.com/auth/drive'
            ]
        )
        
        client = gspread.authorize(credentials)
        
        sheet_id = st.secrets["sheets"]["sheet_id"]
        sheet_name = st.secrets["sheets"].get("sheet_name", "CD-PSR Flag")
        
        sheet = client.open_by_key(sheet_id)
        
        try:
            worksheet = sheet.worksheet(sheet_name)
        except:
            worksheet = sheet.get_worksheet(0)
        
        data = worksheet.get_all_records()
        df = pd.DataFrame(data)
        
        # Clean column names
        df.columns = [col.strip() for col in df.columns]
        
        return df
        
    except Exception as e:
        st.error(f"Data connection error: {str(e)}")
        return None

# Load data
if st.session_state.data is None:
    with st.spinner("Loading customer database..."):
        df = load_data()
        if df is not None and not df.empty:
            st.session_state.data = df
            st.session_state.last_update = datetime.now()
            st.success(f"✓ Database loaded successfully: {len(df)} records")
        else:
            st.error("Unable to load data. Please check configuration.")

# Sidebar with statistics
with st.sidebar:
    st.markdown("### 📈 Dashboard")
    
    if st.session_state.data is not None:
        df = st.session_state.data
        
        # Basic stats
        st.metric("Total Records", len(df))
        
        if 'cluster' in df.columns:
            st.metric("Active Clusters", df['cluster'].nunique())
        
        if 'CD_flag' in df.columns:
            flag_counts = df['CD_flag'].value_counts()
            st.metric("Do Not Ask", flag_counts.get('Do not ask for image', 0))
        
        st.markdown("---")
        
        # Quick actions
        st.markdown("### ⚡ Quick Actions")
        
        if st.button("🔄 Refresh Data", use_container_width=True):
            st.cache_data.clear()
            st.session_state.data = None
            st.rerun()
        
        # Recent searches
        if st.session_state.search_history:
            st.markdown("### 📋 Recent Searches")
            for bzid in st.session_state.search_history[-5:]:
                if st.button(f"🔍 {bzid}", key=f"recent_{bzid}", use_container_width=True):
                    st.session_state.search_input = bzid
                    st.rerun()
        
        st.markdown("---")
        
        # System info
        st.markdown("### ℹ️ System Info")
        st.info(f"Connected to Google Sheets")
        if st.session_state.last_update:
            st.caption(f"Updated: {st.session_state.last_update.strftime('%H:%M:%S')}")

# Main content area
st.markdown('<div class="search-container">', unsafe_allow_html=True)

col1, col2 = st.columns([3, 1])
with col1:
    bzid_input = st.text_input(
        "Enter Customer BZID",
        placeholder="BZID-1305378359 or 1305378359",
        key="search_input",
        help="Enter the customer's BZID to retrieve all associated data"
    )

with col2:
    st.markdown("<br>", unsafe_allow_html=True)
    search_btn = st.button("Search Database", use_container_width=True)

st.markdown('</div>', unsafe_allow_html=True)

# Handle search
if (search_btn or bzid_input) and bzid_input and st.session_state.data is not None:
    df = st.session_state.data
    
    # Find BZID column
    bzid_col = None
    for col in df.columns:
        if 'bzid' in col.lower():
            bzid_col = col
            break
    
    if bzid_col:
        # Add to search history
        if bzid_input not in st.session_state.search_history:
            st.session_state.search_history.append(bzid_input)
            if len(st.session_state.search_history) > 10:
                st.session_state.search_history.pop(0)
        
        # Clean search term
        search_term = str(bzid_input).strip()
        if search_term.upper().startswith('BZID-'):
            search_term = search_term[5:]
        
        # Search for customer
        customer_data = None
        for idx, row in df.iterrows():
            cell_value = str(row[bzid_col]).strip()
            if (search_term == cell_value or 
                f"BZID-{search_term}" == cell_value or
                search_term == cell_value.replace('BZID-', '')):
                customer_data = row
                break
        
        if customer_data is not None:
            # Display results
            st.markdown('<div class="data-card">', unsafe_allow_html=True)
            
            # Customer header
            st.markdown('<div class="data-card-header">', unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                st.markdown(f"### 📋 Customer Profile")
                st.markdown(f"**BZID:** `{customer_data[bzid_col]}`")
            
            with col2:
                if 'cluster' in df.columns:
                    st.markdown(f"**Cluster:** {customer_data.get('cluster', 'N/A')}")
                if 'hub' in df.columns:
                    st.markdown(f"**Hub:** {customer_data.get('hub', 'N/A')}")
            
            with col3:
                if 'CD_flag' in df.columns:
                    flag_value = customer_data['CD_flag']
                    if "Do not ask" in str(flag_value):
                        st.markdown('<span class="status-badge status-success">✓ Do Not Ask</span>', unsafe_allow_html=True)
                    else:
                        st.markdown('<span class="status-badge status-warning">⚠ Ask for Image</span>', unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Key metrics
            st.markdown("### Key Metrics")
            
            metric_cols = st.columns(4)
            
            with metric_cols[0]:
                if 'psr_requested_gmv' in df.columns and pd.notna(customer_data['psr_requested_gmv']):
                    try:
                        value = float(customer_data['psr_requested_gmv'])
                        st.metric("PSR Requested", f"₹{value:,.0f}")
                    except:
                        pass
            
            with metric_cols[1]:
                if 'del_gmv' in df.columns and pd.notna(customer_data['del_gmv']):
                    try:
                        value = float(customer_data['del_gmv'])
                        st.metric("Delivered GMV", f"₹{value:,.0f}")
                    except:
                        pass
            
            with metric_cols[2]:
                if 'psr_pct' in df.columns and pd.notna(customer_data['psr_pct']):
                    try:
                        value = float(customer_data['psr_pct'])
                        st.metric("PSR Percentage", f"{value:.2%}")
                    except:
                        pass
            
            with metric_cols[3]:
                # Calculate utilization if possible
                if all(col in df.columns for col in ['psr_requested_gmv', 'del_gmv']):
                    try:
                        requested = float(customer_data['psr_requested_gmv']) if pd.notna(customer_data['psr_requested_gmv']) else 0
                        delivered = float(customer_data['del_gmv']) if pd.notna(customer_data['del_gmv']) else 0
                        utilization = (requested / delivered * 100) if delivered > 0 else 0
                        st.metric("Utilization", f"{utilization:.1f}%")
                    except:
                        pass
            
            # Detailed data in tabs
            st.markdown("### Customer Details")
            
            tab1, tab2 = st.tabs(["📊 Summary View", "📋 Complete Data"])
            
            with tab1:
                # Display key information in a clean table
                key_fields = ['cluster', 'hub', 'psr_requested_gmv', 'del_gmv', 'psr_pct', 'CD_flag']
                available_fields = [f for f in key_fields if f in df.columns]
                
                summary_data = []
                for field in available_fields:
                    value = customer_data[field]
                    if pd.isna(value) or str(value).strip() == '':
                        continue
                    
                    # Format values
                    display_value = str(value)
                    if 'gmv' in field:
                        try:
                            display_value = f"₹{float(value):,.2f}"
                        except:
                            pass
                    elif 'pct' in field:
                        try:
                            display_value = f"{float(value):.2%}"
                        except:
                            pass
                    
                    summary_data.append({
                        "Field": field.replace('_', ' ').title(),
                        "Value": display_value
                    })
                
                if summary_data:
                    summary_df = pd.DataFrame(summary_data)
                    st.dataframe(
                        summary_df,
                        column_config={
                            "Field": st.column_config.Column(width="medium"),
                            "Value": st.column_config.Column(width="large")
                        },
                        hide_index=True,
                        use_container_width=True
                    )
            
            with tab2:
                # Display all data
                all_data = []
                for col in df.columns:
                    value = customer_data[col]
                    if pd.isna(value) or str(value).strip() == '':
                        continue
                    
                    # Format values
                    display_value = str(value)
                    if 'gmv' in col.lower():
                        try:
                            display_value = f"₹{float(value):,.2f}"
                        except:
                            pass
                    elif 'pct' in col.lower():
                        try:
                            display_value = f"{float(value):.2%}"
                        except:
                            pass
                    
                    all_data.append({
                        "Field": col.replace('_', ' ').title(),
                        "Value": display_value
                    })
                
                if all_data:
                    all_df = pd.DataFrame(all_data)
                    st.dataframe(
                        all_df,
                        column_config={
                            "Field": st.column_config.Column(width="medium"),
                            "Value": st.column_config.Column(width="large")
                        },
                        hide_index=True,
                        use_container_width=True
                    )
            
            # Export options
            with st.expander("📥 Export Options"):
                col1, col2 = st.columns(2)
                
                with col1:
                    # JSON export
                    json_data = customer_data.to_dict() if hasattr(customer_data, 'to_dict') else dict(customer_data)
                    st.download_button(
                        label="Download as JSON",
                        data=pd.Series(json_data).to_json(indent=2),
                        file_name=f"{customer_data[bzid_col]}_data.json",
                        mime="application/json",
                        use_container_width=True
                    )
                
                with col2:
                    # CSV export
                    csv_data = pd.DataFrame([customer_data]).to_csv(index=False)
                    st.download_button(
                        label="Download as CSV",
                        data=csv_data,
                        file_name=f"{customer_data[bzid_col]}_data.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
            
            st.markdown('</div>', unsafe_allow_html=True)
            
        else:
            st.error(f"Customer with BZID '{bzid_input}' not found in the database.")
            
            # Show available BZIDs for reference
            available_bzids = df[bzid_col].dropna().unique()[:8]
            st.info("**Available BZIDs for reference:**")
            cols = st.columns(4)
            for i, bzid in enumerate(available_bzids):
                with cols[i % 4]:
                    if st.button(str(bzid), key=f"suggest_{i}", use_container_width=True):
                        st.session_state.search_input = str(bzid)
                        st.rerun()
    
    else:
        st.error("Database structure error: No BZID column found.")

# Empty state
elif st.session_state.data is None:
    st.info("👈 Configure the application in the sidebar to begin searching.")

# Footer
st.markdown("""
<div class="footer">
    <p>PSR CD Flag Dashboard v1.0 • Secure enterprise data access system</p>
    <p>© 2024 Customer Intelligence Platform • All rights reserved</p>
</div>
""", unsafe_allow_html=True)
