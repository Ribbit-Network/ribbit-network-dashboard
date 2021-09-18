import csv
import time
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import db
import numpy as np
import os
import plotly.express as px
import plotly.graph_objects as go

from dash.dependencies import Output, Input

TITLE = 'Ribbit Network'
REFRESH_MS = 60 * 1000

# Dash App
app = dash.Dash(__name__, title=TITLE)
server = app.server

def serve_layout():
    sensor_ids = db.get_sensor_ids()

    return html.Div([
        html.Div(id='onload', hidden=True),
        dcc.Interval(id='interval', interval=REFRESH_MS, n_intervals=0),

        html.Div([
            html.Img(src='assets/frog.svg'),
            html.H1(TITLE),
            html.A(html.H3('Learn More'), href='https://ribbitnetwork.org/', style={'margin-left': 'auto', 'text-decoration': 'none', 'color': 'black'}),
        ], id='nav'),

        html.Div([
            dcc.Graph(id='map'),
            dcc.Loading(id='loading', children=[html.Div(id='loading-output')]),
        ], id='map-container'),

        html.Div([
            dcc.Dropdown(id='host', clearable=False, searchable=False, value=sensor_ids[0], options=[
                {'label': 'Sensor '+str(i+1), 'value': sensor_id} for i, sensor_id in sensor_ids.iteritems()
            ]),
            dcc.Dropdown(id='duration', clearable=False, searchable=False, value='24h', options=[
                {'label': '10 minutes', 'value': '10m'},
                {'label': '30 minutes', 'value': '30m'},
                {'label': '1 hour',     'value': '1h'},
                {'label': '1 day',      'value': '24h'},
                {'label': '7 days',     'value': '7d'},
                {'label': '30 days',    'value': '30d'},
            ]),
            html.Div([
                html.Button(html.Div([
                    html.Img(src='assets/download.svg'),
                    'Export as CSV',
                ]), id='export'),
                dcc.Download(id='download'),
            ]),
        ], id='controls'),

        html.Div([
            dcc.Graph(id='co2_graph'),
            dcc.Graph(id='temp_graph'),
            dcc.Graph(id='baro_graph'),
            dcc.Graph(id='humidity_graph'),
            html.Div(id='timezone', hidden=True),
            dcc.Loading(id='loading-graphs-2', children=[html.Div(id='output-1')]),
            # dcc.Loading(id='loading-graphs', children=[html.Div(id='loading-output-graphs')])
        ], id='graphs'),
    ])

def get_plotting_zoom_level_and_center_coordinates_from_lonlat_tuples(longitudes=None, latitudes=None):
    """Function documentation:\n
    Basic framework adopted from Krichardson under the following thread:
    https://community.plotly.com/t/dynamic-zoom-for-mapbox/32658/7

    # NOTE:
    # THIS IS A TEMPORARY SOLUTION UNTIL THE DASH TEAM IMPLEMENTS DYNAMIC ZOOM
    # in their plotly-functions associated with mapbox, such as go.Densitymapbox() etc.

    Returns the appropriate zoom-level for these plotly-mapbox-graphics along with
    the center coordinates of all provided coordinate tuples.
    """

    # Check whether both latitudes and longitudes have been passed,
    # or if the list lengths don't match
    if ((latitudes is None or longitudes is None)
            or (len(latitudes) != len(longitudes))):
        # Otherwise, return the default values of 0 zoom and the coordinate origin as center point
        return 0, (0, 0)

    # Get the boundary-box 
    b_box = {} 
    b_box['height'] = latitudes.max()-latitudes.min()
    b_box['width'] = longitudes.max()-longitudes.min()
    b_box['center_lat'] = np.mean(latitudes)
    b_box['center_lon'] = np.mean(longitudes)

    # get the area of the bounding box in order to calculate a zoom-level
    area = b_box['height'] * b_box['width']

    # * 1D-linear interpolation with numpy:
    # - Pass the area as the only x-value and not as a list, in order to return a scalar as well
    # - The x-points "xp" should be in parts in comparable order of magnitude of the given area
    # - The zoom-levels are adapted to the areas, i.e. start with the smallest area possible of 0
    # which leads to the highest possible zoom value 20, and so forth decreasing with increasing areas
    # as these variables are anti-proportional
    zoom = np.interp(x=area,
                     xp=[0,  5**-10, 4**-10, 3**-10, 2**-10, 1**-10, 1**-5],
                     fp=[20, 15,     14,     13,     11,     6,      4])

    # Finally, return the zoom level and the associated boundary-box center coordinates
    return zoom, b_box['center_lat'], b_box['center_lon']

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

# Update the Map
@app.callback(
    Output('map', 'figure'),
    Output('loading-output', 'children'),
    [
        Input('onload', 'children'),
        Input('interval', 'n_intervals'),
    ],
)
def update_map(children, n_intervals):
    df = db.get_map_data()
    zoom, b_box_lat, b_box_lon = get_plotting_zoom_level_and_center_coordinates_from_lonlat_tuples(longitudes=df['lon'], latitudes=df['lat'])

    map_fig = go.Figure(data=go.Scattermapbox(
        lon=df['lon'],
        lat=df['lat'],
        text='CO₂: '+df['co2'].round(decimals=2).astype('str')+' PPM',
        mode='markers',
        marker=dict(color=df['co2'], size=16, showscale=True, cmin=300, cmax=600),
        # Preserve the Map state accross updates (zoom level, selections, etc)
        # https://community.plotly.com/t/preserving-ui-state-like-zoom-in-dcc-graph-with-uirevision-with-dash/15793
        uirevision='dataset'
    ))

    map_fig.update_layout(mapbox_style='carto-positron',
                          margin={'r': 0, 't': 0, 'l': 0, 'b': 0},
                          mapbox_zoom=zoom,
                          mapbox_center_lat=b_box_lat,
                          mapbox_center_lon=b_box_lon)

    return map_fig, True

# Update Data Plots
@app.callback(
    Output('co2_graph', 'figure'),
    Output('temp_graph', 'figure'),
    Output('baro_graph', 'figure'),
    Output('humidity_graph', 'figure'),
    # Output('loading-output-graphs', 'children'),
    [
        Input('timezone', 'children'),
        Input('duration', 'value'),
        Input('host', 'value'),
        Input('interval', 'n_intervals'),
    ],
)
def update_graphs(timezone, duration, host, n_intervals):
    df = db.get_sensor_data(host, duration)
    df.rename(columns = {'_time':'Time', 'co2':'CO₂ (PPM)', 'humidity':'Humidity (%)', 'lat':'Latitude', 
                         'lon':'Longitude','alt':'Altitude (m)','temperature':'Temperature (°C)', 'baro_pressure':'Barometric Pressure (mBar)'}, inplace = True)
    df['Time'] = df['Time'].dt.tz_convert(timezone)
    co2_line = px.line(df, x='Time', y='CO₂ (PPM)', color_discrete_sequence=['black'],
                       template='plotly_white', render_mode='svg', hover_data = {'CO₂ (PPM)':':.2f'})
    temp_line = px.line(df, x='Time', y='Temperature (°C)', color_discrete_sequence=['black'], 
                        template='plotly_white', render_mode='svg', hover_data = {'Temperature (°C)':':.2f'})
    baro_line = px.line(df, x='Time', y='Barometric Pressure (mBar)', color_discrete_sequence=['black'],
                        template='plotly_white', render_mode='svg', hover_data = {'Barometric Pressure (mBar)':':.2f'})
    humidity_line = px.line(df, x='Time', y='Humidity (%)', color_discrete_sequence=['black'],
                            template='plotly_white', render_mode='svg', hover_data = {'Humidity (%)':':.2f'})
    return co2_line, temp_line, baro_line, humidity_line

# Export data as CSV
@app.callback(
    Output('download', 'data'),
    [
        Input('export', 'n_clicks'),
        Input('duration', 'value'),
        Input('host', 'value'),
    ],
)
def export_data(n_clicks, duration, host):
    if n_clicks == None:
        return
    df = db.get_sensor_data(host, duration)
    df.columns = ['Timestamp', 'Altitude (m)', 'CO₂ (PPM)', 'Humidity (%)', 'Latitude', 'Longitude', 'Barometric Pressure (mBar)', 'Temperature (°C)']
    return dcc.send_data_frame(df.to_csv, index=False, filename='data.csv')


if __name__ == '__main__':
    app.run_server(debug=True)
