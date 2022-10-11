import dash
from dash import Dash, dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from torch import load as torch_load
import numpy as np
import string
import sys
import os
from collections import Counter
import math

# Custom module imports
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from web.layout import layout, graph_layout_names, graph_layout_letters
from models.lstm import LSTMGenerator

# Model instantiation
model = LSTMGenerator(128, 2)
model.load_state_dict(torch_load('models/trained/lstm2_hs128_bs128_ep100.pt'))

# App definition
app = Dash(
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    meta_tags=[
        {'name': 'viewport', 'content': 'width=device-width, initial-scale=1' }
    ],
    assets_folder='static',
    title='RX Name Generator'
)
app.layout = layout


@app.callback(
    Output('personal-info-toast', 'is_open'),
    Input('personal-info-toggle', 'n_clicks'),
    State('personal-info-toast', 'is_open'),
    prevent_initial_call=True
)
def open_personal_info(clicks, curr_state):
    '''
    Open or close the personal info pop-up when the logo in the top right of the site is clicked.

        Parameters:
            clicks (int): number of clicks of the logo button, only used to trigger callback
            curr_state (bool): flag for whether or not the pop up is currently open

        Returns:
            new_state (bool): flag for whether or not the pop up is open after the callback
    '''

    new_state = not curr_state
    return new_state


@app.callback(
    [Output('inputs-alert', 'children'),
     Output('inputs-alert', 'color'),
     Output('generate-button', 'disabled')],
    [Input('name-length-select', 'value'),
     Input('name-seed-input', 'value'),
     Input('name-num-input', 'value')]
)
def check_inputs(length, seed, num_gen):
    '''
    Assess the supplied inputs to provide help text and disable/enable the generation button.

        Parameters:
            length (str): user supplied input for the length of the name to generate
            seed (str): user supplied input for the seed string for the generator
            num_gen (int): user supplied input for number of names to generate

        Returns:
            alert_text (str): help message for the user to guide input entry
            color (str): bootstrap color for the alert styling
            disabled (bool): flag indicating if the generate button should be disabled
    '''

    allowed_letters = set(string.ascii_letters)
    if num_gen:
        if seed and length:
            seed_chars = set(seed)
            if not seed_chars.difference(allowed_letters):
                length = int(length)
                seed_len = len(seed)
                warning_len = math.ceil(length / 2)
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
     Output('name-index-select', 'max_value'),
     Output('generate-button', 'children')],
    Input('generate-button', 'n_clicks'),
    [State('name-length-select', 'value'),
     State('name-seed-input', 'value'),
     State('name-num-input', 'value')],
    prevent_initial_call=True
)
def populate_results(clicks, length, seed, num_gen):
    '''
    Generate names using user input and store them in a Dash storage component for use by other callbacks.

        Parameters:
            clicks (int): number of clicks of the generate button, only used to trigger callback
            length (str): user supplied input for length of name to generate
            seed (str): user supplied input for seed string given to generator
            num_gen (int): user supplied input for number of names to generate

        Returns:
            results (dict): dictionary containing different types of results from the model
            max_page (int): equal to num_gen, the max number of pages for navigating the word bank
            button_text (str): always "Generate", included to trigger loading icon when the predictions are processing
    '''

    results = {'names': []}
    seed = seed.lower()
    length = int(length)
    for i in range(num_gen):
        name = model.predict(seed, length)
        results['names'].append(name)
    likely_name, likely_prob = model.predict_max(seed, length)
    results['likely_name'] = likely_name
    results['likely_prob'] = likely_prob
    results['used_seed'] = seed
    max_page = num_gen
    button_text = 'Generate'
    return [results, max_page, button_text]


@app.callback(
    Output('name-index-select', 'active_page'),
    Input('results-storage', 'data'),
    prevent_initial_call=True
)
def reset_pagination(data):
    '''
    Move back to page 1 when new predictions are generated.

        Parameters:
            data (dict): new names generated from model, only used to trigger callback

        Returns:
            page (int): page to go to when new predictions arrive, always 1
    '''

    page = 1
    return page


@app.callback(
    [Output('name-viewer-1', 'children'),
     Output('name-viewer-2', 'children'),
     Output('name-viewer-3', 'children')],
    Input('name-index-select', 'active_page'),
    State('results-storage', 'data')
)
def show_name(page, data):
    '''
    Show the selected name and its two neighbors in the name viewer.

        Parameters:
            page (int): currently selected word index
            data (dict): model results dictionary
        
        Returns:
            view_1 (str): number and name to display in the topmost view panel
            view_2 (str): number and name to display in the middle/main view panel
            view_3 (str): number and name to display in the bottom view panel
    '''

    if not data:
        curr_num = page
        prev_num = page - 1 if page - 1 != 0 else 10
        next_num = page + 1 if page + 1 <= 10 else 1
        view_1, view_2, view_3 = f'{prev_num}.', f'{curr_num}.', f'{next_num}.'
    else:
        data = data['names']
        curr_num = page
        prev_num = page - 1 if page - 1 != 0 else len(data)
        next_num = page + 1 if page + 1 <= len(data) else 1
        prev_word, curr_word, next_word = data[page - 2], data[page - 1], data[page % (len(data))]
        view_1, view_2, view_3 = f'{prev_num}. {prev_word}', f'{curr_num}. {curr_word}', f'{next_num}. {next_word}'
    return [view_1, view_2, view_3]


@app.callback(
    [Output('unique-info', 'children'),
     Output('likely-info', 'children')],
    Input('results-storage', 'data'),
    prevent_initial_call=True
)
def fill_info(data):
    '''
    Fill the supplementary info section with model results.

        Parameters:
            data (dict): model results dictionary

        Returns:
            unique_info (str): text blurb describing the number of unique words generated
            likely_info (str): text blurb describing the most likely word for the given inputs
    '''

    if data:
        unique_names = list(set(data['names']))
        count = len(unique_names)
        prop = round(count / len(data['names']) * 100, 1)
        unique_info = f'This generation run produced {count} unique words (proportion of unique words: {prop}%)'
        likely_info = f'The theoretical most likely name for this combination of inputs is {data["likely_name"].capitalize()} (probability of being generated: {round(data["likely_prob"] * 100, 1)}%)'
        return [unique_info, likely_info]
    else:
        raise dash.exceptions.PreventUpdate


@app.callback(
    Output('name-graph', 'figure'),
    Input('results-storage', 'data'),
    prevent_initial_call=True
)
def fill_name_graph(data):
    '''
    Create the name distribution graph from the generated results.

        Parameters:
            data (dict): model results dictionary

        Returns:
            fig (plotly.graph_objects.Figure): Plotly graph instance containing name chart
    '''

    if data:
        names = data['names']
        total = len(names)
        name_freq = dict(Counter(names))
        sorted_names = sorted(name_freq.items(), key=lambda x: x[1], reverse=True)
        if len(sorted_names) > 10:
            sorted_names = sorted_names[:10]
        names_x = list(map(lambda x: x[0], sorted_names))
        probs_y = list(map(lambda x: x[1]/total, sorted_names))

        bar = go.Bar(
            x=names_x, y=probs_y,
            hovertemplate='<b>Name:</b> %{x}<br><b>Relative Freq:</b> %{y:.3f}<extra></extra>'
        )
        fig = go.Figure(
            data=[bar],
            layout=graph_layout_names
        )

        return fig
    else:
        raise dash.exceptions.PreventUpdate

@app.callback(
    Output('letter-graph', 'figure'),
    Input('results-storage', 'data'),
    prevent_initial_call=True
)
def fill_letter_graph(data):
    '''
    Create the letter distribution graph from the generated results.

        Parameters:
            data (dict): model results dictionary

        Returns:
            fig (plotly.graph_objects.Figure): Plotly graph instance containing letter chart
    '''

    if data:
        names = data['names']
        letters_trim = list(map(lambda x: list(x[len(data['used_seed']):]), names))
        letters_flat = list(np.array(letters_trim).flatten())
        total = len(letters_flat)
        name_freq = dict(Counter(letters_flat))
        letters_x = list(string.ascii_lowercase)
        probs_y = [name_freq[letter]/total for letter in letters_flat]

        bar = go.Bar(
            x=letters_x, y=probs_y,
            hovertemplate='<b>Letter:</b> %{x}<br><b>Relative Freq:</b> %{y:.3f}<extra></extra>'
        )
        fig = go.Figure(
            data=[bar],
            layout=graph_layout_letters
        )

        return fig
    else:
        raise dash.exceptions.PreventUpdate


# Run the server 
if __name__ == '__main__':
    app.run_server(debug=True)
