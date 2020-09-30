import dash
import dash_bootstrap_components as dbc

from apps.monitor import Monitor
from apps.controller import Controller
from apps.navbar import navbar

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=[
                dbc.themes.BOOTSTRAP, 'assets/app.css'])


def start():
    monitor = Monitor(app)
    controller = Controller(app)

    monitor.callbacks()
    controller.callbacks()

    app.layout = dbc.Container(
        [
            navbar,
            dbc.Row(
                [
                    dbc.Col(monitor.layout(), id="id-left-panel", width=6),
                    dbc.Col(controller.layout(), id="id-right-panel", width=6),
                ]
            )
        ],
        fluid=True,
        style={"padding": 0}
    )

    app.run_server(debug=False, host='0.0.0.0')


if __name__ == "__main__":
    start()
