import streamlit as st
import plotly.express as px
from modules.data_loader import load_batting_stats, load_bowling_stats

st.set_page_config(page_title="Player Analysis", page_icon="👤", layout="wide")

st.markdown("# 👤 Player Analysis Dashboard")
st.markdown("Analyze top performing batsmen and bowlers across the history of the IPL.")

# Load Data
bat_df = load_batting_stats()
bowl_df = load_bowling_stats()

if bat_df.empty and bowl_df.empty:
    st.error("No player data available. Please check the database.")
    st.stop()

tab1, tab2 = st.tabs(["🏏 Batting Heroes", "🎯 Bowling Legends"])

with tab1:
    st.subheader("Top Batsmen Analysis")
    if not bat_df.empty:
        # Standardize standard columns we expect from scraper/synthetic data
        player_col = 'Player' if 'Player' in bat_df.columns else bat_df.columns[0]
        runs_col = 'Runs' if 'Runs' in bat_df.columns else (bat_df.columns[2] if len(bat_df.columns)>2 else None)
        sr_col = 'Strike Rate' if 'Strike Rate' in bat_df.columns else None
        
        if runs_col:
            # Sort by highest runs
            bat_df = bat_df.sort_values(by=runs_col, ascending=False).head(50)
            
            col_sel, col_chart = st.columns([1, 3])
            
            with col_sel:
                st.write("**Filter Top Players**")
                selected_players = st.multiselect("Select Players to Compare", bat_df[player_col].tolist(), default=bat_df[player_col].head(5).tolist())
            
            with col_chart:
                filtered_bat = bat_df[bat_df[player_col].isin(selected_players)]
                if not filtered_bat.empty:
                    fig = px.bar(filtered_bat, x=player_col, y=runs_col, color=player_col, 
                                 title="Total Runs by Selected Players",
                                 color_discrete_sequence=px.colors.qualitative.Bold,
                                 template="plotly_white")
                    st.plotly_chart(fig, use_container_width=True)
                    
            st.markdown("---")
            st.markdown("### Runs vs Strike Rate (Top Batsmen)")
            if sr_col:
                # Need to convert to float because web scraped data might be string
                bat_df[runs_col] = bat_df[runs_col].astype(str).str.replace(',', '').astype(float)
                bat_df[sr_col] = bat_df[sr_col].astype(str).str.replace('-', '0').astype(float)
                
                fig2 = px.scatter(bat_df, x=runs_col, y=sr_col, hover_name=player_col,
                                  size=runs_col, color=sr_col,
                                  title="Aggression vs Consistency",
                                  labels={runs_col: "Total Career Runs", sr_col: "Career Strike Rate"},
                                  template="plotly_dark", size_max=40)
                st.plotly_chart(fig2, use_container_width=True)
            
            st.dataframe(bat_df, use_container_width=True)

with tab2:
    st.subheader("Top Bowlers Analysis")
    if not bowl_df.empty:
        player_col = 'Player' if 'Player' in bowl_df.columns else bowl_df.columns[0]
        wkts_col = 'Wickets' if 'Wickets' in bowl_df.columns else None
        
        if wkts_col:
            bowl_df = bowl_df.sort_values(by=wkts_col, ascending=False).head(50)
            bowl_df[wkts_col] = bowl_df[wkts_col].astype(str).str.replace(',', '').astype(float)
            
            fig_bowl = px.bar(bowl_df.head(15), x=player_col, y=wkts_col, 
                              color=wkts_col, color_continuous_scale="Viridis",
                              title="Top 15 All-Time Wicket Takers", template="plotly_white")
            st.plotly_chart(fig_bowl, use_container_width=True)
            
        st.dataframe(bowl_df, use_container_width=True)
