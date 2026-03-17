from flask import Flask, render_template, request, redirect, url_for, flash
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from modules.data_loader import (
    load_team_stats, load_batting_stats, load_match_data, load_bowling_stats,
    get_table_columns, add_record, delete_record, update_record
)
import json

app = Flask(__name__)
app.secret_key = 'ipl_secret_key' # For flash messages

# Helper to load data
def _get_quick_facts():
    team_df = load_team_stats()
    bat_df = load_batting_stats()
    match_df = load_match_data()
    
    facts = {
        'total_matches': 1000,
        'top_scorer_name': 'Unknown',
        'top_scorer_runs': 0,
        'seasons_covered': 0
    }
    
    if not team_df.empty and 'Matches Played' in team_df.columns:
        facts['total_matches'] = int(team_df['Matches Played'].sum() / 2)
    elif not match_df.empty:
        facts['total_matches'] = len(match_df)
        
    if not bat_df.empty and 'Runs' in bat_df.columns:
        player_col = 'Player' if 'Player' in bat_df.columns else bat_df.columns[0]
        top_scorer = bat_df.iloc[0]
        facts['top_scorer_name'] = top_scorer[player_col]
        facts['top_scorer_runs'] = top_scorer['Runs']
        
    if not match_df.empty and 'Season' in match_df.columns:
        facts['seasons_covered'] = match_df['Season'].nunique()
        
    return facts

@app.route('/')
def index():
    facts = _get_quick_facts()
    return render_template('index.html', facts=facts)

@app.route('/player')
def player_analysis():
    bat_df = load_batting_stats()
    bowl_df = load_bowling_stats()
    
    if bat_df.empty and bowl_df.empty:
        return render_template('player.html', error="No player data available. Please check the database.")
        
    charts = {}
    
    # --- BATTING CHARTS ---
    if not bat_df.empty:
        player_col = 'Player' if 'Player' in bat_df.columns else bat_df.columns[0]
        runs_col = 'Runs' if 'Runs' in bat_df.columns else (bat_df.columns[2] if len(bat_df.columns)>2 else None)
        sr_col = 'Strike Rate' if 'Strike Rate' in bat_df.columns else None
        
        if runs_col:
            # Top 50 Batsmen by default
            bat_df_sorted = bat_df.sort_values(by=runs_col, ascending=False).head(50)
            
            # Default comparison: top 5 players
            top_5_players = bat_df_sorted[player_col].head(5).tolist()
            filtered_bat = bat_df_sorted[bat_df_sorted[player_col].isin(top_5_players)]
            
            fig1 = px.bar(filtered_bat, x=player_col, y=runs_col, color=player_col, 
                         title="Total Runs by Selected Players",
                         color_discrete_sequence=['#1E3A8A', '#3A82F6', '#10B981', '#F59E0B', '#EF4444'],
                         template="plotly_dark")
            fig1.update_layout(margin=dict(l=20, r=20, t=40, b=20), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='white')
            charts['bat_bar'] = fig1.to_html(full_html=False, include_plotlyjs=False)
            
            if sr_col:
                # Convert strings to float for scatter plot
                bat_df_sorted[runs_col] = bat_df_sorted[runs_col].astype(str).str.replace(',', '').astype(float)
                bat_df_sorted[sr_col] = bat_df_sorted[sr_col].astype(str).str.replace('-', '0').astype(float)
                
                fig2 = px.scatter(bat_df_sorted, x=runs_col, y=sr_col, hover_name=player_col,
                                  size=runs_col, color=sr_col,
                                  title="Aggression vs Consistency",
                                  labels={runs_col: "Total Career Runs", sr_col: "Career Strike Rate"},
                                  template="plotly_dark", size_max=40, color_continuous_scale="Viridis")
                fig2.update_layout(margin=dict(l=20, r=20, t=40, b=20), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='white')
                charts['bat_scatter'] = fig2.to_html(full_html=False, include_plotlyjs=False)
                
    # --- BOWLING CHARTS ---
    if not bowl_df.empty:
        player_col = 'Player' if 'Player' in bowl_df.columns else bowl_df.columns[0]
        wkts_col = 'Wickets' if 'Wickets' in bowl_df.columns else None
        
        if wkts_col:
            bowl_df_sorted = bowl_df.sort_values(by=wkts_col, ascending=False).head(15)
            bowl_df_sorted[wkts_col] = bowl_df_sorted[wkts_col].astype(str).str.replace(',', '').astype(float)
            
            fig_bowl = px.bar(bowl_df_sorted, x=player_col, y=wkts_col, 
                              color=wkts_col, color_continuous_scale="Viridis",
                              title="Top 15 All-Time Wicket Takers", template="plotly_dark")
            fig_bowl.update_layout(margin=dict(l=20, r=20, t=40, b=20), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='white')
            charts['bowl_bar'] = fig_bowl.to_html(full_html=False, include_plotlyjs=False)

    return render_template('player.html', charts=charts)

@app.route('/team')
def team_analysis():
    team_df = load_team_stats()
    
    if team_df.empty:
        return render_template('team.html', error="No team data available.")
        
    charts = {}
    
    cols = list(team_df.columns)
    team_col = win_col = loss_col = win_pct_col = None
    for c in cols:
        cl = c.lower()
        if 'team' in cl or 'franchise' in cl: team_col = c
        elif 'win' in cl and '%' not in cl and 'percentage' not in cl: win_col = c
        elif 'loss' in cl: loss_col = c
        elif '%' in cl or 'rate' in cl: win_pct_col = c
        
    if team_col and win_col:
        team_df[win_col] = team_df[win_col].astype(str).str.replace(r'[^0-9]', '', regex=True).replace('', '0').astype(float)
        
        if loss_col:
            team_df[loss_col] = team_df[loss_col].astype(str).str.replace(r'[^0-9]', '', regex=True).replace('', '0').astype(float)
        if win_pct_col:
            team_df[win_pct_col] = team_df[win_pct_col].astype(str).str.replace(r'[^0-9.]', '', regex=True).replace('', '0').astype(float)
        
        team_df = team_df.sort_values(by=win_col, ascending=False).head(15)
        
        # Wins chart
        fig1 = px.bar(team_df, x=win_col, y=team_col, orientation='h',
                      color=win_col, color_continuous_scale="Blues",
                      template="plotly_dark", title="All-Time Wins by Franchise")
        fig1.update_layout(margin=dict(l=20, r=20, t=40, b=20), yaxis={'categoryorder':'total ascending'}, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='white')
        charts['wins'] = fig1.to_html(full_html=False, include_plotlyjs=False)
        
        if win_pct_col:
            fig2 = px.bar(team_df.sort_values(by=win_pct_col, ascending=True), 
                          x=win_pct_col, y=team_col, orientation='h',
                          color=win_pct_col, color_continuous_scale="RdYlGn",
                          template="plotly_dark", title="Win Percentage Leaderboard")
            fig2.update_layout(margin=dict(l=20, r=20, t=40, b=20), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='white')
            charts['winpct'] = fig2.to_html(full_html=False, include_plotlyjs=False)
        elif loss_col:
            melted = pd.melt(team_df, id_vars=[team_col], value_vars=[win_col, loss_col])
            fig2 = px.bar(melted, x='value', y=team_col, color='variable', barmode='group',
                          orientation='h', template="plotly_dark",
                          color_discrete_sequence=['#10B981', '#EF4444'], title="Wins vs Losses")
            fig2.update_layout(margin=dict(l=20, r=20, t=40, b=20), yaxis={'categoryorder':'total ascending'}, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='white')
            charts['winpct'] = fig2.to_html(full_html=False, include_plotlyjs=False)

    return render_template('team.html', charts=charts)

@app.route('/match')
def match_insights():
    match_df = load_match_data()
    if match_df.empty:
        return render_template('match.html', error="No match data available.")
        
    charts = {}
    
    season_filter = request.args.get('season', 'All')
    seasons = sorted(match_df['Season'].unique().tolist(), reverse=True)
    
    filtered_df = match_df if season_filter == 'All' else match_df[match_df['Season'] == season_filter]
    
    if not filtered_df.empty:
        # Toss Impact
        filtered_df['Toss_Winner_is_Match_Winner'] = filtered_df['Toss_Winner'] == filtered_df['Match_Winner']
        toss_win_count = filtered_df['Toss_Winner_is_Match_Winner'].value_counts()
        
        fig_pie = px.pie(values=toss_win_count.values, names=['Won Match', 'Lost Match'], 
                         title="Match Outcomes for Toss Winners",
                         color_discrete_sequence=['#10B981', '#EF4444'], hole=0.4, template="plotly_dark")
        fig_pie.update_layout(margin=dict(l=20, r=20, t=40, b=20), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='white')
        charts['toss_pie'] = fig_pie.to_html(full_html=False, include_plotlyjs=False)
        
        # Toss Decisions
        decision_counts = filtered_df['Toss_Decision'].value_counts()
        fig_bar = px.bar(x=decision_counts.index, y=decision_counts.values,
                         labels={'x': 'Decision', 'y': 'Number of Matches'},
                         title="Bat vs Field First", color=decision_counts.index, template="plotly_dark",
                         color_discrete_sequence=['#3B82F6', '#F59E0B'])
        fig_bar.update_layout(margin=dict(l=20, r=20, t=40, b=20), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='white')
        charts['toss_bar'] = fig_bar.to_html(full_html=False, include_plotlyjs=False)
        
        # Venues
        venue_stats = filtered_df.groupby('Venue').agg({
            'Match_ID': 'count',
            'First_Innings_Score': 'mean'
        }).reset_index().rename(columns={'Match_ID': 'Matches Played', 'First_Innings_Score': 'Avg First Innings Score'})
        venue_stats = venue_stats.sort_values(by='Matches Played', ascending=False).head(10)
        
        fig_venue = px.bar(venue_stats, x='Venue', y='Avg First Innings Score',
                           color='Avg First Innings Score', color_continuous_scale="Oryel",
                           title="Average 1st Innings Score by Top Venues",
                           template="plotly_dark")
        fig_venue.update_layout(margin=dict(l=20, r=20, t=40, b=20), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='white')
        charts['venues'] = fig_venue.to_html(full_html=False, include_plotlyjs=False)
        
        # Score distribution
        fig_hist = px.histogram(filtered_df, x="First_Innings_Score", nbins=20,
                                title="Distribution of 1st Innings Scores",
                                labels={'First_Innings_Score': 'Runs Scored'},
                                color_discrete_sequence=['#8B5CF6'], opacity=0.8,
                                template="plotly_dark")
        fig_hist.update_layout(margin=dict(l=20, r=20, t=40, b=20), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='white')
        charts['scores'] = fig_hist.to_html(full_html=False, include_plotlyjs=False)

    return render_template('match.html', charts=charts, seasons=seasons, selected_season=season_filter)

@app.route('/admin')
def admin_dashboard():
    table = request.args.get('table', 'team_stats')
    df = pd.DataFrame()
    if table == 'team_stats': df = load_team_stats()
    elif table == 'batting_stats': df = load_batting_stats()
    elif table == 'bowling_stats': df = load_bowling_stats()
    elif table == 'match_data': df = load_match_data()
    
    columns = get_table_columns(table)
    data = df.to_dict('records')
    
    return render_template('admin.html', table=table, columns=columns, data=data)

@app.route('/admin/add/<table>', methods=['POST'])
def admin_add(table):
    columns = get_table_columns(table)
    data = {col: request.form.get(col) for col in columns if request.form.get(col)}
    success, msg = add_record(table, data)
    if success: flash(f"Record added to {table} successfully!", "success")
    else: flash(f"Error adding record: {msg}", "error")
    return redirect(url_for('admin_dashboard', table=table))

@app.route('/admin/delete/<table>/<id_col>/<id_val>', methods=['POST'])
def admin_delete(table, id_col, id_val):
    success, msg = delete_record(table, id_col, id_val)
    if success: flash(f"Record deleted from {table}!", "success")
    else: flash(f"Error deleting record: {msg}", "error")
    return redirect(url_for('admin_dashboard', table=table))

if __name__ == '__main__':
    app.run(debug=True, port=5000)
