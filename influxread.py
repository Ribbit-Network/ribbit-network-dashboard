from influxdb_client import InfluxDBClient, Point, Dialect


client = InfluxDBClient.from_config_file("influx_config.ini")

query_api = client.query_api()

## using Table structure
data_frame = query_api.query_data_frame('from(bucket:"co2") '
                                        '|> range(start: -10m) '
                                        '|> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value") '
                                        '|> keep(columns: ["co2", "temperature", "humidity", "lat", "lon", "alt"])')
print(data_frame.to_string())
