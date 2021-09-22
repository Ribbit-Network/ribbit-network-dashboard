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
        }
    }
});