import streamlit as st
import pandas as pd
import gspread
from google.oauth2 import service_account

# Page setup - Simple and clean
st.set_page_config(
    page_title="PSR CD Flag Check",
    page_icon="🔍",
    layout="centered"
)

# Simple title
st.title("🔍 PSR CD Flag Check")

# Initialize session state
if 'data' not in st.session_state:
    st.session_state.data = None

# Function to load data once (cached)
@st.cache_data(ttl=300)  # Cache for 5 minutes
def load_data():
    try:
        # Get credentials from secrets
        creds_dict = dict(st.secrets["gcp_service_account"])
        
        # Create credentials
        credentials = service_account.Credentials.from_service_account_info(
            creds_dict,
            scopes=[
                'https://www.googleapis.com/auth/spreadsheets',
                'https://www.googleapis.com/auth/drive'
            ]
        )
        
        # Authorize
        client = gspread.authorize(credentials)
        
        # Get sheet ID from secrets
        sheet_id = st.secrets["sheets"]["sheet_id"]
        sheet_name = st.secrets["sheets"].get("sheet_name", "Main Sheet")
        
        # Open sheet
        sheet = client.open_by_key(sheet_id)
        
        # Get worksheet
        try:
            worksheet = sheet.worksheet(sheet_name)
        except:
            worksheet = sheet.get_worksheet(0)  # First sheet
        
        # Get all data
        data = worksheet.get_all_records()
        
        # Convert to DataFrame
        df = pd.DataFrame(data)
        
        return df
        
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return None

# Auto-load data
if st.session_state.data is None:
    with st.spinner("Loading data..."):
        df = load_data()
        if df is not None and not df.empty:
            st.session_state.data = df
            st.success(f"✅ Ready! Found {len(df)} records")
        else:
            st.error("Could not load data. Check configuration.")

# Search box
st.markdown("---")
bzid_input = st.text_input(
    "**Enter BZID:**",
    placeholder="Example: BZID-1305378359 or 1305378359",
    key="search_input"
)

# Search when Enter is pressed or when text changes
if bzid_input:
    if st.session_state.data is not None:
        df = st.session_state.data
        
        # Find BZID column (case-insensitive)
        bzid_col = None
        for col in df.columns:
            if 'bzid' in col.lower():
                bzid_col = col
                break
        
        if bzid_col is None:
            st.error("No BZID column found in data!")
            st.write("Available columns:", list(df.columns))
        else:
            # Clean search term
            search_term = str(bzid_input).strip()
            
            # Remove BZID- prefix if present
            if search_term.upper().startswith('BZID-'):
                search_term = search_term[5:]
            
            # Search for the BZID
            found = False
            for idx, row in df.iterrows():
                cell_value = str(row[bzid_col]).strip()
                
                # Check if search term matches (with or without BZID- prefix)
                if (search_term == cell_value or 
                    f"BZID-{search_term}" == cell_value or
                    search_term == cell_value.replace('BZID-', '')):
                    
                    # Display the data in a clean format
                    st.markdown("---")
                    st.markdown("### 📋 Customer Data")
                    
                    # Create a nice display
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.metric("BZID", row[bzid_col])
                        if 'cluster' in df.columns:
                            st.metric("Cluster", row['cluster'])
                        if 'hub' in df.columns:
                            st.metric("Hub", row['hub'])
                    
                    with col2:
                        if 'CD_flag' in df.columns:
                            flag_value = row['CD_flag']
                            flag_color = "green" if "Do not ask" in str(flag_value) else "red"
                            st.metric("CD Flag", flag_value)
                        
                        if 'del_gmv' in df.columns and pd.notna(row['del_gmv']):
                            try:
                                gmv_value = float(row['del_gmv'])
                                st.metric("Delivered GMV", f"₹{gmv_value:,.2f}")
                            except:
                                pass
                    
                    # Show all data in a table
                    st.markdown("### 📊 Complete Details")
                    
                    # Create a display dataframe
                    display_data = []
                    for col in df.columns:
                        value = row[col]
                        
                        # Skip NaN values
                        if pd.isna(value) or value == "":
                            continue
                        
                        # Format values
                        if 'gmv' in col.lower() and pd.notna(value):
                            try:
                                value = f"₹{float(value):,.2f}"
                            except:
                                pass
                        elif 'pct' in col.lower() and pd.notna(value):
                            try:
                                value = f"{float(value):.2%}"
                            except:
                                pass
                        
                        display_data.append({
                            "Field": col,
                            "Value": value
                        })
                    
                    # Display as table
                    display_df = pd.DataFrame(display_data)
                    st.dataframe(
                        display_df,
                        column_config={
                            "Field": st.column_config.Column(width="medium"),
                            "Value": st.column_config.Column(width="large")
                        },
                        hide_index=True,
                        use_container_width=True
                    )
                    
                    found = True
                    break
            
            if not found:
                st.error(f"❌ BZID '{bzid_input}' not found")
                
                # Show available BZIDs
                if len(df) > 0:
                    available = df[bzid_col].head(10).tolist()
                    st.info(f"Try these BZIDs: {', '.join(map(str, available))}")
    
    else:
        st.warning("Data not loaded yet. Please wait...")

# Simple footer
st.markdown("---")
st.caption("Enter BZID → Get All Data • Simple & Fast")
