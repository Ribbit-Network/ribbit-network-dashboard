import React, { useEffect, useRef } from "react";
import { Box } from "@mui/material";
import { InfluxDB } from "@influxdata/influxdb-client-browser";

export function MyMapComponent() {
  const ref = React.useRef<HTMLDivElement>(null);
  const [map, setMap] = React.useState<google.maps.Map>();
  const [heatmapLayerRows, setHeatmapLayerRows] = React.useState<any[]>([]);

  useEffect(() => {
    const influxDB = new InfluxDB({
      url: "https://us-west-2-1.aws.cloud2.influxdata.com",
      token:
        "wQdQ6Xeh0jvjy_oCHnqYtux9qNaoEdt57B4mQiFz6gV-itMn2WnuLnolwAVfFuE6c6dR27m6bUxdqSxb9f5Rog==",
    }).getQueryApi("keenan.johnson@gmail.com");

    const mapQuery =
      'from(bucket:"co2")' +
      "|> range(start:-30d)" +
      '|> filter(fn: (r) => r._field == "co2" or r._field == "lat" or r._field == "lon")' +
      "|> last()" +
      '|> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")' +
      "|> filter(fn: (r) => r.lat != 0 and r.lon != 0)" +
      '|> keep(columns: ["_time", "host", "lat", "lon", "co2"])';

    const map = new window.google.maps.Map(ref.current!, {
      zoom: 3,
      center: { lat: 37.775, lng: -122.434 },
      mapTypeId: "satellite",
    });
    setMap(map);

    influxDB.queryRows(mapQuery, {
      next: (raw: any, tableMeta: any) => {
        const row: {
          co2: number;
          host: string;
          lat: number;
          lon: number;
          result: string;
          table: number;
          _time: string;
        } = tableMeta.toObject(raw);

        setHeatmapLayerRows((prev) => [
          ...prev,
          new google.maps.LatLng(row.lat, row.lon),
        ]);
      },
      error: console.error,
      complete: () => {
        console.log("creating a heatmap now...");
        new window.google.maps.visualization.HeatmapLayer({
          data: heatmapLayerRows,
          map,
        });
      },
    });
  }, []);

  return (
    <Box
      sx={{
        height: "100vh",
        width: "100vw",
      }}
      ref={ref}
      id="map"
    />
  );
}
