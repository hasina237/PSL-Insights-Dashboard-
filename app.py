import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go


# PAGE CONFIG

st.set_page_config(
    page_title="Cricket Analytics Dashboard",
    page_icon="🏏",
    layout="wide"
)


# LOAD DATA

@st.cache_data
def load_data():
    return pd.read_csv("Cricket_Data.csv")

df = load_data()


# SIDEBAR FILTERS

st.sidebar.title("🏏 Cricket Analytics")

season = st.sidebar.multiselect(
    "Select Season",
    sorted(df["season"].unique()),
    default=sorted(df["season"].unique())
)

batting_team = st.sidebar.multiselect(
    "Batting Team",
    sorted(df["batting_team"].unique()),
    default=sorted(df["batting_team"].unique())
)

bowling_team = st.sidebar.multiselect(
    "Bowling Team",
    sorted(df["bowling_team"].unique()),
    default=sorted(df["bowling_team"].unique())
)

filtered_df = df[
    (df["season"].isin(season)) &
    (df["batting_team"].isin(batting_team)) &
    (df["bowling_team"].isin(bowling_team))
]


# TITLE

st.title("🏏 Advanced Cricket Analytics Dashboard")
st.markdown("---")


# KPI CARDS

total_runs = filtered_df["total_runs"].sum()
total_wickets = filtered_df["is_wicket"].sum()
total_fours = filtered_df["is_four"].sum()
total_sixes = filtered_df["is_six"].sum()

col1, col2, col3, col4 = st.columns(4)

col1.metric("Runs", f"{total_runs:,}")
col2.metric("Wickets", f"{total_wickets:,}")
col3.metric("Fours", f"{total_fours:,}")
col4.metric("Sixes", f"{total_sixes:,}")

st.markdown("---")


# TABS

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(
    ["Team Analysis",
     "Batter Analysis",
     "Bowler Analysis",
     "Fantasy Points",
     "Death Overs", 
     'Player VS Player Analysis']
)


# TEAM ANALYSIS

with tab1:

    st.subheader("Team Runs")

    team_runs = (
        filtered_df.groupby("batting_team")["total_runs"]
        .sum()
        .reset_index()
        .sort_values("total_runs", ascending=False)
    )

    fig = px.bar(
        team_runs,
        x="batting_team",
        y="total_runs",
        color="total_runs",
        text="total_runs"
    )

    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Season Wise Runs")

    season_runs = (
        filtered_df.groupby("season")["total_runs"]
        .sum()
        .reset_index()
    )

    fig = px.line(
        season_runs,
        x="season",
        y="total_runs",
        markers=True
    )

    st.plotly_chart(fig, use_container_width=True)


# BATTER ANALYSIS

with tab2:

    batter = st.selectbox(
        "Select Batter",
        sorted(filtered_df["batter"].dropna().unique())
    )

    batter_df = filtered_df[
        filtered_df["batter"] == batter
    ]

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Runs",
        batter_df["batsman_runs"].sum()
    )

    col2.metric(
        "Fours",
        batter_df["is_four"].sum()
    )

    col3.metric(
        "Sixes",
        batter_df["is_six"].sum()
    )

    over_runs = (
        batter_df.groupby("over")["batsman_runs"]
        .sum()
        .reset_index()
    )

    fig = px.area(
        over_runs,
        x="over",
        y="batsman_runs",
        title="Runs by Over"
    )

    st.plotly_chart(fig, use_container_width=True)


# BOWLER ANALYSIS

with tab3:

    bowler = st.selectbox(
        "Select Bowler",
        sorted(filtered_df["bowler"].dropna().unique())
    )

    bowler_df = filtered_df[
        filtered_df["bowler"] == bowler
    ]

    wickets = bowler_df["is_wicket"].sum()
    runs_conceded = bowler_df["total_runs"].sum()

    col1, col2 = st.columns(2)

    col1.metric("Wickets", wickets)
    col2.metric("Runs Conceded", runs_conceded)

    dismissal = (
        bowler_df.groupby("dismissal_kind")
        .size()
        .reset_index(name="count")
    )

    fig = px.pie(
        dismissal,
        names="dismissal_kind",
        values="count",
        title="Dismissal Types"
    )

    st.plotly_chart(fig, use_container_width=True)


# FANTASY ANALYSIS

with tab4:

    fantasy = (
        filtered_df.groupby("batter")["fantasy_points"]
        .sum()
        .reset_index()
        .sort_values("fantasy_points", ascending=False)
        .head(15)
    )

    fig = px.bar(
        fantasy,
        x="batter",
        y="fantasy_points",
        color="fantasy_points",
        title="Top Fantasy Players"
    )

    st.plotly_chart(fig, use_container_width=True)

# DEATH OVER ANALYSIS

with tab5:

    death_df = filtered_df[
        filtered_df["death_over"] == 1
    ]

    death_runs = (
        death_df.groupby("batting_team")["total_runs"]
        .sum()
        .reset_index()
    )

    fig = px.bar(
        death_runs,
        x="batting_team",
        y="total_runs",
        color="total_runs",
        title="Death Over Runs"
    )

    st.plotly_chart(fig, use_container_width=True)

    wicket_analysis = (
        death_df.groupby("bowling_team")["is_wicket"]
        .sum()
        .reset_index()
    )

    fig = px.scatter(
        wicket_analysis,
        x="bowling_team",
        y="is_wicket",
        size="is_wicket",
        title="Death Over Wickets"
    )

    st.plotly_chart(fig, use_container_width=True)


# PLAYER VE PLAYER ANALYSIS 

with tab6:
    st.header('Player vs Player Analysis')

    batter = st.selectbox('Select Better ', sorted(df['batter'].dropna().unique()))
    bowler = st.selectbox('Select Bowler ', sorted(df['bowler'].dropna().unique()))

    matchup = df[(df['bowler'] == bowler) & (df['batter'] == batter)]
    runs = matchup['batsman_runs'].sum()

    balls = len(matchup)
   
    outs = (matchup['player_dismissed'] != 'Not Out').sum()

    if balls > 0:
        sr = round((runs / balls) * 100, 2)
    else:
        sr = 0
    if outs > 0:
        AVG = round(runs / outs, 2)
    else:
        AVG = runs
    
    st.metric('Runs',runs)
    st.metric('Balls', balls)
    st.metric('Dismissals', outs)
    st.metric('Strike Rate', sr)

    stats_df = pd.DataFrame({
        'Metric' : ['Runs','Balls','Dismissals'],
        'Value' : [runs,balls,outs]
    })

    
    fig = px.bar(stats_df, x= 'Metric', y= 'Value',title= f'{batter} vs {bowler}')
    st.plotly_chart(fig, use_container_width=True)


# --------------------------
# RAW DATA
# --------------------------
with st.expander("View Dataset"):
    st.dataframe(filtered_df)
    
