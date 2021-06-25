import os

import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Output, Input
import plotly.express as px

from influxdb_client import InfluxDBClient, Point, Dialect

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

# Dash App
app = dash.Dash(__name__, title='GHG Cloud', external_stylesheets=external_stylesheets)
server = app.server

# Connect to InfluxDB
client = InfluxDBClient.from_config_file("influx_config.ini")
query_api = client.query_api()


def get_influxdb_data():
    ## Query data as pandas dataframe
    data_frame = query_api.query_data_frame('from(bucket:"co2") '
                                            '|> range(start: -60m) '
                                            '|> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value") '
                                            '|> keep(columns: ["co2", "temperature", "humidity", "lat", "lon", "alt", "_time"])')

    return data_frame

def serve_layout():
    #Define this function to query new data on page load
    return html.Div([
        dcc.Graph(
            id='co2_graph',
            figure=fig
        ),
        dcc.Interval(
            id='interval-component',
            interval=60*1000, # in milliseconds
            n_intervals=0
        )
    ])

## Query data as pandas dataframe
fig = px.line(get_influxdb_data(), x="_time", y="co2", title="Co2 PPM")


app.layout = serve_layout

# update temperature graph
@app.callback(Output('co2_graph', 'figure'),
              [Input('interval-component', 'n_intervals')
              ])
def update_graph(n):
    ## Query data as pandas dataframe
    fig = px.line(get_influxdb_data(), x="_time", y="co2", title="Co2 PPM")
    return fig

if __name__ == '__main__':
    app.run_server(debug=True)
