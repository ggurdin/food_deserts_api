/* AJAX API calls for map data */

function get_demographics_data(api_endpoint, api_key) {
    var endpoint = `${api_endpoint}/tract_demographics/`
    return $.ajax({
        url: endpoint,
        headers: {'x-access-token': api_key},
        dataType: 'json'
    })
}

function get_distance_data(distance, api_endpoint, api_key) {
    var endpoint = `${api_endpoint}/access/${distance}`
    return $.ajax({
        url: endpoint,
        headers: {'x-access-token': api_key},
        dataType: 'json'
    })
}