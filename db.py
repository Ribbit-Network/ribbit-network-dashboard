import os
import pandas as pd
import numpy as np
from datetime import datetime, timezone
from cachetools import cached, TTLCache

import influxdb_client

INFLUXDB_BUCKET = "frog_fleet"
INFLUXDB_ORG = "Ribbit Network"
INFLUXDB_URL = "https://us-west-2-1.aws.cloud2.influxdata.com/"
INFLUXDB_TOKEN = os.environ['INFLUXDB_TOKEN']

client = influxdb_client.InfluxDBClient(url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG)
query_api = client.query_api()


@cached(cache=TTLCache(maxsize=1, ttl=60))
def get_map_data() -> pd.DataFrame:
    df = query_api.query_data_frame(f'from(bucket:"{INFLUXDB_BUCKET}")'
                                    '|> range(start:-30d)'
                                    '|> filter(fn: (r) => r._field == "co2" or r._field == "lat" or r._field == "lon")'
                                    '|> last()'
                                    '|> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")'
                                    '|> filter(fn: (r) => r.lat != 0 and r.lon != 0)'
                                    '|> keep(columns: ["_time", "host", "lat", "lon", "co2"])')
    if type(df) is list:
        return pd.concat(df)
    if type(df) is pd.DataFrame:
        return df


# `100` chosen arbitrarily, tweak with extreme prejudice
@cached(cache=TTLCache(maxsize=100, ttl=60))
def get_sensor_data(host: str, duration: str, frequency: str) -> pd.DataFrame:
    df = query_api.query_data_frame(f'from(bucket:"{INFLUXDB_BUCKET}")'
                                    f'|> range(start: -{duration})'
                                    f'|> filter(fn: (r) => r.host == "{host}")'
                                    '|> aggregateWindow(every: 1m, fn: mean, createEmpty: false)'
                                    '|> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")'
                                    '|> keep(columns: ["co2", "temperature", "humidity", "lat", "lon", "_time", "baro_pressure"])')
    if df.empty:
        return df
    df.drop(['result', 'table'], axis=1, inplace=True)
    if frequency in ['5min', '10min', '15min', '30min', '1h']:
        df.set_index('_time', inplace=True)
        df = df.resample(frequency).mean().reset_index()
    return df


def print_sensor_info():

    influx_query = f'from(bucket:"{INFLUXDB_BUCKET}") \
    |> range(start:-30d) \
    |> filter(fn:(r) => r._measurement == "ghg_point") \
    |> filter(fn:(r) => r._field == "co2") \
    |> last() \
    |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")'

    result = query_api.query_data_frame(org=INFLUXDB_ORG, query=influx_query)[['_time', 'host', 'co2']]
    result["days_since_last_read"] = ((datetime.now(timezone.utc) - result["_time"]).dt.total_seconds() / (60 * 60 * 24)).astype(int)
    result["version"] = np.where(result['host'].str.endswith('_golioth_esp32s3'), 'v4', 'v3')
    result["co2"] = result["co2"].astype(int)
    result = result.sort_values(by=['days_since_last_read'], ascending=[True])[['host', 'co2', 'version', 'days_since_last_read']]
    print(result)

# python3 ./db.py
if __name__ == '__main__':
    # https://stackoverflow.com/questions/52805115/certificate-verify-failed-unable-to-get-local-issuer-certificate
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', 1000)

    print_sensor_info()
