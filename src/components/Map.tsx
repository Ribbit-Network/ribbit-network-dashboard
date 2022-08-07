import React, {useEffect} from "react";
import {Box} from "@mui/material";
import core from "../core/core";

export function MyMapComponent() {
  const ref = React.useRef<HTMLDivElement>(null);
  const [map, setMap] = React.useState<google.maps.Map>();
  const [heatmap, setHeatmap] =
      React.useState<google.maps.visualization.HeatmapLayer>();
  const [heatmapLayerRows, setHeatmapLayerRows] = React.useState<any[]>([]);

  useEffect(() => {
    const mapQuery =
        'from(bucket:"co2")' +
        "|> range(start:-30d)" +
        '|> filter(fn: (r) => r._field == "co2" or r._field == "lat" or r._field == "lon")' +
        "|> last()" +
        '|> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")' +
        "|> filter(fn: (r) => r.lat != 0 and r.lon != 0)" +
        '|> keep(columns: ["_time", "host", "lat", "lon", "co2"])';

    const mapInstance = new window.google.maps.Map(ref.current!, {
      zoom: 3,
      center: { lat: 37.775, lng: -122.434 },
      mapTypeId: "satellite",
    });
    setMap(mapInstance);

    core.influxDB.queryRows(mapQuery, {
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

        const point = new google.maps.LatLng(row.lat, row.lon);

        setHeatmapLayerRows((prev) => [...prev, point]);

        const infowindow = new google.maps.InfoWindow({
          content: `
        <div>
              <Typography><strong>${row.co2.toFixed(
                0
              )}</strong> kg CO2 emitted</Typography>
              <br/>
              <Typography>${new Date(row._time).toDateString()}</Typography>
            </div>`,
        });

        const marker = new google.maps.Marker({
          position: point,
          map: mapInstance,
          title: "",
          icon: " ",
        });

        marker.addListener("click", () => {
          infowindow.open({
            anchor: marker,
            map: mapInstance,
            shouldFocus: false,
          });
        });
      },
      error: console.error,
      complete: () => {
        console.log("creating a heatmap");
        const heatmap = new window.google.maps.visualization.HeatmapLayer({
          data: heatmapLayerRows,
          map: mapInstance,
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
