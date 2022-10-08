/* function for making and updating plotly map */

function update_info_text(data) {
    var population = unpack(data, "population")
    var income = unpack(data, "median_family_income")
    var low_income = unpack(data, "low_income_population")
    
    population = population.reduce((accumulator, value) => {
        return accumulator + value;
    }, 0);

    income = income.reduce((a, b) => a + b, 0) / income.length;
    income = income.toFixed(2)

    low_income = low_income.reduce((accumulator, value) => {
        return accumulator + value;
    }, 0);

    $("#population-txt").text(population)
    $("#income-txt").text("$" + income)
    $("#low-income-txt").text(low_income)
}

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
        marker: {"opacity": 0.5},
        selected: {marker: {opacity: 0.8}}
    }];

    var layout = {
        dragmode: false,
        width: 700, 
        height: 600, 
        mapbox: {
            style: 'dark',
            center: {lon: -77.434769, lat: 37.4}, 
            zoom: 7.7
        }, 
        margin: {"r":0,"t":0,"l":0,"b":0}
    };
    return [data, layout]
}

function update_buttons(mapDiv, endpoint, key) {
    $("button").on("click", function() {
        $("button").removeClass("active");
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

    $("#distance_dropdown > button").on("click", function() {
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

function set_select_events(mapDiv) {
    mapDiv.on("plotly_click", function(data) {
        var customdata = data.points[0].customdata
        var county = customdata[0]
        var population = customdata[1]
        var median_income = customdata[2]
        var low_income = customdata[3]
        var tract = data.points[0].location

        $("#location-txt").html(`${county}<br><span style="font-size: 16px;">Census Tract #${tract}</span>`)
        $("#population-txt").text(population)
        $("#income-txt").text("$" + median_income)
        $("#low-income-txt").text(low_income)

        var center = data.points[0].ct
        center = {lon: center[0], lat: center[1]}

        var tract_idx = data.points[0].pointIndex;
        mapDiv.data[0].selectedpoints = [tract_idx]
        Plotly.redraw(mapDiv)
    })

    mapDiv.on('plotly_doubleclick', function() {
        var demographics = stack(mapDiv.data[0].customdata)

        var population = demographics[1].reduce((accumulator, value) => {
            return accumulator + value;
        }, 0);
    
        var income = demographics[2]
        income = income.reduce((a, b) => a + b, 0) / income.length;
        income = income.toFixed(2)
    
        var low_income = demographics[3].reduce((accumulator, value) => {
            return accumulator + value;
        }, 0);
    
        $("#location-txt").text("Greater Richmond Area")
        $("#population-txt").text(population)
        $("#income-txt").text("$" + income)
        $("#low-income-txt").text(low_income)

        mapDiv.data[0].selectedpoints = null
        mapDiv.data[0].marker.opacity = 0.5
        Plotly.redraw(mapDiv)
    });
}