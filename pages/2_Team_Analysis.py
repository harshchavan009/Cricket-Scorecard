import streamlit as st
import plotly.express as px
from modules.data_loader import load_team_stats

st.set_page_config(page_title="Team Analysis", page_icon="🛡️", layout="wide")

st.markdown("# 🛡️ Team Performance Analytics")
st.markdown("Analyze historical success, win percentages, and overall standings of IPL Franchises.")

team_df = load_team_stats()

if team_df.empty:
    st.error("No team data available.")
    st.stop()
    
# Clean up data just in case
cols = list(team_df.columns)
team_col = None
win_col = None
loss_col = None
win_pct_col = None

for c in cols:
    cl = c.lower()
    if 'team' in cl or 'franchise' in cl: team_col = c
    elif 'win' in cl and '%' not in cl and 'percentage' not in cl: win_col = c
    elif 'loss' in cl: loss_col = c
    elif '%' in cl or 'rate' in cl: win_pct_col = c
    
if team_col and win_col:
    # Ensure numerics
    team_df[win_col] = team_df[win_col].astype(str).str.replace(r'[^0-9]', '', regex=True)
    team_df[win_col] = team_df[win_col].replace('', '0').astype(float)
    
    if loss_col:
        team_df[loss_col] = team_df[loss_col].astype(str).str.replace(r'[^0-9]', '', regex=True)
        team_df[loss_col] = team_df[loss_col].replace('', '0').astype(float)

    if win_pct_col:
        team_df[win_pct_col] = team_df[win_pct_col].astype(str).str.replace(r'[^0-9.]', '', regex=True)
        team_df[win_pct_col] = team_df[win_pct_col].replace('', '0').astype(float)
    
    team_df = team_df.sort_values(by=win_col, ascending=False).head(15) # top active+defunct teams

    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("All-Time Wins by Franchise")
        fig1 = px.bar(team_df, x=win_col, y=team_col, orientation='h',
                      color=win_col, color_continuous_scale="Blues",
                      template="plotly_white")
        fig1.update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig1, use_container_width=True)
        
    with col2:
        if win_pct_col:
            st.subheader("Win Percentage Leaderboard")
            fig2 = px.bar(team_df.sort_values(by=win_pct_col, ascending=True), 
                          x=win_pct_col, y=team_col, orientation='h',
                          color=win_pct_col, color_continuous_scale="RdYlGn",
                          template="plotly_white")
            st.plotly_chart(fig2, use_container_width=True)
        elif loss_col:
            # calculate it if missing
            st.subheader("Wins vs Losses")
            import pandas as pd
            melted = pd.melt(team_df, id_vars=[team_col], value_vars=[win_col, loss_col])
            fig2 = px.bar(melted, x='value', y=team_col, color='variable', barmode='group',
                          orientation='h', template="plotly_white",
                          color_discrete_sequence=['#10B981', '#EF4444'])
            fig2.update_layout(yaxis={'categoryorder':'total ascending'})
            st.plotly_chart(fig2, use_container_width=True)
            
    st.markdown("### Detailed Team Statistics Table")
    st.dataframe(team_df.set_index(team_col), use_container_width=True)
else:
    st.write(team_df)
    st.warning("Could not automatically map the team columns from the scraped Wikipedia data. Displaying raw data table instead.")
