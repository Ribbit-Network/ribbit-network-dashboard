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
                                            '|> range(start: -1h) '
                                            '|> filter(fn: (r) => r.host == "6cb1b8e43a19bdb3950a118a36af3452")'
                                            '|> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value") '
                                            '|> keep(columns: ["co2", "temperature", "humidity", "lat", "lon", "alt", "_time"])')

    return data_frame

def serve_layout():
    #Define this function to query new data on page load
    return html.Div([
        html.H1("Ribbit Network"),
        html.A(html.Button('Learn More!'),
            href='https://ribbitnetwork.org/'),
        html.H3('Sensor Map'),
        dcc.Graph(
            id='co2_globe',
            figure=globe_fig,
            style={
            "width": "100%",
            'display': 'inline-block'
        }),
        html.H3('Sensor Data'),
        dcc.Graph(
            id='co2_graph',
            figure=co2_fig),
        dcc.Interval(
            id='interval-component',
            interval=60*1000, # in milliseconds
            n_intervals=0),
        html.Div(id='timezone', hidden=True)
    ])

## Query data as pandas dataframe
co2_fig = px.line(get_influxdb_data(), x="_time", y="co2", title="Co2 PPM")

# Only get the latest point for displaying on the map
map_df = query_api.query_data_frame('from(bucket:"co2") '
                                    '|> range(start:-15m) '
                                    '|> limit(n:1) '
                                    '|> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value") '
                                    '|> keep(columns: ["co2","lat", "lon"])')

globe_fig =go.Figure(data=go.Scattergeo(
    lon = map_df['lon'],
    lat = map_df['lat'],
    text = map_df['co2'],
    mode = 'markers',
    marker=dict(color="crimson", size=25,)
    ))
globe_fig.update_geos(
    projection_type="orthographic",
    landcolor="white",
    oceancolor="MidnightBlue",
    showocean=True,
    lakecolor="LightBlue",
    lataxis_showgrid=True,
    lonaxis_showgrid=True,
    projection_rotation=dict(lon=-122, lat=25, roll=0)
)
globe_fig.update_layout(height=500, margin={"r":0,"t":0,"l":0,"b":0})

app.layout = serve_layout

# Get browser timezone
app.clientside_callback(
    '''
    function(n_intervals) {
        return Intl.DateTimeFormat().resolvedOptions().timeZone
    }
    ''',
    Output('timezone', 'children'),
    Input('interval-component', 'n_intervals')
)

# Update CO2 graph
@app.callback(Output('co2_graph', 'figure'), Input('timezone', 'children'))
def update_graph(timezone):
    df = get_influxdb_data()
    df['_time'] = df['_time'].dt.tz_convert(timezone)
    return px.line(df, x="_time", y="co2", title="Co2 PPM")

if __name__ == '__main__':
    app.run_server(debug=True)
