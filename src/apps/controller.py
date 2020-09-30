import json
import dash
import dash_core_components as dcc
import dash_html_components as html

from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate
from apps.message import MessageQueue

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=[
                dbc.themes.BOOTSTRAP, 'assets/app.css'])

server = app.server

message_queue = MessageQueue()


class Controller:
    def __init__(self, app):
        self.name = 'controller'
        self.app = app

    def get_id(self, str):
        return f'id_{self.name}_{str}'

    def layout(self):
        return dbc.Container(children=[
            html.Br(),
            html.H3("Elevator Controller", style={'textAlign': 'center'}),
            dbc.Alert("",
                      id=self.get_id('command'),
                      color="primary",
                      style={"width": "280px",
                             'margin': 'auto'},
                      duration=5000),

            # html.Br(),
            self.create_buttons(),
            dbc.Container(id=self.get_id('display_button'), className="ml-2"),
        ],
            style={"margin": "auto", }
        )

    def callbacks(self):
        @self.app.callback(
            [
                Output(self.get_id('command'), 'is_open'),
                Output(self.get_id('command'), 'children')
            ],
            self.input_buttons()
        )
        def buttons_click(*args):
            ctx = dash.callback_context

            button_id = ctx.triggered[0]['prop_id'].split('.')[0]

            print(f'button_id={button_id}')

            if not button_id.strip():
                return False, ''

            values = button_id.split('_')

            command = values[2].upper()
            floor_number = int(values[3])

            message_queue.send_command(command, floor_number)

            return True, f'Send command: {command} {floor_number}'

    def input_buttons(self):
        input_list = []
        for number in range(7, -2, -1):
            input_list.append(Input(self.get_id(f'stop_{number}'), 'n_clicks'))
            input_list.append(Input(self.get_id(f'up_{number}'), 'n_clicks'))
            input_list.append(Input(self.get_id(f'down_{number}'), 'n_clicks'))

        return input_list

    def create_buttons(self):
        rows = []
        for number in range(7, -2, -1):
            row = dbc.Row([
                dbc.ButtonGroup(
                    [
                        dbc.Button(f"{number}", color="info", className="mr-2"),
                        dbc.Button("STOP", id=self.get_id(f'stop_{number}'), color="success", className="mr-1"),
                        dbc.Button("UP", id=self.get_id(f'up_{number}'), color="success", className="mr-1"),
                        dbc.Button("DOWN", id=self.get_id(f'down_{number}'), color="success", className="mr-1")
                    ],
                    # size="sm",
                    className="mr-1",
                )],
                className="m-2",
                justify='center'
            )

            rows.append(row)

        return dbc.Container(
            rows,
            style={
                "margin": "auto",
                "borderStyle": "solid",
                "border-radius": "5px",
                "maxWidth": "280px",
                "backgroundColor": "#DFDEDC"
            }
        )


def main():
    controller = Controller(app)

    app.layout = controller.layout()
    controller.callbacks()
    app.run_server(debug=True, host='0.0.0.0')


if __name__ == '__main__':
    main()
