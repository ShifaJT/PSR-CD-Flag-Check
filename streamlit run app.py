import streamlit as st
import pandas as pd
import numpy as np
import time
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
from io import BytesIO
import requests
import json

# Page configuration
st.set_page_config(
    page_title="BZID Player Dashboard",
    page_icon="🎮",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for better UI
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #FF4B4B;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: 800;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        background: linear-gradient(90deg, #FF4B4B, #FF6B6B);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #FFFFFF;
        margin-bottom: 1rem;
        font-weight: 600;
    }
    .player-card {
        background: linear-gradient(135deg, #1E1E2E 0%, #2D2D44 100%);
        border-radius: 15px;
        padding: 25px;
        margin: 15px 0;
        border-left: 5px solid #FF4B4B;
        box-shadow: 0 4px 20px rgba(0,0,0,0.3);
        transition: transform 0.3s ease;
    }
    .player-card:hover {
        transform: translateY(-5px);
    }
    .stat-box {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
        text-align: center;
    }
    .stat-value {
        font-size: 2rem;
        font-weight: bold;
        color: #FF4B4B;
        margin-bottom: 5px;
    }
    .stat-label {
        font-size: 0.9rem;
        color: #AAAAAA;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .search-container {
        background: rgba(30, 30, 46, 0.8);
        padding: 30px;
        border-radius: 15px;
        margin-bottom: 30px;
        backdrop-filter: blur(10px);
    }
    .stButton > button {
        width: 100%;
        height: 50px;
        background: linear-gradient(90deg, #FF4B4B, #FF6B6B);
        color: white;
        border: none;
        border-radius: 10px;
        font-size: 1.1rem;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        transform: scale(1.02);
        box-shadow: 0 5px 15px rgba(255, 75, 75, 0.4);
    }
    .stTextInput > div > div > input {
        background: rgba(255, 255, 255, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.2);
        color: white;
        border-radius: 10px;
        padding: 15px;
        font-size: 1.1rem;
    }
    .loading-spinner {
        text-align: center;
        padding: 40px;
    }
    .metric-container {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 15px;
        margin: 20px 0;
    }
    .tab-container {
        background: rgba(30, 30, 46, 0.8);
        border-radius: 15px;
        padding: 20px;
        margin-top: 20px;
    }
</style>
""", unsafe_allow_html=True)

# Title
st.markdown('<h1 class="main-header">🎮 BZID Player Dashboard</h1>', unsafe_allow_html=True)
st.markdown('<p style="text-align: center; color: #AAAAAA; margin-bottom: 40px;">Instant Player Statistics & Performance Analytics</p>', unsafe_allow_html=True)

# Mock data generator (Replace with your actual data source)
def generate_mock_player_data(bzid):
    """Generate mock player data based on BZID"""
    # In production, replace this with your actual database/API call
    
    # Create a deterministic hash from BZID for consistent mock data
    hash_val = hash(bzid) % 1000
    
    return {
        "basic_info": {
            "BZID": bzid,
            "Player_Name": f"Player_{hash_val}",
            "Level": (hash_val % 100) + 1,
            "Rank": ["Bronze", "Silver", "Gold", "Platinum", "Diamond"][hash_val % 5],
            "Region": ["NA", "EU", "ASIA", "SA"][hash_val % 4],
            "Join_Date": "2023-{:02d}-{:02d}".format((hash_val % 12) + 1, (hash_val % 28) + 1),
            "Last_Active": "2024-{:02d}-{:02d}".format((hash_val % 12) + 1, (hash_val % 28) + 1),
            "Status": "Active" if hash_val % 10 > 2 else "Inactive"
        },
        "combat_stats": {
            "Total_Matches": hash_val + 100,
            "Wins": (hash_val + 100) // 2,
            "Losses": (hash_val + 100) // 2,
            "Win_Rate": round(((hash_val + 100) // 2) / (hash_val + 100) * 100, 1),
            "Kills": hash_val * 10,
            "Deaths": hash_val * 5,
            "Assists": hash_val * 3,
            "K/D_Ratio": round((hash_val * 10) / max(hash_val * 5, 1), 2),
            "Headshot_Percentage": round((hash_val % 50) + 20, 1),
            "Accuracy": round((hash_val % 40) + 50, 1)
        },
        "performance_metrics": {
            "Avg_Score_per_Match": (hash_val * 100) % 5000 + 1000,
            "Highest_Score": (hash_val * 100) % 10000 + 5000,
            "MVP_Count": hash_val % 50,
            "Playtime_Hours": hash_val + 50,
            "Avg_Kills_per_Match": round((hash_val * 10) / max(hash_val + 100, 1), 1),
            "Avg_Deaths_per_Match": round((hash_val * 5) / max(hash_val + 100, 1), 1)
        },
        "recent_matches": [
            {
                "Match_ID": f"MATCH_{hash_val + i}",
                "Result": ["Win", "Loss"][(hash_val + i) % 2],
                "Score": (hash_val + i) * 100 % 5000 + 1000,
                "Kills": (hash_val + i) % 30 + 5,
                "Deaths": (hash_val + i) % 20 + 2,
                "Assists": (hash_val + i) % 15 + 1,
                "Date": f"2024-{(hash_val % 12) + 1:02d}-{(i % 28) + 1:02d}"
            }
            for i in range(5)
        ],
        "achievements": [
            "First Win",
            "Killing Spree",
            "Headshot Master",
            "Team Player",
            "Veteran Player"
        ][:hash_val % 4 + 1]
    }

def search_player_data(bzid):
    """Search for player data - replace with your actual data source"""
    # Add artificial delay to simulate loading
    time.sleep(0.5)
    
    if not bzid:
        return None
    
    # In production, replace this with your actual data fetching logic
    # For example:
    # 1. Database query
    # 2. API call to your backend
    # 3. CSV/Excel file lookup
    
    # For now, use mock data
    return generate_mock_player_data(bzid)

def create_performance_charts(player_data):
    """Create performance visualization charts"""
    charts = {}
    
    # Win/Loss Pie Chart
    win_loss_data = pd.DataFrame({
        'Result': ['Wins', 'Losses'],
        'Count': [player_data['combat_stats']['Wins'], player_data['combat_stats']['Losses']]
    })
    
    fig_pie = px.pie(win_loss_data, values='Count', names='Result',
                    title='Win/Loss Distribution',
                    color='Result',
                    color_discrete_map={'Wins':'#00FF88', 'Losses':'#FF4B4B'})
    fig_pie.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                         font_color='white', title_font_color='white')
    charts['win_loss'] = fig_pie
    
    # K/D Ratio Gauge
    fig_gauge = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = player_data['combat_stats']['K/D_Ratio'],
        title = {'text': "K/D Ratio"},
        domain = {'x': [0, 1], 'y': [0, 1]},
        gauge = {
            'axis': {'range': [None, 5]},
            'bar': {'color': "#FF4B4B"},
            'steps': [
                {'range': [0, 1], 'color': "#FF6B6B"},
                {'range': [1, 2], 'color': "#FF8B8B"},
                {'range': [2, 5], 'color': "#00FF88"}
            ]
        }
    ))
    fig_gauge.update_layout(paper_bgcolor='rgba(0,0,0,0)', font_color='white')
    charts['kd_gauge'] = fig_gauge
    
    # Recent Matches Performance
    recent_matches = pd.DataFrame(player_data['recent_matches'])
    fig_line = px.line(recent_matches, x='Date', y='Score',
                      title='Recent Match Performance',
                      markers=True, line_shape='spline')
    fig_line.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                          font_color='white', title_font_color='white')
    fig_line.update_traces(line_color='#00FF88')
    charts['performance_trend'] = fig_line
    
    return charts

# Main app layout
with st.container():
    st.markdown('<div class="search-container">', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([2, 1, 2])
    
    with col2:
        bzid_input = st.text_input(
            "Enter BZID:",
            placeholder="e.g., BZ123456789",
            key="bzid_input"
        )
        
        search_button = st.button(
            "🔍 Search Player",
            type="primary",
            use_container_width=True
        )
    
    st.markdown('</div>', unsafe_allow_html=True)

# Initialize session state for player data
if 'player_data' not in st.session_state:
    st.session_state.player_data = None
if 'loading' not in st.session_state:
    st.session_state.loading = False

# Handle search
if search_button or bzid_input:
    if bzid_input:
        with st.spinner('🔍 Searching for player data...'):
            st.session_state.loading = True
            player_data = search_player_data(bzid_input)
            st.session_state.player_data = player_data
            st.session_state.loading = False
            st.rerun()
    else:
        st.warning("⚠️ Please enter a BZID to search")

# Display results if data exists
if st.session_state.player_data and not st.session_state.loading:
    player_data = st.session_state.player_data
    
    # Player Overview Card
    st.markdown('<div class="player-card">', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
    
    with col1:
        st.markdown(f'<h2 style="color: #FFFFFF; margin-bottom: 5px;">{player_data["basic_info"]["Player_Name"]}</h2>', unsafe_allow_html=True)
        st.markdown(f'<p style="color: #AAAAAA;">BZID: {player_data["basic_info"]["BZID"]}</p>', unsafe_allow_html=True)
        
        # Badges
        badges_html = " ".join([f'<span style="background: rgba(255,75,75,0.2); color: #FF6B6B; padding: 5px 10px; border-radius: 15px; margin-right: 10px; font-size: 0.9rem;">🏆 {badge}</span>' 
                              for badge in player_data["achievements"]])
        st.markdown(badges_html, unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="stat-box">', unsafe_allow_html=True)
        st.markdown(f'<div class="stat-value">{player_data["basic_info"]["Level"]}</div>', unsafe_allow_html=True)
        st.markdown('<div class="stat-label">LEVEL</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="stat-box">', unsafe_allow_html=True)
        st.markdown(f'<div class="stat-value">{player_data["basic_info"]["Rank"]}</div>', unsafe_allow_html=True)
        st.markdown('<div class="stat-label">RANK</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col4:
        status_color = "#00FF88" if player_data["basic_info"]["Status"] == "Active" else "#FF4B4B"
        st.markdown('<div class="stat-box">', unsafe_allow_html=True)
        st.markdown(f'<div class="stat-value" style="color: {status_color};">{player_data["basic_info"]["Status"]}</div>', unsafe_allow_html=True)
        st.markdown('<div class="stat-label">STATUS</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Quick Stats
    st.markdown('<div class="metric-container">', unsafe_allow_html=True)
    
    metrics = [
        ("Total Matches", player_data["combat_stats"]["Total_Matches"], "#FF6B6B"),
        ("Win Rate", f"{player_data['combat_stats']['Win_Rate']}%", "#00FF88"),
        ("K/D Ratio", player_data["combat_stats"]["K/D_Ratio"], "#FF4B4B"),
        ("Accuracy", f"{player_data['combat_stats']['Accuracy']}%", "#4B8BFF"),
        ("MVP Count", player_data["performance_metrics"]["MVP_Count"], "#FFD700"),
        ("Playtime", f"{player_data['performance_metrics']['Playtime_Hours']}h", "#8B4BFF")
    ]
    
    cols = st.columns(len(metrics))
    for idx, (label, value, color) in enumerate(metrics):
        with cols[idx]:
            st.markdown(f'''
            <div class="stat-box">
                <div class="stat-value" style="color: {color};">{value}</div>
                <div class="stat-label">{label}</div>
            </div>
            ''', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Tabs for detailed information
    st.markdown('<div class="tab-container">', unsafe_allow_html=True)
    
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Performance Charts", "⚔️ Combat Stats", "📈 Recent Matches", "👤 Player Info"])
    
    with tab1:
        charts = create_performance_charts(player_data)
        
        col1, col2 = st.columns(2)
        with col1:
            st.plotly_chart(charts['win_loss'], use_container_width=True)
        with col2:
            st.plotly_chart(charts['kd_gauge'], use_container_width=True)
        
        st.plotly_chart(charts['performance_trend'], use_container_width=True)
    
    with tab2:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<h3 style="color: white;">Combat Statistics</h3>', unsafe_allow_html=True)
            combat_df = pd.DataFrame([
                ["Kills", player_data['combat_stats']['Kills']],
                ["Deaths", player_data['combat_stats']['Deaths']],
                ["Assists", player_data['combat_stats']['Assists']],
                ["Headshot %", f"{player_data['combat_stats']['Headshot_Percentage']}%"],
                ["Avg Kills/Match", player_data['performance_metrics']['Avg_Kills_per_Match']],
                ["Avg Deaths/Match", player_data['performance_metrics']['Avg_Deaths_per_Match']]
            ], columns=["Statistic", "Value"])
            
            # Style the dataframe
            st.dataframe(
                combat_df,
                column_config={
                    "Statistic": st.column_config.TextColumn(width="medium"),
                    "Value": st.column_config.NumberColumn(width="small")
                },
                hide_index=True,
                use_container_width=True
            )
        
        with col2:
            st.markdown('<h3 style="color: white;">Performance Metrics</h3>', unsafe_allow_html=True)
            perf_df = pd.DataFrame([
                ["Total Matches", player_data['combat_stats']['Total_Matches']],
                ["Wins", player_data['combat_stats']['Wins']],
                ["Losses", player_data['combat_stats']['Losses']],
                ["Avg Score/Match", player_data['performance_metrics']['Avg_Score_per_Match']],
                ["Highest Score", player_data['performance_metrics']['Highest_Score']],
                ["Playtime Hours", player_data['performance_metrics']['Playtime_Hours']]
            ], columns=["Metric", "Value"])
            
            st.dataframe(perf_df, hide_index=True, use_container_width=True)
    
    with tab3:
        recent_matches_df = pd.DataFrame(player_data['recent_matches'])
        st.dataframe(
            recent_matches_df,
            column_config={
                "Match_ID": "Match ID",
                "Result": st.column_config.TextColumn(
                    width="small",
                    help="Match result"
                ),
                "Score": st.column_config.NumberColumn(
                    format="%d"
                ),
                "Kills": st.column_config.NumberColumn(
                    format="%d"
                ),
                "Deaths": st.column_config.NumberColumn(
                    format="%d"
                ),
                "Assists": st.column_config.NumberColumn(
                    format="%d"
                ),
                "Date": "Date"
            },
            hide_index=True,
            use_container_width=True
        )
    
    with tab4:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<h3 style="color: white;">Basic Information</h3>', unsafe_allow_html=True)
            info_df = pd.DataFrame([
                ["Player Name", player_data['basic_info']['Player_Name']],
                ["BZID", player_data['basic_info']['BZID']],
                ["Region", player_data['basic_info']['Region']],
                ["Join Date", player_data['basic_info']['Join_Date']],
                ["Last Active", player_data['basic_info']['Last_Active']]
            ], columns=["Field", "Value"])
            
            st.dataframe(info_df, hide_index=True, use_container_width=True)
        
        with col2:
            st.markdown('<h3 style="color: white;">Achievements</h3>', unsafe_allow_html=True)
            for achievement in player_data['achievements']:
                st.markdown(f'<p style="color: #00FF88;">🏆 {achievement}</p>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Export option
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("📥 Export Player Report", use_container_width=True):
            # Create a downloadable JSON report
            json_str = json.dumps(player_data, indent=2)
            st.download_button(
                label="Download JSON Report",
                data=json_str,
                file_name=f"{player_data['basic_info']['BZID']}_report.json",
                mime="application/json",
                use_container_width=True
            )

# Initial state message
elif not st.session_state.loading and not st.session_state.player_data:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div style="text-align: center; padding: 60px; background: rgba(30, 30, 46, 0.8); border-radius: 15px; margin-top: 50px;">
            <h3 style="color: #FFFFFF; margin-bottom: 20px;">🚀 Quick Player Lookup</h3>
            <p style="color: #AAAAAA; margin-bottom: 10px;">Enter a BZID in the search box above to get:</p>
            <ul style="color: #CCCCCC; text-align: left; display: inline-block;">
                <li>Instant player statistics</li>
                <li>Performance charts & analytics</li>
                <li>Combat history</li>
                <li>Achievements & rankings</li>
                <li>Exportable reports</li>
            </ul>
            <p style="color: #00FF88; margin-top: 20px;">No more waiting for Metabase to load! ⚡</p>
        </div>
        """, unsafe_allow_html=True)

# Footer
st.markdown("""
<hr style="border: 1px solid rgba(255, 255, 255, 0.1); margin: 40px 0 20px 0;">
<div style="text-align: center; color: #666666; font-size: 0.9rem;">
    <p>🎮 BZID Player Dashboard • Instant Access to Player Statistics</p>
    <p>⚡ Faster than Metabase • 📊 Interactive Visualizations • 📱 Mobile-Friendly</p>
</div>
""", unsafe_allow_html=True)
