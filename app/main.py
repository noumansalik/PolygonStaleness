# app/main.py
from dash import Dash
import dash_bootstrap_components as dbc
from app.layout import layout
from app.callbacks import register_callbacks

# Create Dash app
app = Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    suppress_callback_exceptions=True
)
app.title = "48-Hour Live Latency Monitor"
app.layout = layout

# Register all callbacks
register_callbacks(app)

# Expose for Gunicorn
application = app

if __name__ == "main":
    app.run(debug=True)