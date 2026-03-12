import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from modules.data_loader import load_match_data

st.set_page_config(page_title="Match Insights", page_icon="🏟️", layout="wide")

st.markdown("# 🏟️ Match Insights & Trends")
st.markdown("Dive into match-level data to discover winning patterns, toss impacts, and venue characteristics.")

match_df = load_match_data()

if match_df.empty:
    st.error("No match data available.")
    st.stop()

# Interactive Filters
st.sidebar.header("Filter Match Data")
seasons = sorted(match_df['Season'].unique().tolist(), reverse=True)
selected_season = st.sidebar.selectbox("Select Season (or All)", ["All"] + seasons)

if selected_season != "All":
    match_df = match_df[match_df['Season'] == selected_season]

tab1, tab2, tab3 = st.tabs(["🪙 Toss Impact", "🏟️ Venue Analysis", "📈 Run Distributions"])

with tab1:
    st.subheader("Does winning the toss matter?")
    
    # Calculate toss impact
    match_df['Toss_Winner_is_Match_Winner'] = match_df['Toss_Winner'] == match_df['Match_Winner']
    toss_win_count = match_df['Toss_Winner_is_Match_Winner'].value_counts()
    
    col1, col2 = st.columns(2)
    with col1:
        fig_pie = px.pie(values=toss_win_count.values, names=['Won Match', 'Lost Match'], 
                         title="Match Outcomes for Toss Winners",
                         color_discrete_sequence=['#10B981', '#EF4444'], hole=0.4)
        st.plotly_chart(fig_pie, use_container_width=True)
        
    with col2:
        st.write("### Toss Decision Trends")
        decision_counts = match_df['Toss_Decision'].value_counts()
        fig_bar = px.bar(x=decision_counts.index, y=decision_counts.values,
                         labels={'x': 'Decision', 'y': 'Number of Matches'},
                         title="Bat vs Field First", color=decision_counts.index, template="plotly_white")
        st.plotly_chart(fig_bar, use_container_width=True)

with tab2:
    st.subheader("Venue Characteristics")
    venue_stats = match_df.groupby('Venue').agg({
        'Match_ID': 'count',
        'First_Innings_Score': 'mean'
    }).reset_index()
    venue_stats = venue_stats.rename(columns={'Match_ID': 'Matches Played', 'First_Innings_Score': 'Avg First Innings Score'})
    venue_stats = venue_stats.sort_values(by='Matches Played', ascending=False).head(10)
    
    fig_venue = px.bar(venue_stats, x='Venue', y='Avg First Innings Score',
                       color='Avg First Innings Score', color_continuous_scale="Oryel",
                       title="Average 1st Innings Score by Top Venues",
                       template="plotly_dark")
    st.plotly_chart(fig_venue, use_container_width=True)

with tab3:
    st.subheader("First Innings Score Distribution")
    fig_hist = px.histogram(match_df, x="First_Innings_Score", nbins=20,
                            title="Distribution of 1st Innings Scores",
                            labels={'First_Innings_Score': 'Runs Scored'},
                            color_discrete_sequence=['#3B82F6'], opacity=0.8,
                            template="plotly_white")
    st.plotly_chart(fig_hist, use_container_width=True)
    
    st.markdown("### Match Outcomes by Runs vs Wickets")
    win_types = ['Win_By_Runs', 'Win_By_Wickets']
    runs_wins = len(match_df[match_df['Win_By_Runs'] > 0])
    wkt_wins = len(match_df[match_df['Win_By_Wickets'] > 0])
    
    fig_outcomes = px.bar(x=['Defending (Runs)', 'Chasing (Wickets)'], y=[runs_wins, wkt_wins],
                          title="Defending vs Chasing Success",
                          labels={'x': 'Winning Method', 'y': 'Number of Matches'},
                          color=['Defending (Runs)', 'Chasing (Wickets)'], template="plotly_white")
    st.plotly_chart(fig_outcomes, use_container_width=True)
