import dash
from dash import Dash, dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
import string
from torch import load as torch_load
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from web.layout import layout
from models.lstm import LSTMGenerator


# Model Instantiation

model = LSTMGenerator(128, 2)
model.load_state_dict(torch_load('models/trained/lstm2_hs128_bs128_ep100.pt'))


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
    Input('personal-info-toggle', 'n_clicks'),
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

@app.callback(
    [Output('results-storage', 'data'),
     Output('name-index-select', 'max_value')],
    Input('generate-button', 'n_clicks'),
    [State('name-length-select', 'value'),
     State('name-seed-input', 'value'),
     State('name-num-input', 'value')],
    prevent_initial_call=True
)
def populate_results(clicks, length, seed, num_gen):
    results = []
    seed = seed.lower()
    length = int(length)
    for i in range(num_gen):
        name = model.predict(seed, length)
        results.append(name)
    return [results, num_gen]

@app.callback(
    Output('name-index-select', 'active_page'),
    Input('results-storage', 'data'),
    prevent_initial_call=True
)
def reset_pagination(data):
    return 1

@app.callback(
    [Output('name-viewer-1', 'children'),
     Output('name-viewer-2', 'children'),
     Output('name-viewer-3', 'children')],
    Input('name-index-select', 'active_page'),
    State('results-storage', 'data')
)
def show_name(page, data):
    if not data:
        curr_num = page
        prev_num = page - 1 if page - 1 != 0 else 10
        next_num = page + 1 if page + 1 <= 10 else 1
        return [f'{prev_num}.', f'{curr_num}.', f'{next_num}.']
    else:
        curr_num = page
        prev_num = page - 1 if page - 1 != 0 else len(data)
        next_num = page + 1 if page + 1 <= len(data) else 1
        prev_word, curr_word, next_word = data[page - 2], data[page - 1], data[page % (len(data))]
        return [f'{prev_num}. {prev_word}', f'{curr_num}. {curr_word}', f'{next_num}. {next_word}']

@app.callback(
    Output('unique-info', 'children'),
    Input('results-storage', 'data'),
    prevent_initial_call=True
)
def calculate_unique(data):
    if data:
        unique_names = list(set(data))
        count = len(unique_names)
        prop = round(count / len(data) * 100, 1)
        return f'This generation run produced {count} unique words (proportion of unique words: {prop}%)'
    else:
        raise dash.exceptions.PreventUpdate


# Run the Server 

if __name__ == '__main__':
    app.run_server(debug=True)
