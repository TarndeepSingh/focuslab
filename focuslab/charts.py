"""Plotly figure builders."""
import plotly.express as px
import plotly.graph_objects as go

ACCENT = "#6C5CE7"


def _style(fig, height=340):
    fig.update_layout(template="plotly_dark", height=height, margin=dict(l=10, r=10, t=40, b=10),
                      paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    return fig


def weekly_chart(df):
    fig = px.bar(df, x="week", y="hours", title="Weekly study hours", color_discrete_sequence=[ACCENT])
    fig.update_xaxes(title=None)
    fig.update_yaxes(title="Hours")
    return _style(fig)


def daily_chart(df):
    fig = px.area(df, x="day", y="minutes", title="Daily focus minutes", color_discrete_sequence=[ACCENT])
    fig.update_xaxes(title=None)
    return _style(fig)


def subject_chart(df):
    fig = px.pie(df, names="subject", values="hours", hole=0.55, title="Time by subject")
    fig.update_traces(textinfo="percent+label")
    return _style(fig)


def heatmap_chart(pivot):
    fig = go.Figure(go.Heatmap(z=pivot.values, x=list(pivot.columns), y=list(pivot.index),
                               colorscale="Purples", colorbar=dict(title="min")))
    fig.update_layout(title="When you focus (weekday × hour)")
    fig.update_xaxes(title="Hour of day", dtick=2)
    return _style(fig, 300)
