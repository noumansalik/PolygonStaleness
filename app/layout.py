# app/layout.py
from dash import html, dcc
import dash_bootstrap_components as dbc

layout = dbc.Container([
    html.H2("48-Hour Latency Monitoring", className="text-center my-4"),

    dcc.Interval(id="interval", interval=1000, n_intervals=0),
    dcc.Store(id="data-store", data=[]),

    html.Div(id="time-info", className="text-center mb-2", style={"fontSize": "20px"}),
    html.Div(id="progress-info", className="text-center mb-4", style={"fontSize": "18px"}),

    dcc.Graph(id="line-graph"),
    dbc.Row([
        dbc.Col(dcc.Graph(id="pie-chart"), width=6),
        dbc.Col(dcc.Graph(id="bar-chart"), width=6),
    ])
], fluid=True)