/*
MIT License

Copyright (c) 2016 Kluizeberg

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

https://github.com/kluizeberg/Leaflet.Map-hash
*/

L.Map.mergeOptions({
	urlHash: false
});

L.Map.include({
	_onHashChange: function () {
		var center;
		var hash = L.parseParamString(window.location.hash.slice(1));
		var zoom;

		function isNum(n) {
			return typeof n === 'number';
		}

		if (isNum(hash.lng) && isNum(hash.lat)) {
			center = new L.LatLng(hash.lat, hash.lng);
		} else if (isNum(hash.lon) && isNum(hash.lat)) { // lon as lng
			center = new L.LatLng(hash.lat, hash.lon);
		} else if (isNum(hash.x) && isNum(hash.y)) { // cartesian coordinates
			center = this.options.crs.unproject(new L.Point(hash.x, hash.y));
		} else {
			center = this.getCenter();
		}

		if (isNum(hash.zoom)) {
			zoom = hash.zoom;
		}

		this.setView(center, zoom); // (re)sets hash through moveend handler
	},

	_setHash: function () {
		var center = this.getCenter();
		var zoom = this.getZoom();
		var decimals = 5;

		window.history.replaceState(null, '', '#' + [ // no history
			'lng='  + center.lng.toFixed(decimals),
			'lat='  + center.lat.toFixed(decimals),
			'zoom=' + zoom
		].join(';'));
	}
});

L.Map.addInitHook(function () {
	if (this.options.urlHash) {
		this.whenReady(function () {
			L.DomEvent.on(window, 'hashchange', this._onHashChange, this);

			this.on('moveend', this._setHash);

			if (window.location.hash) {
				this._onHashChange();
			}
		});
	}
});

/* utility/helper method */

L.parseParamString = function (str, result) { // key=value;k2=v2&k3=v3
	function parse(s) {
		switch (s) {
			case 'null':
				return null;
			case 'false':
				return false;
			case 'true':
				return true;
			default:
				var n = parseFloat(s);
				return !isNaN(n) && isFinite(s) ? n : decodeURIComponent(s.replace(/\+/g, ' '));
		}
	}

	result = result || {};
	str.replace(/([^&;=]+)=([^&;]*)/gi, function (match, key, value) {
		result[decodeURIComponent(key)] = parse(value);
	});

	return result;
};
