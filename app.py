import dash
from dash import html

app = dash.Dash(__name__)
app.layout = html.Div(" Hello from Dash!\")

application = app  #  this must be at the top level

if __name__ == "__main__\":
    app.run(debug=True)
