import os, time
import pandas as pd
import numpy as np
from datetime import datetime, timezone
from cachetools import cached, TTLCache

import influxdb_client

INFLUXDB_BUCKET = "frog_fleet"
INFLUXDB_ORG = "Ribbit Network"
INFLUXDB_URL = "https://us-west-2-1.aws.cloud2.influxdata.com/"
INFLUXDB_TOKEN = os.environ['INFLUXDB_TOKEN']
#INFLUXDB_TOKEN = os.environ['INFLUXDB_ALL_ACCESS_TOKEN']

client = influxdb_client.InfluxDBClient(url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG)
query_api = client.query_api()

INFLUXDB_TEST_BUCKET = None
INFLUXDB_TEST_TOKEN = None
test_client = None
test_query_api = None

@cached(cache=TTLCache(maxsize=1, ttl=60))
def get_map_data() -> pd.DataFrame:
    return get_map_data_from_bucket(INFLUXDB_BUCKET)

def get_test_map_data() -> pd.DataFrame:
    return get_map_data_from_bucket(INFLUXDB_TEST_BUCKET)

def get_map_data_from_bucket(bucket: str) -> pd.DataFrame:
    df = test_query_api.query_data_frame(f'from(bucket:"{bucket}")'
                                    '|> range(start:-30d)'
                                    '|> filter(fn: (r) => r._field == "co2" or r._field == "lat" or r._field == "lon")'
                                    '|> filter(fn: (r) => r.lat != 0 and r.lon != 0)'
                                    '|> last()'
                                    '|> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")'
                                    '|> map(fn: (r) => ({r with co2: float(v: r.co2)}))'
                                    '|> keep(columns: ["_time", "host", "lat", "lon", "co2"])')
    return concat_result(df)

# `100` chosen arbitrarily, tweak with extreme prejudice
@cached(cache=TTLCache(maxsize=100, ttl=60))
def get_sensor_data(host: str, duration: str, frequency: str) -> pd.DataFrame:
    return get_sensor_data_from_bucket(host, duration, frequency, INFLUXDB_BUCKET)

def get_test_sensor_data(host: str, duration: str, frequency: str) -> pd.DataFrame:
    return get_sensor_data_from_bucket(host, duration, frequency, INFLUXDB_TEST_BUCKET)


def get_sensor_data_from_bucket(host: str, duration: str, frequency: str, bucket: str) -> pd.DataFrame:
    df = test_query_api.query_data_frame(f'from(bucket:"{bucket}")'
                                    f'|> range(start: -{duration})'
                                    f'|> filter(fn: (r) => r.host == "{host}")'
                                    '|> aggregateWindow(every: 1m, fn: mean, createEmpty: false)'
                                    '|> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")'
                                    '|> keep(columns: ["co2", "temperature", "humidity", "lat", "lon", "_time", "baro_pressure"])')
    if df.empty:
        return df
    #print(df.dtypes)
    df.drop(['result', 'table'], axis=1, inplace=True)
    if frequency in ['5min', '10min', '15min', '30min', '1h']:
        df.set_index('_time', inplace=True)
        df = df.resample(frequency).mean().reset_index()

    return df


def print_sensor_info():

    influx_query = f'from(bucket:"{INFLUXDB_BUCKET}") \
    |> range(start:-30d) \
    |> filter(fn:(r) => r._field == "co2") \
    |> last() \
    |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")'

    result = query_api.query_data_frame(org=INFLUXDB_ORG, query=influx_query)
    result = concat_result(result)

    result["days_since_last_read"] = ((datetime.now(timezone.utc) - result["_time"]).dt.total_seconds() / (60 * 60 * 24)).astype(int)
    result["version"] = np.where(result['host'].str.endswith('_golioth_esp32s3'), 'v4', 'v3')
    result["co2"] = result["co2"].astype(int)
    result = result.sort_values(by=['days_since_last_read'], ascending=[True])[['host', 'co2', 'version', 'days_since_last_read']]

    return result

def concat_result(df):
    if type(df) is list:
        # for x in df:
        #     print(x.dtypes)
        #     print(x[['_measurement', 'co2', 'host']])
        return pd.concat(df)
    if type(df) is pd.DataFrame:
        return df

def copy_data(write_api, host):
    df = query_api.query_data_frame(f'from(bucket:"{INFLUXDB_BUCKET}")'
                                    f'|> range(start: -1d)'
                                    f'|> filter(fn: (r) => r.host == "{host}")'
                                    '|> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")')

    if df.shape[0] != 0:
        #print(df)
        #print(df.dtypes)
        df.drop(columns=['result', 'table', '_start', '_stop', '_measurement'], axis=1, inplace=True)
        df.set_index('_time', inplace=True)

        backfill_split(write_api, df)


def write_df(write_api, df):
    #print(df)
    #print(df.dtypes)
    #quit()
    try:
        write_api.write(INFLUXDB_TEST_BUCKET, INFLUXDB_ORG, record=df, data_frame_measurement_name="ghg_reading",
                        data_frame_tag_columns=['host'])
    except TimeoutError:
        print('timeout error - trying again')
        time.sleep(5)
        write_api.write(INFLUXDB_TEST_BUCKET, INFLUXDB_ORG, record=df, data_frame_measurement_name="ghg_reading",
                        data_frame_tag_columns=['host'])


    time.sleep(5)

count = 0
def backfill_split(write_api, df, spacer=''):
    global count
    if df.shape[0] > 10000:
        print(spacer + '  splitting')
        half = df.shape[0] // 2
        df1 = df.iloc[half:, :]
        df2 = df.iloc[:half, :]

        print(spacer + '    ' + str(df1.shape[0]))
        backfill_split(write_api, df1, spacer + '    ')

        print(spacer + '    ' + str(df2.shape[0]))
        backfill_split(write_api, df2, spacer + '    ')
    else:
        count += 1
        if count == 15:
            write_df(write_api, df)
        #print(count)

def backfill():
    import csv
    from pathlib import Path
    from influxdb_client import InfluxDBClient, Point, WritePrecision  # type: ignore
    from influxdb_client.client.write_api import SYNCHRONOUS  # type: ignore

    write_api = test_client.write_api(write_options=SYNCHRONOUS)
    #write_api = client.write_api(write_options=SYNCHRONOUS)

    total_records = 0
    files = Path('RibbitNetworkArchived').rglob('*.csv')

    finished = ['RibbitNetworkArchived/80ab28d8990e634f9ad1b80a9634e009.csv',
                'RibbitNetworkArchived/63b9de5ab679f5d522bda828.csv',
                'RibbitNetworkArchived/3d31d42c0d06fa599a854b7ff1278afe.csv',
                'RibbitNetworkArchived/63cc4fdfc345ce2e0256ac06.csv',
                'RibbitNetworkArchived/63b9decdb679f5d522bda82c.csv',
                'RibbitNetworkArchived/63cf34fef9744313c5f7d1fe.csv',
                'RibbitNetworkArchived/c77005e188667ce0cdd574e3712a22ec.csv',
                'RibbitNetworkArchived/983e22fb7ee6269154186163eeac570f.csv',
                'RibbitNetworkArchived/5cd0a6a9bd06807565805d5ca4f9204c.csv',
                'RibbitNetworkArchived/8d95bea2c96c11a5894a4e25dd59ee67.csv',
                'RibbitNetworkArchived/5abd197daa9cdffdb3d7162d326ad383.csv',
                'RibbitNetworkArchived/63cc5000c345ce2e0256ac0a.csv',
                'RibbitNetworkArchived/63bb52d4d65e350fedc17e19.csv',
                'RibbitNetworkArchived/145595451a3b208f650307bdaff444bc.csv',
                'RibbitNetworkArchived/63c0803b4a40c3355595ba68.csv',
                'RibbitNetworkArchived/63b9deb6b679f5d522bda82a.csv',
                'RibbitNetworkArchived/b3cb78300e0e173b0517b9297923c314.csv',
                'RibbitNetworkArchived/5c782d2a5a9420f717c5b37b93756ff2.csv',
                'RibbitNetworkArchived/03deeb5b8858da8b1fdaa5f30209f8de.csv']
    errored = 'RibbitNetworkArchived/cebbf6da20d60ca032c55706cadadf71.csv'
    for file in files:
        #if str(file) not in finished and str(file) != errored:
        if str(file) == errored:
            df = pd.read_csv(file)
            df['_time'] = pd.to_datetime(df['_time'], format="%Y-%m-%d %H:%M:%S")
            df.rename(columns={"host_id": "host"}, inplace=True)
            df.set_index(['_time'], inplace=True)

            print(str(file) + ' ' + str(df.shape[0]))
            host = str(file).split('/')[1].split('.csv')[0]

            #copy_data(write_api, host)
            backfill_split(write_api, df)

            total_records += df.shape[0]
        else:
            print('skipping')

    print(str(total_records))

def init_test_db():
    global INFLUXDB_TEST_BUCKET, INFLUXDB_TEST_TOKEN, test_client, test_query_api

    INFLUXDB_TEST_BUCKET = "frog_fleet_test"
    INFLUXDB_TEST_TOKEN= os.environ['INFLUXDB_TEST_TOKEN']
    test_client = influxdb_client.InfluxDBClient(url=INFLUXDB_URL, token=INFLUXDB_TEST_TOKEN, org=INFLUXDB_ORG)
    test_query_api = test_client.query_api()

# python3 ./db.py
if __name__ == '__main__':
    # https://stackoverflow.com/questions/52805115/certificate-verify-failed-unable-to-get-local-issuer-certificate
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', 1000)

    init_test_db()

    #df = print_sensor_info()
    #print(df)

    #df = get_test_map_data()
    #print(df)
    #quit()

    #df = get_sensor_data('63b9deb6b679f5d522bda82a_golioth_esp32s3', '30d', '5min')
    #df = get_sensor_data('983e22fb7ee6269154186163eeac570f', '30d', '5min')
    #print(df)

    #backfill()