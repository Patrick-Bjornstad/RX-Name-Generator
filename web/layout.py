from turtle import width
from dash import html, dcc
import dash_bootstrap_components as dbc

navbar = dbc.Navbar(
    dbc.Container(
        [
            dbc.Row(
                [
                    dbc.Col(html.Img(src='/static/images/logo_site.svg', height='60px')),
                    dbc.Col(dbc.NavbarBrand('LSTM Prescription Drug Name Generator', class_name='h1 text-light ps-2 fs-3 fw-bolder')),
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
                    dbc.Button(
                        'Generate',
                        id='generate-button',
                        class_name='fs-4',
                        disabled=True
                    ),
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
    ],
    fluid=True,
    class_name='mt-5'
)

layout = html.Div(
    [
        # Main content: navbar, body, footer
        navbar,
        body,

        # Extras - popups, hidden storage components, etc
        personal_info
    ]
)
