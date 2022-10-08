/* utility functions used to structure data for plotly mapbox */

function unpack(rows, key) {
    return rows.map(function(row) { return row[key]; });
}

function stack(rows) {
    let ret = [] 
    for (var i = 0; i < rows[0].length; i++) {
        let temp = []
        for (j = 0; j < rows.length; j++) {
            temp.push(rows[j][i])
        }
        ret.push(temp)
    }
    return ret
}
