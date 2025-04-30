import dash
from dash import html

app = dash.Dash(__name__)
app.layout = html.Div("✅ Hello from Dash on Render!")

application = app  # THIS IS CRUCIAL for Gunicorn

if __name__ == "__main__":
    app.run(debug=True)
