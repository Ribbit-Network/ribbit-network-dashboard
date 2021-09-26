window.dashExtensions = Object.assign({}, window.dashExtensions, {
    default: {
        function0: function(feature, latlng, context) {
            const {
                min,
                max,
                colorscale,
                circleOptions,
                colorProp
            } = context.props.hideout;
            const csc = chroma.scale(colorscale).domain([min, max]);
            circleOptions.fillColor = csc(feature.properties[colorProp]);
            return L.circleMarker(latlng, circleOptions);
        },
        function1: function(feature, latlng, index, context) {
            const {
                min,
                max,
                colorscale,
                circleOptions,
                colorProp
            } = context.props.hideout;
            const csc = chroma.scale(colorscale).domain([min, max]);
            // Set color based on mean value of leaves.
            const leaves = index.getLeaves(feature.properties.cluster_id);
            let valueSum = 0;
            for (let i = 0; i < leaves.length; ++i) {
                valueSum += leaves[i].properties[colorProp]
            }
            const valueMean = valueSum / leaves.length;
            // Render a circle with the number of leaves written in the center.
            const icon = L.divIcon.scatter({
                html: '<div style="background-color:white;"><span>' + feature.properties.point_count_abbreviated + '</span></div>',
                className: "marker-cluster",
                iconSize: L.point(40, 40),
                color: csc(valueMean)
            });
            return L.marker(latlng, {
                icon: icon
            })
        }
    }
});