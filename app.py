import streamlit as st

st.set_page_config(
    page_title="IPL Analytics Dashboard",
    page_icon="🏏",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling for aesthetics
st.markdown("""
<style>
    .main-title {
        font-family: 'Helvetica Neue', sans-serif;
        color: #1E3A8A;
        font-weight: 800;
        font-size: 3rem;
        margin-bottom: 0rem;
    }
    .sub-title {
        font-family: 'Helvetica Neue', sans-serif;
        color: #4B5563;
        font-size: 1.2rem;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #F3F4F6;
        padding: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
    }
    .stButton>button {
        background-color: #1E3A8A;
        color: white;
        border-radius: 5px;
        padding: 0.5rem 1rem;
        font-weight: bold;
        transition: all 0.3s;
    }
    .stButton>button:hover {
        background-color: #3B82F6;
        border-color: #3B82F6;
    }
</style>
""", unsafe_allow_html=True)

from modules.data_loader import load_team_stats, load_batting_stats, load_match_data

def main():
    st.markdown('<h1 class="main-title">🏏 IPL Analytics Dashboard</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-title">A comprehensive data-driven exploration of Indian Premier League stats and trends.</p>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    st.markdown("### 🏆 Welcome to the Ultimate IPL Experience")
    st.write("""
    Explore detailed player career statistics, deep-dive into team historical performances across seasons, 
    and identify match-winning trends using our interactive visualizer tools.
    
    👈 Use the **Sidebar Menu** to navigate between:
    - 👤 **Player Analysis**: Compare batsmen and bowlers, view strike-rates and dynamic charts.
    - 🛡️ **Team Analysis**: Monitor win percentages, historical standings, and team head-to-heads.
    - 🏟️ **Match Insights**: See how the toss, venues, and innings impact match results.
    """)
    
    st.markdown("---")
    
    # Showcase some key summary facts dynamically from data
    st.markdown("### ⚡ Quick Facts")
    
    team_df = load_team_stats()
    bat_df = load_batting_stats()
    match_df = load_match_data()
    
    col1, col2, col3, col4 = st.columns(4)
    
    if not team_df.empty:
        # Assuming we have a 'Matches Played' or 'Team' columns
        if 'Matches Played' in team_df.columns:
            total_matches_franchises = int(team_df['Matches Played'].sum() / 2) # Rough approximation since two teams play a match
        else:
            total_matches_franchises = len(match_df) if not match_df.empty else 1000
        with col1:
            st.metric("Total Matches (approx)", f"{total_matches_franchises:,}")
    
    if not bat_df.empty:
        if 'Runs' in bat_df.columns:
            top_scorer = bat_df.iloc[0]
            with col2:
                # Top scorer name usually in 'Player' or 'Batsman'
                player_col = 'Player' if 'Player' in bat_df.columns else bat_df.columns[0]
                runs_col = 'Runs'
                st.metric("All-time Top Scorer", top_scorer[player_col], f"{top_scorer[runs_col]} Runs")
                
    if not match_df.empty and 'Season' in match_df.columns:
        seasons = match_df['Season'].nunique()
        with col3:
            st.metric("Seasons Covered", str(seasons))
            
    with col4:
        st.metric("Data Source", "Wikipedia & Synthetic", "+ High Quality")

if __name__ == "__main__":
    main()
