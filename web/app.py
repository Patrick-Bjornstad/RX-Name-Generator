from dash import Dash, dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
import string

from layout import layout

# App Definition

app = Dash(
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    meta_tags=[
        {'name': 'viewport', 'content': 'width=device-width, initial-scale=1' }
    ],
    assets_folder='static/',
    title='RX Name Generator'
)

app.layout = layout


# App Callbacks

@app.callback(
    Output('personal-info-toast', 'is_open'),
    [Input('personal-info-toggle', 'n_clicks')],
    prevent_initial_call=True
)
def open_personal_info(clicks):
    return True

@app.callback(
    [Output('inputs-alert', 'children'),
     Output('inputs-alert', 'color'),
     Output('generate-button', 'disabled')],
    [Input('name-length-select', 'value'),
     Input('name-seed-input', 'value'),
     Input('name-num-input', 'value')]
)
def check_inputs(length, seed, num_gen):

    allowed_letters = set(string.ascii_letters)

    if num_gen:
        if seed and length:
            seed_chars = set(seed)
            if not seed_chars.difference(allowed_letters):
                length = int(length)
                seed_len = len(seed)
                warning_len = length // 2
                if seed_len >= length:
                    alert_text = 'Your seed length is longer than the requested name length! Try a shorter seed or a longer name...'
                    color = 'danger'
                    disabled = True
                elif seed_len >= warning_len:
                    alert_text = f'Your seed length is fairly long compared to the requested name length! Only {length - seed_len} characters will be generated.'
                    color = 'warning'
                    disabled = False
                else:
                    alert_text = 'Press the generate button to produce results!'
                    color = 'success'
                    disabled = False
            else:
                alert_text = 'Invalid characters present in the seed. Only upper or lowercase English letters are allowed!'
                color = 'danger'
                disabled = True
        else:
            alert_text = 'Input how many names to generate, the desired name length, and a seed string to get started...'
            color = 'warning'
            disabled = True
    else:
        alert_text = 'Ensure that the specified number of names is an integer between 10 and 100...'
        color='danger'
        disabled=True

    return [alert_text, color, disabled]

# Run the Server 

if __name__ == '__main__':
    app.run_server(debug=True)
