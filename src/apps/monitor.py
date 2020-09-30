import dash
import dash_core_components as dcc
import dash_html_components as html

from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate

from apps.message import MessageQueue

queue = MessageQueue()


class Monitor:
    def __init__(self, app):
        self.name = 'monitor'
        self.app = app

    def get_id(self, str):
        return f'id_{self.name}_{str}'

    def showFloorNumber(self, number, action='STOP'):
        return dbc.Button(
            [
                html.Span(
                    f"{action}",
                    id="floor-number-action"
                ),
                dbc.Badge(
                    f"{number}",
                    id="floor-number-badge",
                    color="light",
                    className="ml-2"
                ),
            ],
            id='floor-number-button',
            # color="primary",
            className="mr-1",
            size="sm",
            style={'width': '100%', 'align': 'center'}
        )

    def display_elevator(self):
        div = html.Div([
            html.H3("Elevator Monitor", style={'textAlign': 'center'}),
            html.Div(id='floor-number',
                     children=[self.showFloorNumber(0)]
                     ),
            html.Div(id="closedoor-live-image",
                     children=[
                         html.Img(id='closedoor-image',
                                  src='/assets/elevator-close.png')
                     ],
                     style={'align': 'center'},
                     hidden=False,
                     ),
            html.Div(id="opendoor-live-image",
                     children=[
                         html.Img(id='opendoor-image',
                                  src='/assets/elevator-open.png'),
                     ],
                     style={'align': 'center'},
                     hidden=True,
                     ),
            html.Div(id='live-update-text'),
        ],
            style={'align': 'center'},
            id='elevator'
        )

        return div

    def layout(self):
        return dbc.Container(children=[
            html.Br(),
            self.display_elevator(),
            html.Div(id=self.get_id('display_button'), className="ml-2"),
            html.Div(
                children=[dcc.Interval(
                    id='interval-component',
                    interval=200,  # in milliseconds
                    n_intervals=0
                )]
            )
        ])

    def callbacks(self):

        @self.app.callback(
            [
                Output('closedoor-live-image', 'hidden'),
                Output('opendoor-live-image', 'hidden'),
                Output('floor-number-badge', 'children'),
                Output('floor-number-action', 'children')
            ],
            [Input('interval-component', 'n_intervals')]
        )
        def update_elevator_status(n):
            data = queue.get_status()
            door_open = False

            if data:
                if data['action'] == 'OPEN_DOOR':
                    door_open = True
                else:
                    door_open = False
                # status_str = json.dumps(data)

                return door_open, not door_open, data['floor'], data['action']
            else:
                raise PreventUpdate
