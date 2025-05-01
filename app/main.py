# app/main.py

from dash import Dash
import dash_bootstrap_components as dbc
from app.layout import layout
from app.callbacks import register_callbacks

# Create the Dash app instance
app = Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    suppress_callback_exceptions=True
)
app.title = "48-Hour Live Latency Monitor"

# Set layout and register callbacks
app.layout = layout
register_callbacks(app)

# Expose for Gunicorn (must be at global scope!)
application = app

# Local dev server
if __name__ == "__main__":
    app.run(debug=True)
