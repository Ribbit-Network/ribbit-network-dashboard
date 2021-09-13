from influxdb_client import InfluxDBClient

# Connect to InfluxDB
client = InfluxDBClient.from_config_file('influx_config.ini')
query_api = client.query_api()

def get_sensor_ids():
    df = query_api.query_data_frame('from(bucket:"co2") '
                                    '|> range(start:-15m) '
                                    '|> limit(n:1) '
                                    '|> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value") '
                                    '|> keep(columns: ["host"])')
    return df['host']

def get_map_data():
    print('Fetching map data')
    # Only get the latest point for displaying on the map
    return query_api.query_data_frame('from(bucket:"co2") '
                                        '|> range(start:-15m) '
                                        '|> limit(n:1) '
                                        '|> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value") '
                                        '|> keep(columns: ["co2", "lat", "lon"])')

def get_sensor_data(host, duration):
    df = query_api.query_data_frame('from(bucket:"co2")'
                                    f'|> range(start: -{duration})'
                                    f'|> filter(fn: (r) => r.host == "{host}")'
                                    '|> aggregateWindow(every: 1m, fn: mean, createEmpty: false)'
                                    '|> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")'
                                    '|> keep(columns: ["co2", "temperature", "humidity", "lat", "lon", "alt", "_time", "baro_pressure"])')

    return df.drop(['result', 'table'], axis=1)

