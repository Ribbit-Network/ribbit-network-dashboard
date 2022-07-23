window.ribbit = Object.assign({}, window.ribbit, {
  map: {
    pointToLayer: function (feature, latlng, context) {
      const { min, max, colorscale, circleOptions, colorProp, selectedSensor } =
        context.props.hideout;
      const csc = chroma.scale(colorscale).domain([min, max]);

      const extraOptions = {
        fillColor: csc(feature.properties[colorProp]),
      };

      // Lower opacity for sensors with stale data
      if (
        new Date() - new Date(feature.properties._time) >
        1000 * 60 * 60 * 2
      ) {
        extraOptions.fillOpacity = 0.3;
      } else {
        extraOptions.fillOpacity = 1;
      }

      // Highlight selected sensor
      if (selectedSensor === feature.properties.host) {
        extraOptions.stroke = true;
        extraOptions.color = "cyan";
        extraOptions.weight = 10;
      } else {
        extraOptions.stroke = false;
      }

      return L.circleMarker(latlng, {
        ...circleOptions,
        ...extraOptions,
      });
    },

    clusterToLayer: function (feature, latlng, index, context) {
      const { min, max, colorscale, colorProp } = context.props.hideout;
      const csc = chroma.scale(colorscale).domain([min, max]);

      // Set color based on mean value of leaves.
      const leaves = index.getLeaves(feature.properties.cluster_id);
      let valueSum = 0;
      for (let i = 0; i < leaves.length; ++i) {
        valueSum += leaves[i].properties[colorProp];
      }
      const valueMean = valueSum / leaves.length;

      // Render a circle with the number of leaves written in the center.
      const icon = L.divIcon.scatter({
        html:
          '<div style="background-color:white;"><span>' +
          feature.properties.point_count_abbreviated +
          "</span></div>",
        className: "marker-cluster",
        iconSize: L.point(40, 40),
        color: csc(valueMean),
      });
      return L.marker(latlng, {
        icon: icon,
      });
    },
  },
});
