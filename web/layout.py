from dash import html, dcc
import dash_bootstrap_components as dbc
import plotly.graph_objects as go

navbar = dbc.Navbar(
    dbc.Container(
        [
            dbc.Row(
                [
                    dbc.Col(html.Img(src='/static/images/logo_site.svg', height='60px')),
                    dbc.Col(dbc.NavbarBrand('LSTM Prescription Brand Name Generator', class_name='h1 text-light ps-2 fs-3 fw-bolder')),
                ],
                align='center',
                class_name='g-0'
            ),
            dbc.Row(
                [
                    dbc.Col(
                        dbc.Button(
                            html.Img(src='/static/images/logo_web_light.png', height='60px'),
                            id='personal-info-toggle',
                            color='dark',
                            class_name='p-1',
                            outline=True
                        )
                    )
                ],
                align='center'
            )   
        ],
        fluid=True
    ),
    color='dark',
    style={'height': '100px'}
)

personal_info = dbc.Toast(
    [
        dbc.Row(
            [
                dbc.Col(html.Img(src='/static/images/github.svg', height='40px'), width='auto'),
                dbc.Col(html.A('Profile', href='https://github.com/Patrick-Bjornstad', className='fs-6'), width='auto'),
                dbc.Col(html.A('Project Repository', href='', className='fs-6'), width='auto')
            ],
            align='center',
            class_name='pb-3',
        ),
        dbc.Row(
            [
                dbc.Col(html.Img(src='/static/images/linkedin.svg', height='40px'), width='auto'),
                dbc.Col(html.A('Profile', href='https://www.linkedin.com/in/patrick-bjornstad-216753163/', className='fs-6'), width='auto')
            ],
            align='center'
        )
    ],
    id='personal-info-toast',
    header='Patrick Bjornstad',
    is_open=False,
    dismissable=True,
    icon='info',
    style={'position': 'fixed', 'top': 110, 'right': 10, 'background-color': 'rgba(255,255,255,1)'}
)

results_storage = dcc.Store(id='results-storage', data=None)

graph_layout_names = go.Layout(
        margin=dict(l=50, r=50, t=80, b=50),
        title='Distribution of Generated Names (Up to Top 10)',
        xaxis=dict(title='Name'),
        yaxis=dict(title='Prob'),
        template='plotly_white'
)

graph_layout_letters = go.Layout(
        margin=dict(l=50, r=50, t=80, b=50),
        title='Distribution of Generated Letters (not incl. Seed)',
        xaxis=dict(title='Letter'),
        yaxis=dict(title='Prob'),
        template='plotly_white'
)

graph_names_emptyfig = go.Figure(
    data=[],
    layout= graph_layout_names
)

graph_letters_emptyfig = go.Figure(
    data=[],
    layout= graph_layout_letters
)

body = dbc.Container(
    [

        # Model inputs section
        dbc.Row(
            [
                dbc.Col(
                    html.Div(
                        'Generate', 
                        className='fs-2',
                    ), 
                    width='auto'
                ),
                dbc.Col(
                    dbc.Input(
                        id='name-num-input',
                        type='number',
                        value=10,
                        class_name='fs-4',
                        style={'width': '90px'},
                        min=10,
                        max=100
                    ),
                    width='auto',
                    class_name='ps-3 pe-3'
                ),
                dbc.Col(
                    html.Div(
                        'prescription drug brand names of', 
                        className='fs-2',
                    ), 
                    width='auto'
                ),
                dbc.Col(
                    dbc.Select(
                        id='name-length-select',
                        options=[{'label': i, 'value': i} for i in range(4, 17)],
                        class_name='fs-5'
                    ),
                    width='auto',
                    class_name='ps-3 pe-3'
                ),
                dbc.Col(
                    html.Div(
                        'letters that start with', 
                        className='fs-2',
                    ), 
                    width='auto'
                ),
                dbc.Col(
                    dbc.Input(
                        id='name-seed-input',
                        placeholder='<seed string>',
                        type='text',
                        class_name='fs-4',
                        style={'width': '178px'}
                    ),
                    width='auto',
                    class_name='ps-3 pe-3'
                ),
                dbc.Col(
                    dcc.Loading(dbc.Button(
                        'Generate',
                        id='generate-button',
                        class_name='fs-4',
                        disabled=True
                    )),
                    width='auto'
                )
            ],
            class_name='g-0',
            align='center',
            justify='center'
        ),

        # Input Alerts Section
        dbc.Alert(
            'bitchesss',
            id='inputs-alert',
            color='warning',
            class_name='w-50 ms-auto me-auto mt-3'
        ),

        # Divider
        html.Div(className='border border-bottom ms-5 me-5 mt-4'),

        # Results Section
        html.Div(
            [
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                html.Div(
                                    '10.',
                                    id='name-viewer-1',
                                    className='h1 fs-3 text-center text-muted'
                                ),
                                html.Div(
                                    '1.',
                                    id='name-viewer-2',
                                    className='h1 fs-1 text-center'
                                ),
                                html.Div(
                                    '2.',
                                    id='name-viewer-3',
                                    className='h1 fs-3 text-center mb-3 text-muted'
                                ),
                                dbc.Pagination(
                                    id='name-index-select',
                                    max_value=10,
                                    fully_expanded=False,
                                    first_last=True,
                                    previous_next=True,
                                )
                            ], 
                            width='auto'
                        ),
                        dbc.Col(
                            [
                                dbc.ListGroup(
                                    [
                                        dbc.ListGroupItem(
                                            'This generation run produced __ unique names (proportion of unique names: __%)', 
                                            class_name='fs-6',
                                            id='unique-info'
                                        ),
                                        dbc.ListGroupItem(
                                            'The theoretical most likely name for this combination of inputs is __________ (probability of being generated: __%)', 
                                            class_name='fs-6',
                                            id='likely-info'
                                        ),
                                        dbc.ListGroupItem(
                                            'The graphs below showcase the actual distribution of results for this run, from both the letter level and the name level:', 
                                            class_name='fs-6'
                                        )
                                    ],
                                    flush=True
                                )
                            ],
                            width=5
                        )
                    ],
                    justify='center',
                    class_name='mt-3'
                ),
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                dbc.Tabs(
                                    [
                                        dbc.Tab(
                                            dcc.Graph(id='name-graph', figure=graph_names_emptyfig),
                                            label='Name Distribution',
                                            tab_class_name='ms-auto'
                                        ),
                                        dbc.Tab(
                                            dcc.Graph(id='letter-graph', figure=graph_letters_emptyfig),
                                            label='Letter Distribution'
                                        )
                                    ]
                                )
                            ],
                            width=8
                        )
                    ],
                    justify='center',
                    class_name='mt-3'
                )
            ]
        )
    ],
    fluid=True,
    class_name='mt-5'
)

footer = html.Div(
    [
        dbc.Row(
            [
                dbc.Col(
                    html.Img(src='/static/images/logo_web_dark.png', height='30px', className='me-2'),
                    width='auto'
                ),
                dbc.Col(
                    html.Div('Site Version: 1.0.0 | Last Update: 10/9/22'),
                    width='auto'
                )
            ],
            justify='center',
            align='center',
            class_name='g-0'
        ),
        html.Div('All web app and underlying model development by Patrick Bjornstad', className='text-center'),
        html.Div(
            [
                'Questions or comments? ',
                html.A('Contact', href='mailto:patchbjornstad@gmail.com')
            ],
            className='text-center'
        )
    ],
    className='border-top pt-3 pb-3 mt-5'
)

layout = html.Div(
    [
        # Main content: navbar, body, footer
        navbar,
        body,
        footer,

        # Extras - popups, hidden storage components, etc
        personal_info,
        results_storage
    ]
)
