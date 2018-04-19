document.addEventListener('DOMContentLoaded', () => {
    // Only execute on table, query and row pages
    if (document.querySelector('body.table,body.row,body.query')) {
        // Does it have Latitude and Longitude columns?
        var columns = Array.prototype.map.call(
            document.querySelectorAll('th'),
            (th) => {
                return th.className.replace(/^col\-/, '')
            }
        );
        var latitudeColumn = null;
        var longitudeColumn = null;
        columns.forEach((col) => {
            if (col.toLowerCase() == 'latitude') {
                latitudeColumn = col;
            }
            if (col.toLowerCase() == 'longitude') {
                longitudeColumn = col;
            }
        });
        if (latitudeColumn && longitudeColumn) {
            addMap(latitudeColumn, longitudeColumn);
        }
    }
});

function addMap(latitudeColumn, longitudeColumn) {
	var path = location.pathname + '.jsono' + location.search;
    fetch(path).then(r => r.json()).then(data => {
		var el = document.createElement('div');
	    el.style.width = '100%';
	    el.style.height = '400px';
		el.style.marginBottom = '2em';
	    var tiles = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
	        maxZoom: 19,
	        detectRetina: true,
	        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors, Points &copy 2012 LINZ'
	    }),
	    latlng = L.latLng(0, 0);
	    var map = L.map(el, {
	        //center: latlng,
	        zoom: 13,
	        layers: [tiles]
	    });
		var table = document.getElementsByTagName('table')[0];
	    table.parentNode.insertBefore(el, table);
	    var currentLayer = L.markerClusterGroup({
	        chunkedLoading: true,
	        maxClusterRadius: 50
	    });
        var markerList = [];
        data.rows.forEach((row) => {
            if (row[latitudeColumn] && row[longitudeColumn]) {
                var title = JSON.stringify(row, null, 4);
                var marker = L.marker(
                    L.latLng(
                        row[latitudeColumn],
                        row[longitudeColumn]
                    ),
                    {title: title}
                );
                marker.bindPopup('<pre>' + title + '</pre>');
                markerList.push(marker);
            }
        });
        currentLayer.addLayers(markerList);
        map.addLayer(currentLayer);
        map.fitBounds(currentLayer.getBounds());
    });
}
