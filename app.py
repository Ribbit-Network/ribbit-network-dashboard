from dash.dependencies import Output, Input
from influxdb_client import InfluxDBClient, Point, Dialect

import csv
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import os
import plotly.express as px
import plotly.graph_objects as go

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

# Dash App
app = dash.Dash(__name__, title='GHG Cloud', external_stylesheets=external_stylesheets)
server = app.server

# Connect to InfluxDB
client = InfluxDBClient.from_config_file("influx_config.ini")
query_api = client.query_api()

def get_influxdb_data(duration):
    ## Query data as pandas dataframe
    df = query_api.query_data_frame('from(bucket:"co2")'
                                    f'|> range(start: -{duration})'
                                    '|> filter(fn: (r) => r.host == "6cb1b8e43a19bdb3950a118a36af3452")'
                                    '|> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")'
                                    '|> keep(columns: ["co2", "temperature", "humidity", "lat", "lon", "alt", "_time"])')
    return df.drop(['result', 'table'], axis=1)

def serve_layout():
    #Define this function to query new data on page load
    return html.Div([
        html.Div(id='onload', hidden=True),

        html.H1("Ribbit Network"),
        html.A(html.Button('Learn More!'), href='https://ribbitnetwork.org/'),

        html.H3('Sensor Map'),
        dcc.Graph(
            id='co2_globe',
            figure=globe_fig,
            style={
            "width": "100%",
            'display': 'inline-block'
        }),

        html.H3('Sensor Data'),
        dcc.Dropdown(id='duration', value='1h', options=[
            {'label': '10 minutes', 'value': '10m'},
            {'label': '30 minutes', 'value': '30m'},
            {'label': '1 hour',     'value': '1h'},
            {'label': '1 day',      'value': '24h'},
        ]),
        dcc.Graph(id='co2_graph', figure=co2_fig),
        dcc.Interval(id='interval', interval=60*1000, n_intervals=0),
        html.Div(id='timezone', hidden=True),
        html.Div([html.Button('Export as CSV', id='export'), dcc.Download(id='download')]),
    ])

## Query data as pandas dataframe
co2_fig = px.line(get_influxdb_data('1h'), x="_time", y="co2", title="Co2 PPM")

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
    Input('onload', 'children'),
)

# Update CO2 graph
@app.callback(
    Output('co2_graph', 'figure'),
    [
        Input('timezone', 'children'),
        Input('duration', 'value'),
        Input('interval', 'n_intervals'),
    ],
)
def update_graph(timezone, duration, n_intervals):
    df = get_influxdb_data(duration)
    df['_time'] = df['_time'].dt.tz_convert(timezone)
    return px.line(df, x="_time", y="co2", title="Co2 PPM")

# Export data as CSV
@app.callback(Output('download', 'data'), [Input('export', 'n_clicks'), Input('duration', 'value')])
def export_data(n_clicks, duration):
    if n_clicks == None:
        return
    df = get_influxdb_data(duration)
    df.columns = ['Timestamp', 'Altitude', 'CO2', 'Humidity', 'Latitude', 'Longitude', 'Temperature']
    return dcc.send_data_frame(df.to_csv, index=False, filename='data.csv')

if __name__ == '__main__':
    app.run_server(debug=True)
