from dash import Dash, dcc, html, Input, Output, State
import dash_bootstrap_components as dbc

app = Dash(
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    meta_tags=[
        {'name': 'viewport', 'content': 'width=device-width, initial-scale=1' }
    ],
    assets_folder='static/'
)

app.layout = html.Div(
    'RX Name Generator: Temporary',
    className='text-center fs-4'
)

if __name__ == '__main__':
    app.run_server(debug=True)
