/* function for making and updating plotly map */

function make_map(locations, z, customdata, geojson) {
    var data = [{
        type: 'choroplethmapbox',
        locations: locations,
        customdata: customdata,
        z: z,
        geojson: geojson,
        featureidkey: "properties.GEO_ID",
        colorscale: [
            [0, 'rgb(230,240,245)'], [0.2, 'rgb(201,218,233)'],
            [0.4, 'rgb(162,190,218)'], [0.6, 'rgb(141,126,187)'],
            [0.8, 'rgb(134,58,151)'], [1, 'rgb(84,2,83)']
        ],
        showscale: false,
        hovertemplate: "%{customdata[0]}<br>Population: %{customdata[1]}<extra></extra>",
        marker: {"opacity": 0.5}
    }];

    var layout = {
        dragmode: false,
        width: 650, 
        height: 550, 
        mapbox: {
            style: 'dark',
            center: {lon: -77.434769, lat: 37.4}, 
            zoom: 7.7,
        }, 
        margin: {"r":0,"t":0,"l":0,"b":0}
    };
    return [data, layout]
}

function update_buttons(mapDiv, endpoint, key) {
    $("input").on("click", function() {
        $("input").removeClass("active");
        $(this).addClass("active");
    });
    
    $("#population-btn").on("click", function() {
        get_demographics_data(endpoint, key)
        .then(data => {
            data = data['demographics']
            population = unpack(data, 'population')
            mapDiv.data[0].z = population
            mapDiv.data[0].hovertemplate = "%{customdata[0]}<br>Population: %{z}<extra></extra>"
            Plotly.redraw(mapDiv)
        })
        .catch(error => console.log('Error:', error));
    });    

    $("#income-btn").on("click", function() {
        get_demographics_data(endpoint, key)
        .then(data => {
            data = data['demographics']
            population = unpack(data, 'median_family_income')
            mapDiv.data[0].z = population
            mapDiv.data[0].hovertemplate = "%{customdata[0]}<br>Median Income: %{z}<extra></extra>"
            Plotly.redraw(mapDiv)
        })
        .catch(error => console.log('Error:', error));
    });

    $("#distance_dropdown > input").on("click", function() {
        var distance = $(this).attr("name")

        get_distance_data(distance, endpoint, key)
        .then(data => {
            data = data['demographics']
            la_population = unpack(data, 'low_access_population')
            mapDiv.data[0].z = la_population
            mapDiv.data[0].hovertemplate = "%{customdata[0]}<br>Low Access Population: %{z}<extra></extra>"
            Plotly.redraw(mapDiv)
        })
        .catch(error => console.log('Error:', error));

        $("#dropdownMenuButton").addClass("active");
    });
}

// mapDiv.on('plotly_click', function(data) {
//     var county = data.points[0].customdata[0]
//     var tract = data.points[0].location
//     $("#static-title").hide()
//     $("#dynamic-title").text(`Census Tract #${tract}\t${county}`)
//     $("#dynamic-title").show()

//     var tract_id = data.points[0].location
//     let geojson = '{{ geojson }}'.replaceAll("&#39;", '"')
//     geojson = JSON.parse(geojson)

//     for (var i = 0; i < geojson.features.length; i++) {
//         if (geojson.features[i].properties.GEO_ID == tract_id) {
//             geojson.features = geojson.features[i]
//             break
//         }
//     }
//     mapDiv.layout.mapbox.zoom *= 1.3
//     var center = data.points[0].ct
//     mapDiv.layout.mapbox.center = {"lat": center[1], "lon": center[0]}
//     Plotly.redraw(mapDiv)
// });