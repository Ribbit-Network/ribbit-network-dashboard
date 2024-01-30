(function () {
  const STALE_THRESHOLD_DAYS = 2;
  const STALE_THRESHOLD_MS = STALE_THRESHOLD_DAYS * 24 * 60 * 60 * 1000;
  const STALE_OPACITY = 0.3;
  const NORMAL_OPACITY = 1;

  // const HIGHLIGHT_CIRCLE = {
  //   stroke: true,
  //   color: "cyan",
  //   weight: 10,
  // };

  const HIGHLIGHT_CIRCLE = {
    //Made Markers more distinct
    fillColor: '#ff0000',
    color: '#ffffff',
    fillOpacity: 1,
  };

  const UNHIGHLIGHT_CIRCLE = {
    stroke: false,
  };

  function pointToLayer(feature, latlng, context) {
    const { min, max, colorscale, circleOptions, colorProp, selectedSensor } =
      context.props.hideout;
    const csc = chroma.scale(colorscale).domain([min, max]);

    const extraOptions = {
      fillColor: csc(feature.properties[colorProp]),
    };

    // Lower opacity for sensors with stale data
    if (new Date() - new Date(feature.properties._time) > STALE_THRESHOLD_MS) {
      extraOptions.fillOpacity = STALE_OPACITY;
    } else {
      extraOptions.fillOpacity = NORMAL_OPACITY;
    }

    // Highlight selected sensor
    if (selectedSensor === feature.properties.host) {
      Object.assign(extraOptions, HIGHLIGHT_CIRCLE);
    } else {
      Object.assign(extraOptions, UNHIGHLIGHT_CIRCLE);
    }

    const marker = L.circleMarker(latlng, {
      ...circleOptions,
      ...extraOptions,
    });
    //Execute pulse animation on selected sensor
    if (selectedSensor === feature.properties.host) {
      // Add 'pulse-marker' class to the marker's DOM element
      marker.on('add', function () {
        const markerDom = marker.getElement();
        markerDom.classList.add('pulse-marker');
      });
    }
    return marker;
  }

  function clusterToLayer(feature, latlng, index, context) {
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
  }

  window.ribbit = Object.assign({}, window.ribbit, {
    map: {
      pointToLayer,
      clusterToLayer,
    },
  });
})();
