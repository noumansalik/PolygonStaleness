import requests
import pandas as pd
import plotly.express as px
import dash
from dash import dcc, html, Output, Input
import dash_bootstrap_components as dbc
from datetime import datetime
import time

# --- Config ---
API_URL = "https://exs.redenvelope.dev/polygon/rate/USD-AUD/100"
HEALTHY_THRESHOLD = 2000  # ms
MAX_DURATION_SECONDS = 172800  # 2 days = 48 hours
REQUEST_INTERVAL_MS = 1000     # 1 second
MAX_RECORDS = MAX_DURATION_SECONDS
LATENCY_KEY = "Latency (ms)"

# Initialize app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "48-Hour Live Latency Monitor"

# Global in-memory store
data_store = []

# --- Layout ---
app.layout = dbc.Container([
    html.H2("48-Hour Latency Monitoring", className="text-center my-4"),

    dcc.Interval(id="interval", interval=REQUEST_INTERVAL_MS, n_intervals=0),
    dcc.Store(id="data-store", data=[]),

    html.Div(id="time-info", className="text-center mb-2", style={"fontSize": "20px"}),
    html.Div(id="progress-info", className="text-center mb-4", style={"fontSize": "18px"}),

    dcc.Graph(id="line-graph"),
    dbc.Row([
        dbc.Col(dcc.Graph(id="pie-chart"), width=6),
        dbc.Col(dcc.Graph(id="bar-chart"), width=6),
    ])
], fluid=True)

# --- Callback 1: Fetch latency + append to store + save CSV every 6h ---
@app.callback(
    Output("data-store", "data"),
    Input("interval", "n_intervals"),
    prevent_initial_call=False
)
def fetch_and_store(n):
    if n >= MAX_DURATION_SECONDS:
        # Final save
        pd.DataFrame(data_store).to_csv("latency_final.csv", index=False)
        print("✅ Final data saved. Monitoring complete.")
        return data_store

    try:
        response = requests.get(API_URL, timeout=3)
        response.raise_for_status()
        latency = response.json().get("latency")
    except Exception:
        latency = None

    timestamp = datetime.now().isoformat()
    data_store.append({"Timestamp": timestamp, LATENCY_KEY: latency})

    # Save snapshot every 6 hours
    if n % 21600 == 0 and n != 0:
        filename = f"latency_snapshot_{n // 3600:02d}h.csv"
        pd.DataFrame(data_store).to_csv(filename, index=False)
        print(f"💾 Saved 6-hour backup: {filename}")

    return data_store[-MAX_RECORDS:]  # keep memory usage bounded


# --- Callback 2: Update Graphs ---
@app.callback(
    Output("line-graph", "figure"),
    Output("pie-chart", "figure"),
    Output("bar-chart", "figure"),
    Input("data-store", "data")
)
def update_graphs(data):
    if not data:
        return dash.no_update, dash.no_update, dash.no_update

    df = pd.DataFrame(data)
    df["Timestamp"] = pd.to_datetime(df["Timestamp"])
    df = df.dropna()
    if df.empty:
        return dash.no_update, dash.no_update, dash.no_update

    df["Health"] = df[LATENCY_KEY].apply(
        lambda x: "Healthy" if x <= HEALTHY_THRESHOLD else "Unhealthy"
    )

    # Line chart
    line_fig = px.line(df, x="Timestamp", y=LATENCY_KEY, color="Health",
                       title="📈 Latency Over Time")

    # Pie chart
    health_counts = df["Health"].value_counts()
    pie_fig = px.pie(
        names=health_counts.index,
        values=health_counts.values,
        title="🩺 Health Distribution",
        hole=0.4,
        color_discrete_map={"Healthy": "#4CAF50", "Unhealthy": "#F44336"}
    )

    # Bar chart
    max_latency = df[LATENCY_KEY].max()
    avg_latency = df[LATENCY_KEY].mean()
    bar_fig = px.bar(
        x=["Max Latency", "Avg Latency"],
        y=[max_latency, avg_latency],
        title="📊 Staleness Overview",
        labels={"x": "Metric", "y": "Latency (ms)"}
    )

    return line_fig, pie_fig, bar_fig


# --- Callback 3: Update Time Elapsed, Remaining, and % ---
@app.callback(
    Output("time-info", "children"),
    Output("progress-info", "children"),
    Input("interval", "n_intervals")
)
def update_time(n):
    elapsed = min(n, MAX_DURATION_SECONDS)
    remaining = max(0, MAX_DURATION_SECONDS - elapsed)
    percent = (elapsed / MAX_DURATION_SECONDS) * 100

    def fmt(sec):
        return time.strftime('%H:%M:%S', time.gmtime(sec))

    time_display = f"⏱ Time Elapsed: {fmt(elapsed)} | ⏳ Time Remaining: {fmt(remaining)}"
    progress_display = f"📊 Progress: {percent:.2f}%"
    return time_display, progress_display


application = app  # required for Render

if __name__ == "__main__":
    app.run(debug=True)
