import streamlit as st
import pandas as pd
import gspread
from google.oauth2 import service_account

# Page setup
st.set_page_config(
    page_title="BZID Lookup",
    page_icon="🔍",
    layout="centered"
)

st.title("🔍 BZID Lookup")

# Initialize session state
if 'df' not in st.session_state:
    st.session_state.df = None

# Debug: Show what's in secrets
with st.sidebar:
    st.markdown("### 🔧 Configuration Status")
    
    if 'gcp_service_account' in st.secrets:
        st.success("✅ Service Account Found")
        st.code(f"Email: {st.secrets['gcp_service_account']['client_email']}")
    else:
        st.error("❌ Service Account Missing")
        
    if 'sheets' in st.secrets:
        st.success("✅ Sheets Config Found")
        st.code(f"Sheet ID: {st.secrets['sheets']['sheet_id']}")
        st.code(f"Sheet Name: {st.secrets['sheets'].get('sheet_name', 'Main Sheet')}")
    else:
        st.error("❌ Sheets Config Missing")

# Load ALL data from Google Sheet with debugging
def load_all_sheet_data():
    try:
        # Get credentials
        creds = service_account.Credentials.from_service_account_info(
            dict(st.secrets["gcp_service_account"]),
            scopes=[
                'https://www.googleapis.com/auth/spreadsheets',
                'https://www.googleapis.com/auth/drive'
            ]
        )
        
        # Authorize client
        client = gspread.authorize(creds)
        
        # Open sheet
        sheet_id = st.secrets["sheets"]["sheet_id"]
        sheet = client.open_by_key(sheet_id)
        
        # List all worksheets
        worksheets = sheet.worksheets()
        st.sidebar.markdown(f"### 📄 Worksheets Found: {len(worksheets)}")
        for i, ws in enumerate(worksheets):
            st.sidebar.write(f"{i+1}. **{ws.title}** (Rows: {ws.row_count}, Cols: {ws.col_count})")
        
        # Try to load from configured sheet name
        sheet_name = st.secrets["sheets"].get("sheet_name", "Main Sheet")
        worksheet = None
        
        # Try to find the worksheet
        for ws in worksheets:
            if ws.title.lower() == sheet_name.lower():
                worksheet = ws
                break
        
        # If not found, use first sheet
        if worksheet is None:
            worksheet = worksheets[0]
            st.warning(f"Sheet '{sheet_name}' not found. Using first sheet: '{worksheet.title}'")
        else:
            st.success(f"Using sheet: '{worksheet.title}'")
        
        # Get ALL values (not just records) to debug structure
        all_values = worksheet.get_all_values()
        
        if not all_values:
            st.error("Sheet is completely empty!")
            return None, []
        
        st.info(f"Raw data shape: {len(all_values)} rows x {len(all_values[0])} columns")
        
        # Show raw data for debugging
        with st.expander("🔍 View Raw Sheet Data Structure"):
            st.write("**First few rows (as they appear in sheet):**")
            for i, row in enumerate(all_values[:10]):
                st.write(f"Row {i+1}: {row}")
        
        # Try to create DataFrame
        if len(all_values) > 1:
            # Try to use first row as headers
            headers = all_values[0]
            data = all_values[1:]
            
            # Check if headers look valid
            st.write(f"**Detected Headers:** {headers}")
            
            # Create DataFrame
            df = pd.DataFrame(data, columns=headers)
            
            # Clean up empty rows
            df = df.dropna(how='all')
            
            st.success(f"✅ Created DataFrame with {len(df)} rows and {len(df.columns)} columns")
            
            # Show column names
            st.write(f"**Column Names:** {list(df.columns)}")
            
            return df, headers
        else:
            st.error("Sheet has only header row, no data!")
            return None, all_values[0] if all_values else []
            
    except Exception as e:
        st.error(f"Error loading sheet: {str(e)}")
        return None, []

# Main app
st.markdown("---")

# Load data button
if st.button("📥 Load Data from Google Sheets", type="primary"):
    with st.spinner("Loading data..."):
        df, headers = load_all_sheet_data()
        
        if df is not None and not df.empty:
            st.session_state.df = df
            
            # Show preview
            st.markdown("### 📊 Data Preview")
            st.dataframe(df.head())
            
            # Show data types
            st.markdown("### 📝 Data Types")
            dtype_info = pd.DataFrame({
                'Column': df.columns,
                'Non-Null Count': df.count().values,
                'DType': df.dtypes.values
            })
            st.dataframe(dtype_info)
            
            # Check for BZID column
            bzid_columns = [col for col in df.columns if 'bzid' in col.lower()]
            if bzid_columns:
                st.success(f"✅ Found BZID column(s): {bzid_columns}")
                
                # Show sample BZIDs
                bzid_col = bzid_columns[0]
                sample_bzids = df[bzid_col].dropna().unique()[:10]
                st.write(f"**Sample BZIDs (first 10):**")
                for bzid in sample_bzids:
                    st.write(f"- {bzid}")
            else:
                st.warning("⚠️ No column containing 'BZID' found!")
                st.write(f"Available columns: {list(df.columns)}")

# If data is loaded, show search
if st.session_state.df is not None:
    df = st.session_state.df
    
    st.markdown("---")
    st.markdown("### 🔍 Search for BZID")
    
    # Find BZID column
    bzid_columns = [col for col in df.columns if 'bzid' in col.lower()]
    
    if not bzid_columns:
        st.error("No BZID column found in the data!")
        st.write("Available columns:", list(df.columns))
    else:
        bzid_col = bzid_columns[0]
        st.info(f"Using column: **'{bzid_col}'** for search")
        
        # Search input
        col1, col2 = st.columns([3, 1])
        with col1:
            bzid_input = st.text_input(
                f"Enter BZID (searching in {bzid_col}):",
                placeholder="Example: BZID-1305378359 or 1305378359",
                key="search_input"
            )
        
        with col2:
            st.markdown("<br>", unsafe_allow_html=True)
            search_btn = st.button("🔍 Search", use_container_width=True)
        
        # Search function
        if search_btn and bzid_input:
            search_term = str(bzid_input).strip().lower()
            
            # Try to find the BZID
            found_rows = []
            
            for idx, row in df.iterrows():
                cell_value = str(row[bzid_col]).lower().strip()
                
                # Check if search term is in cell value
                if search_term in cell_value:
                    found_rows.append(row)
                # Also check without BZID- prefix
                elif search_term.replace('bzid-', '') in cell_value.replace('bzid-', ''):
                    found_rows.append(row)
            
            if found_rows:
                st.success(f"✅ Found {len(found_rows)} matching record(s)")
                
                for i, row in enumerate(found_rows):
                    with st.expander(f"Record {i+1}: {row[bzid_col]}", expanded=(i==0)):
                        # Display all columns
                        for col in df.columns:
                            value = row[col]
                            
                            # Skip NaN/empty values
                            if pd.isna(value) or value == "":
                                continue
                                
                            st.write(f"**{col}:** {value}")
            else:
                st.error(f"❌ No matches found for '{bzid_input}'")
                
                # Show available BZIDs
                available_bzids = df[bzid_col].dropna().unique()[:20]
                st.info("**Available BZIDs (first 20):**")
                cols = st.columns(4)
                for i, bzid in enumerate(available_bzids):
                    with cols[i % 4]:
                        if st.button(str(bzid), key=f"bzid_{i}"):
                            st.session_state.search_input = str(bzid)
                            st.rerun()
        
        # Show data stats
        with st.sidebar.expander("📈 Data Statistics"):
            st.write(f"**Total Records:** {len(df)}")
            st.write(f"**Columns:** {len(df.columns)}")
            st.write(f"**BZID Column:** {bzid_col}")
            st.write(f"**Unique BZIDs:** {df[bzid_col].nunique()}")
            
            if 'cluster' in df.columns:
                st.write(f"**Clusters:** {df['cluster'].nunique()}")
            if 'hub' in df.columns:
                st.write(f"**Hubs:** {df['hub'].nunique()}")

# Manual data entry for testing
with st.expander("🛠️ Manual Data Entry (for testing)"):
    st.write("Paste your data in CSV format to test:")
    
    # Your sample data
    sample_csv = """cluster,hub,BZID,psr_requested_gmv,del_gmv,psr_pct,CD_flag
Lucknow,LKO_AMS,BZID-1305378359,,387790.1689,,Do not ask for image
Bangalore,BLR_HNU,BZID-1304459378,,105724.1275,,Do not ask for image
Test,Test_Hub,BZID-1304114892,1000,2000,50%,Ask for image"""
    
    csv_data = st.text_area("CSV Data:", sample_csv, height=150)
    
    if st.button("Load Test Data"):
        try:
            from io import StringIO
            test_df = pd.read_csv(StringIO(csv_data))
            st.session_state.df = test_df
            st.success(f"Loaded {len(test_df)} test records")
            st.dataframe(test_df)
            st.rerun()
        except Exception as e:
            st.error(f"Error: {str(e)}")

# Check sharing
st.sidebar.markdown("---")
st.sidebar.markdown("### 🔗 Sharing Check")
st.sidebar.write("Make sure the sheet is shared with:")
st.sidebar.code("psr-cd-lookup@psr-cd-flag-check.iam.gserviceaccount.com")
st.sidebar.write("with **Viewer** access")

# Footer
st.markdown("---")
st.caption("BZID Lookup Tool • Checks Google Sheets directly")
