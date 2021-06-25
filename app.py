import os

import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Output, Input
import plotly.express as px
import plotly.graph_objects as go

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
            id='co2_globe',
            figure=globe_fig,
            style={
            "width": "100%"
        }),
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

# Build Map
map_df = get_influxdb_data()
globe_fig =go.Figure(data=go.Scattergeo(
    lon = map_df['lon'],
    lat = map_df['lat'],
    text = map_df['co2'],
    mode = 'markers'
    ))
#globe_fig.update_geos(projection_type="orthographic")
globe_fig.update_layout(height=500, margin={"r":0,"t":0,"l":0,"b":0})
globe_fig.update_geos(lataxis_showgrid=True, lonaxis_showgrid=True)

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
