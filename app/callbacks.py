# app/callbacks.py
import requests
import pandas as pd
from datetime import datetime
import time
import plotly.express as px
from dash import Input, Output, no_update

# Monitoring configuration
API_URL = "https://exs.redenvelope.dev/polygon/rate/USD-AUD/100"
HEALTHY_THRESHOLD = 2000  # ms
MAX_DURATION_SECONDS = 172800  # 2 days = 48 hours
LATENCY_KEY = "Latency (ms)"

# In-memory store
_data_store = []


def register_callbacks(app):
    # Fetch & store
    @app.callback(
        Output("data-store", "data"),
        Input("interval", "n_intervals"),
        prevent_initial_call=False
    )
    def fetch_and_store(n):
        if n >= MAX_DURATION_SECONDS:
            pd.DataFrame(_data_store).to_csv("latency_final.csv", index=False)
            print("✅ Final data saved. Monitoring complete.")
            return _data_store

        try:
            resp = requests.get(API_URL, timeout=3)
            resp.raise_for_status()
            latency = resp.json().get("latency")
        except Exception:
            latency = None

        ts = datetime.now().isoformat()
        _data_store.append({"Timestamp": ts, LATENCY_KEY: latency})

        # Backup every 6h
        if n % 21600 == 0 and n != 0:
            fn = f"latency_snapshot_{n // 3600:02d}h.csv"
            pd.DataFrame(_data_store).to_csv(fn, index=False)
            print(f"💾 Saved 6-hour backup: {fn}")

        return _data_store

    # Graph updates
    @app.callback(
        Output("line-graph", "figure"),
        Output("pie-chart", "figure"),
        Output("bar-chart", "figure"),
        Input("data-store", "data")
    )
    def update_graphs(data):
        if not data:
            return no_update, no_update, no_update

        df = pd.DataFrame(data)
        df["Timestamp"] = pd.to_datetime(df["Timestamp"])
        df = df.dropna()
        if df.empty:
            return no_update, no_update, no_update

        df["Health"] = df[LATENCY_KEY].apply(
            lambda x: "Healthy" if x < HEALTHY_THRESHOLD else "Unhealthy"
        )

        line_fig = px.line(
            df, x="Timestamp", y=LATENCY_KEY, color="Health",
            title="📈 Latency Over Time"
        )

        counts = df["Health"].value_counts()
        pie_fig = px.pie(
            names=counts.index,
            values=counts.values,
            title="🩺 Health Distribution",
            hole=0.4,
            color_discrete_map={"Healthy": "#4CAF50", "Unhealthy": "#F44336"}
        )

        max_lat = df[LATENCY_KEY].max()
        avg_lat = df[LATENCY_KEY].mean()
        bar_fig = px.bar(
            x=["Max Latency", "Avg Latency"],
            y=[max_lat, avg_lat],
            title="📊 Staleness Overview",
            labels={"x": "Metric", "y": "Latency (ms)"}
        )

        return line_fig, pie_fig, bar_fig

    # Time tracker
    @app.callback(
        Output("time-info", "children"),
        Output("progress-info", "children"),
        Input("interval", "n_intervals")
    )
    def update_time(n):
        elapsed = min(n, MAX_DURATION_SECONDS)
        remaining = max(0, MAX_DURATION_SECONDS - elapsed)
        pct = (elapsed / MAX_DURATION_SECONDS) * 100

        def fmt(s):
            return time.strftime('%H:%M:%S', time.gmtime(s))

        return (
            f"⏱ Time Elapsed: {fmt(elapsed)} | ⏳ Time Remaining: {fmt(remaining)}",
            f"📊 Progress: {pct:.2f}%"
        )