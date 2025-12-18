import streamlit as st
import pandas as pd
import gspread
from google.oauth2 import service_account
import random
import time

# Page setup - Fun and engaging
st.set_page_config(
    page_title="🎮 BZID Detective",
    page_icon="🕵️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Fun CSS with animations
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700;800&display=swap');
    
    * {
        font-family: 'Poppins', sans-serif;
    }
    
    .main-title {
        font-size: 3.5rem;
        background: linear-gradient(90deg, #FF6B6B, #4ECDC4, #45B7D1);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        font-weight: 800;
        margin-bottom: 0;
        text-shadow: 0 2px 10px rgba(0,0,0,0.1);
        animation: titleGlow 2s ease-in-out infinite alternate;
    }
    
    @keyframes titleGlow {
        from { text-shadow: 0 0 20px #FF6B6B; }
        to { text-shadow: 0 0 30px #4ECDC4, 0 0 20px #45B7D1; }
    }
    
    .subtitle {
        text-align: center;
        color: #666;
        font-size: 1.2rem;
        margin-bottom: 2rem;
        animation: fadeIn 2s;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }
    
    .search-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 20px;
        padding: 40px;
        margin: 20px auto;
        max-width: 800px;
        box-shadow: 0 10px 40px rgba(102, 126, 234, 0.4);
        animation: containerFloat 3s ease-in-out infinite;
        border: 3px solid rgba(255,255,255,0.2);
    }
    
    @keyframes containerFloat {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-10px); }
    }
    
    .search-input {
        background: rgba(255,255,255,0.9) !important;
        border: none !important;
        border-radius: 15px !important;
        padding: 20px !important;
        font-size: 1.2rem !important;
        color: #333 !important;
        box-shadow: 0 5px 15px rgba(0,0,0,0.1) !important;
        transition: all 0.3s !important;
    }
    
    .search-input:focus {
        transform: scale(1.02);
        box-shadow: 0 8px 25px rgba(0,0,0,0.15) !important;
    }
    
    .stButton > button {
        background: linear-gradient(90deg, #FFD166, #06D6A0) !important;
        color: white !important;
        border: none !important;
        border-radius: 15px !important;
        padding: 15px 40px !important;
        font-size: 1.3rem !important;
        font-weight: 700 !important;
        transition: all 0.3s !important;
        box-shadow: 0 5px 15px rgba(255,209,102,0.4) !important;
        margin-top: 20px !important;
        animation: buttonPulse 2s infinite;
    }
    
    @keyframes buttonPulse {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.05); }
    }
    
    .stButton > button:hover {
        transform: translateY(-3px) !important;
        box-shadow: 0 10px 25px rgba(255,209,102,0.6) !important;
        background: linear-gradient(90deg, #FFD166, #06D6A0) !important;
    }
    
    .result-card {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        border-radius: 25px;
        padding: 30px;
        margin: 30px 0;
        box-shadow: 0 15px 35px rgba(0,0,0,0.1);
        border-left: 8px solid #FF6B6B;
        animation: cardAppear 0.8s ease-out;
    }
    
    @keyframes cardAppear {
        from { 
            opacity: 0;
            transform: translateY(30px) scale(0.95);
        }
        to { 
            opacity: 1;
            transform: translateY(0) scale(1);
        }
    }
    
    .data-badge {
        display: inline-block;
        background: linear-gradient(90deg, #4ECDC4, #45B7D1);
        color: white;
        padding: 8px 20px;
        border-radius: 50px;
        margin: 5px;
        font-weight: 600;
        box-shadow: 0 3px 10px rgba(78, 205, 196, 0.3);
        animation: badgeGlow 3s infinite;
    }
    
    @keyframes badgeGlow {
        0%, 100% { box-shadow: 0 3px 10px rgba(78, 205, 196, 0.3); }
        50% { box-shadow: 0 3px 15px rgba(78, 205, 196, 0.6); }
    }
    
    .flag-badge {
        display: inline-block;
        padding: 10px 25px;
        border-radius: 50px;
        font-weight: 700;
        font-size: 1.1rem;
        animation: flagBounce 1s;
    }
    
    @keyframes flagBounce {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.1); }
    }
    
    .metric-card {
        background: white;
        border-radius: 20px;
        padding: 20px;
        margin: 10px;
        text-align: center;
        box-shadow: 0 5px 15px rgba(0,0,0,0.08);
        transition: all 0.3s;
        border-top: 5px solid #FF6B6B;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 25px rgba(0,0,0,0.15);
    }
    
    .metric-value {
        font-size: 2.5rem;
        font-weight: 800;
        background: linear-gradient(90deg, #FF6B6B, #4ECDC4);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 5px;
    }
    
    .metric-label {
        color: #666;
        font-size: 0.9rem;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .loading-dots {
        display: inline-block;
        margin-left: 10px;
    }
    
    .loading-dots:after {
        content: ' .';
        animation: dots 1.5s steps(5, end) infinite;
    }
    
    @keyframes dots {
        0%, 20% { content: ' .'; }
        40% { content: ' ..'; }
        60% { content: ' ...'; }
        80%, 100% { content: ' ....'; }
    }
    
    .fun-fact {
        background: linear-gradient(135deg, #A8E6CF, #DCEDC1);
        border-radius: 15px;
        padding: 15px;
        margin: 10px 0;
        font-style: italic;
        border-left: 5px solid #FF8B94;
    }
    
    .emoji-header {
        font-size: 2rem;
        margin-right: 10px;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'data' not in st.session_state:
    st.session_state.data = None
if 'searched' not in st.session_state:
    st.session_state.searched = False
if 'current_bzid' not in st.session_state:
    st.session_state.current_bzid = None

# Title with emojis
st.markdown('<h1 class="main-title">🔍🕵️‍♂️ BZID Detective 🎯📊</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Find customer data faster than lightning! ⚡ Just drop a BZID and watch the magic happen ✨</p>', unsafe_allow_html=True)

# Fun loading messages
loading_messages = [
    "🔍 Scanning the database...",
    "🕵️‍♂️ On the case!",
    "⚡ Processing at light speed...",
    "🎯 Locking onto target...",
    "✨ Working some magic...",
    "🚀 Blasting off to find data...",
    "🧠 Using detective skills...",
    "🔮 Consulting the crystal ball..."
]

# Function to load data once (cached)
@st.cache_data(ttl=300)
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
            worksheet = sheet.get_worksheet(0)
        
        # Get all data
        data = worksheet.get_all_records()
        
        # Convert to DataFrame
        df = pd.DataFrame(data)
        
        return df
        
    except Exception as e:
        return None

# Auto-load data with fun animation
if st.session_state.data is None:
    with st.container():
        col1, col2, col3 = st.columns([1,2,1])
        with col2:
            with st.spinner(random.choice(loading_messages)):
                df = load_data()
                if df is not None and not df.empty:
                    st.session_state.data = df
                    st.balloons()
                    st.success(f"🎉 **Database unlocked!** Found **{len(df)}** secret records!")
                    
                    # Fun fact
                    fun_facts = [
                        f"📈 That's like finding a needle in {len(df)} haystacks!",
                        f"🚀 Ready to search at warp speed!",
                        f"🎯 Locked and loaded for BZID hunting!",
                        f"✨ Magic data connection established!"
                    ]
                    st.markdown(f'<div class="fun-fact">{random.choice(fun_facts)}</div>', unsafe_allow_html=True)
                else:
                    st.error("⚠️ Could not connect to the secret database!")
                    st.info("🔧 Check if your detective toolkit (credentials) is properly configured.")

# Fun search interface
st.markdown('<div class="search-container">', unsafe_allow_html=True)

col1, col2, col3 = st.columns([1,3,1])
with col2:
    st.markdown('<h2 style="color: white; text-align: center;">🎯 Enter BZID Target</h2>', unsafe_allow_html=True)
    
    bzid_input = st.text_input(
        "",
        placeholder="🔤 Type BZID here... Example: BZID-1305378359",
        key="search_input"
    )
    
    search_col1, search_col2, search_col3 = st.columns([1,2,1])
    with search_col2:
        search_btn = st.button("🚀 Launch Investigation!", use_container_width=True)

st.markdown('</div>', unsafe_allow_html=True)

# Handle search
if (search_btn or bzid_input) and bzid_input:
    if st.session_state.data is not None:
        df = st.session_state.data
        
        # Find BZID column
        bzid_col = None
        for col in df.columns:
            if 'bzid' in col.lower():
                bzid_col = col
                break
        
        if bzid_col:
            # Show searching animation
            with st.spinner(f"🔍 Investigating {bzid_input}..."):
                time.sleep(0.5)  # Small delay for effect
                
                # Clean search term
                search_term = str(bzid_input).strip()
                
                # Remove BZID- prefix if present
                if search_term.upper().startswith('BZID-'):
                    search_term = search_term[5:]
                
                # Search for the BZID
                found_player = None
                for idx, row in df.iterrows():
                    cell_value = str(row[bzid_col]).strip()
                    
                    if (search_term == cell_value or 
                        f"BZID-{search_term}" == cell_value or
                        search_term == cell_value.replace('BZID-', '')):
                        found_player = row
                        break
                
                if found_player is not None:
                    st.session_state.searched = True
                    st.session_state.current_bzid = bzid_input
                    
                    # Celebrate!
                    st.balloons()
                    st.success(f"🎉 **Target Acquired!** Found {bzid_input}")
                    
                    # Display results in fun cards
                    st.markdown('<div class="result-card">', unsafe_allow_html=True)
                    
                    # Header with emoji
                    emoji = random.choice(["🕵️‍♂️", "🎯", "✨", "🌟", "🔥", "🚀"])
                    st.markdown(f'<h2>{emoji} Case File: {found_player[bzid_col]}</h2>', unsafe_allow_html=True)
                    
                    # Quick stats in cards
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                        st.markdown(f'<div class="metric-value">{found_player.get("cluster", "N/A")}</div>', unsafe_allow_html=True)
                        st.markdown('<div class="metric-label">📍 CLUSTER</div>', unsafe_allow_html=True)
                        st.markdown('</div>', unsafe_allow_html=True)
                    
                    with col2:
                        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                        st.markdown(f'<div class="metric-value">{found_player.get("hub", "N/A")}</div>', unsafe_allow_html=True)
                        st.markdown('<div class="metric-label">🏢 HUB</div>', unsafe_allow_html=True)
                        st.markdown('</div>', unsafe_allow_html=True)
                    
                    with col3:
                        if 'del_gmv' in df.columns and pd.notna(found_player['del_gmv']):
                            try:
                                gmv_value = float(found_player['del_gmv'])
                                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                                st.markdown(f'<div class="metric-value">₹{gmv_value:,.0f}</div>', unsafe_allow_html=True)
                                st.markdown('<div class="metric-label">💰 GMV</div>', unsafe_allow_html=True)
                                st.markdown('</div>', unsafe_allow_html=True)
                            except:
                                pass
                    
                    with col4:
                        if 'CD_flag' in df.columns:
                            flag_value = found_player['CD_flag']
                            flag_color = "#06D6A0" if "Do not ask" in str(flag_value) else "#EF476F"
                            flag_emoji = "✅" if "Do not ask" in str(flag_value) else "⚠️"
                            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                            st.markdown(f'<div class="metric-value">{flag_emoji}</div>', unsafe_allow_html=True)
                            st.markdown(f'<div class="metric-label">🚩 CD FLAG</div>', unsafe_allow_html=True)
                            st.markdown('</div>', unsafe_allow_html=True)
                    
                    # All data in badges
                    st.markdown("---")
                    st.markdown("### 📋 Complete Intelligence Report")
                    
                    # Create two columns for data
                    data_col1, data_col2 = st.columns(2)
                    
                    with data_col1:
                        for i, col in enumerate(df.columns[:len(df.columns)//2]):
                            if col != bzid_col and pd.notna(found_player[col]) and str(found_player[col]).strip():
                                value = str(found_player[col])
                                # Format values
                                if 'gmv' in col.lower():
                                    try:
                                        value = f"₹{float(value):,.2f}"
                                    except:
                                        pass
                                elif 'pct' in col.lower():
                                    try:
                                        value = f"{float(value):.2%}"
                                    except:
                                        pass
                                
                                st.markdown(f'<div class="data-badge"><strong>{col}:</strong> {value}</div>', unsafe_allow_html=True)
                    
                    with data_col2:
                        for i, col in enumerate(df.columns[len(df.columns)//2:]):
                            if col != bzid_col and pd.notna(found_player[col]) and str(found_player[col]).strip():
                                value = str(found_player[col])
                                # Format values
                                if 'gmv' in col.lower():
                                    try:
                                        value = f"₹{float(value):,.2f}"
                                    except:
                                        pass
                                elif 'pct' in col.lower():
                                    try:
                                        value = f"{float(value):.2%}"
                                    except:
                                        pass
                                
                                st.markdown(f'<div class="data-badge"><strong>{col}:</strong> {value}</div>', unsafe_allow_html=True)
                    
                    # CD Flag with special styling
                    if 'CD_flag' in df.columns:
                        flag_value = found_player['CD_flag']
                        if "Do not ask" in str(flag_value):
                            st.markdown('<div class="flag-badge" style="background: linear-gradient(90deg, #06D6A0, #118AB2); color: white;">✅ ' + str(flag_value) + '</div>', unsafe_allow_html=True)
                        else:
                            st.markdown('<div class="flag-badge" style="background: linear-gradient(90deg, #EF476F, #FFD166); color: white;">⚠️ ' + str(flag_value) + '</div>', unsafe_allow_html=True)
                    
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    # Fun footer
                    fun_endings = [
                        "🎯 Mission accomplished! Ready for another target?",
                        "✨ Case closed! Want to investigate another BZID?",
                        "🚀 Data retrieved successfully! Next search?",
                        "🕵️‍♂️ Investigation complete! Another mystery to solve?"
                    ]
                    st.markdown(f'<div class="fun-fact">{random.choice(fun_endings)}</div>', unsafe_allow_html=True)
                    
                else:
                    st.error(f"❌ **Target Not Found!** {bzid_input} is hiding too well!")
                    st.info(f"🕵️‍♂️ Try one of these active targets:")
                    
                    # Show available BZIDs in a fun way
                    if len(df) > 0:
                        available = df[bzid_col].head(8).tolist()
                        cols = st.columns(4)
                        for i, bzid in enumerate(available):
                            with cols[i % 4]:
                                if st.button(f"🔎 {bzid}", key=f"quick_{i}"):
                                    st.session_state.search_input = str(bzid)
                                    st.rerun()
        else:
            st.error("⚠️ **No BZID column found in the secret files!**")
            
    else:
        st.warning("🔄 **Database still loading...** Please wait a moment!")

# Fun sidebar stats
with st.sidebar:
    st.markdown("### 📊 Detective Stats")
    
    if st.session_state.data is not None:
        df = st.session_state.data
        
        st.metric("🔍 Total Cases", len(df))
        
        if 'cluster' in df.columns:
            unique_clusters = df['cluster'].nunique()
            st.metric("📍 Clusters", unique_clusters)
        
        if 'hub' in df.columns:
            unique_hubs = df['hub'].nunique()
            st.metric("🏢 Hubs", unique_hubs)
        
        if 'CD_flag' in df.columns:
            do_not_ask = df['CD_flag'].str.contains('Do not ask', na=False).sum()
            st.metric("✅ Do Not Ask", do_not_ask)
        
        st.markdown("---")
        st.markdown("### 🎮 Quick Actions")
        
        if st.button("🔄 Refresh Database"):
            st.cache_data.clear()
            st.session_state.data = None
            st.session_state.searched = False
            st.rerun()
        
        if st.button("🎲 Random BZID"):
            if st.session_state.data is not None:
                df = st.session_state.data
                bzid_col = None
                for col in df.columns:
                    if 'bzid' in col.lower():
                        bzid_col = col
                        break
                if bzid_col:
                    random_bzid = df[bzid_col].sample(1).iloc[0]
                    st.session_state.search_input = str(random_bzid)
                    st.rerun()
    
    st.markdown("---")
    st.markdown("### 🎯 Pro Tips")
    tips = [
        "💡 Enter BZID with or without 'BZID-' prefix",
        "🚀 Press Enter after typing to search",
        "🎲 Try 'Random BZID' for surprises!",
        "🔄 Refresh if data seems outdated"
    ]
    for tip in tips:
        st.info(tip)

# Fun footer
st.markdown("---")
st.markdown(
    """
    <div style="text-align: center; color: #666;">
        <p>🎮 <strong>BZID Detective</strong> • ⚡ Faster than Metabase • 🎯 One search, all data</p>
        <p>Made with ❤️ for instant customer intelligence</p>
    </div>
    """,
    unsafe_allow_html=True
)
