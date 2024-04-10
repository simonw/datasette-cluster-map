const clusterMapCSS = `
dl.cluster-map-dl {
    font-size: 1.1em;
}
dl.cluster-map-dl dt {
    font-weight: bold;
}
dl.cluster-map-dl dd {
    margin: 0px 0 0 0.7em;
}
dl.cluster-map-dl dd span {
    color: #aaa;
    font-size: 0.8em;
}
button.cluster-map-button {
    color: #fff;
    background-color: #007bff;
    border-color: #007bff;
    vertical-align: middle;
    cursor: pointer;
    border: 1px solid blue;
    padding: 0.3em 0.8em;
    font-size: 0.6rem;
    line-height: 1;
    border-radius: .25rem;
}
`;

document.addEventListener("DOMContentLoaded", () => {
  // Only execute on table, query and row pages
  if (document.querySelector("body.table,body.row,body.query")) {
    // Does it have Latitude and Longitude columns?
    let columns = Array.prototype.map.call(
      document.querySelectorAll("table.rows-and-columns th"),
      (th) => (th.getAttribute("data-column") || th.textContent).trim()
    );
    let latitudeColumn = null;
    let longitudeColumn = null;
    columns.forEach((col) => {
      if (
        col.toLowerCase() ==
        (
          window.DATASETTE_CLUSTER_MAP_LATITUDE_COLUMN || "latitude"
        ).toLowerCase()
      ) {
        latitudeColumn = col;
      }
      if (
        col.toLowerCase() ==
        (
          window.DATASETTE_CLUSTER_MAP_LONGITUDE_COLUMN || "longitude"
        ).toLowerCase()
      ) {
        longitudeColumn = col;
      }
    });
    if (latitudeColumn && longitudeColumn) {
      // Load dependencies and then add the map
      const loadDependencies = (callback) => {
        let loaded = [];
        function hasLoaded() {
          loaded.push(this);
          if (loaded.length == 3) {
            callback();
          }
        }
        let stylesheet = document.createElement("link");
        stylesheet.setAttribute("rel", "stylesheet");
        stylesheet.setAttribute("href", datasette.leaflet.CSS_URL);
        stylesheet.onload = hasLoaded;
        document.head.appendChild(stylesheet);
        let stylesheet2 = document.createElement("link");
        stylesheet2.setAttribute("rel", "stylesheet");
        stylesheet2.setAttribute(
          "href",
          datasette.cluster_map.MARKERCLUSTER_CSS_URL
        );
        stylesheet2.onload = hasLoaded;
        document.head.appendChild(stylesheet2);
        // Leaflet needs to be loaded before Leaflet.clustermap
        import(datasette.leaflet.JAVASCRIPT_URL).then(() => {
            import(datasette.cluster_map.MARKERCLUSTER_URL).then(hasLoaded);
        });
      };
      loadDependencies(() => addClusterMap(latitudeColumn, longitudeColumn));
    }
  }
});

const clusterMapEscapeHTML = (s) =>
  s
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");

const clusterMapMarkerContent = (row) => {
  // if row has popup, use that
  let popup = row.popup;
  if (popup) {
    // It may be JSON or a string
    if (typeof popup === "string") {
      try {
        popup = JSON.parse(popup);
      } catch (e) {
        popup = {};
      }
    }
    if (popup.image || popup.title || popup.description || popup.link) {
      // We have a valid popup configuration - render that
      let html = [];
      if (popup.link) {
        html.push('<a href="' + clusterMapEscapeHTML(popup.link) + '">');
      }
      if (popup.title) {
        html.push(
          "<p><strong>" + clusterMapEscapeHTML(popup.title) + "</strong></p>"
        );
      }
      if (popup.image) {
        html.push(
          '<img style="max-width: 100%" src="' +
            clusterMapEscapeHTML(popup.image) +
            '"'
        );
        if (popup.alt) {
          html.push(' alt="' + clusterMapEscapeHTML(popup.alt) + '"');
        }
        html.push(">");
      }
      if (popup.description) {
        html.push(
          '<p style="text-decoration: none; color: black;">' +
            clusterMapEscapeHTML(popup.description) +
            "</p>"
        );
      }
      if (popup.link) {
        html.push("</a>");
      }
      return html.join("");
    }
  }

  function addAsLink(element, parent) {
    if (element.startsWith('http://') || element.startsWith('https://')) {
      const text = document.createTextNode('link\n');
      var link = document.createElement('a');
      link.setAttribute('href', element);
      link.appendChild(text);
      parent.appendChild(link);
    } else {
      parent.appendChild(document.createTextNode(element));
    }
  };

  // Otherwise, use a <dl>
  const dl = document.createElement("dl");
  Object.keys(row).forEach((key) => {
    const dt = document.createElement("dt");
    dt.appendChild(document.createTextNode(key));
    const dd = document.createElement("dd");
    let value = row[key];
    let label = value;
    let extra = null;
    if (typeof value === "object") {
      if (
        value !== null &&
        value.label !== undefined &&
        value.value !== undefined
      ) {
        label = value.label;
        extra = document.createElement("span");
        extra.appendChild(document.createTextNode(" " + value.value));
      } else {
        label = JSON.stringify(value);
      }
    }
    const parts = label.toString().split('\n');
    if (parts.length > 1) {
      parts.forEach((part) => addAsLink(part, dd));
    } else {
      addAsLink(label.toString(), dd);
    }
    if (extra) {
      dd.appendChild(extra);
    }
    dl.appendChild(dt);
    dl.appendChild(dd);
  });
  return (
    '<dl class="cluster-map-dl" style="height: 100%; overflow: auto">' +
    dl.innerHTML +
    "</dl>"
  );
};

const addClusterMap = (latitudeColumn, longitudeColumn) => {
  let keepGoing = false;

  let style = document.createElement("style");
  style.innerText = clusterMapCSS;
  document.head.appendChild(style);

  function isValidLatitude(latitude) {
    latitude = parseFloat(latitude);
    if (isNaN(latitude)) {
      return false;
    }
    return latitude >= -90 && latitude <= 90;
  }
  function isValidLongitude(longitude) {
    longitude = parseFloat(longitude);
    if (isNaN(longitude)) {
      return false;
    }
    return longitude >= -180 && longitude <= 180;
  }

  const loadMarkers = (path, map, markerClusterGroup, progressDiv, count) => {
    count = count || 0;
    return fetch(path)
      .then((r) => r.json())
      .then((data) => {
        let markerList = [];
        data.rows.forEach((row) => {
          if (isValidLatitude(row[latitudeColumn]) && isValidLongitude(row[longitudeColumn])) {
            let markerContent = clusterMapMarkerContent(row);
            let marker = L.marker(
              L.latLng(row[latitudeColumn], row[longitudeColumn])
            );
            marker.bindPopup(markerContent);
            markerList.push(marker);
          }
        });
        count += data.rows.length;
        markerClusterGroup.addLayers(markerList);
        map.fitBounds(markerClusterGroup.getBounds());
        let percent = "";
        let button;
        // Fix for http v.s. https
        let next_url = data.next_url;
        if (next_url && location.protocol == "https:") {
          next_url = next_url.replace(/^https?:/, "https:");
        }
        if (next_url) {
          percent = ` (${
            Math.round((count / data.filtered_table_rows_count) * 100 * 100) /
            100
          }%)`;
          // Add a control to either continue loading or pause
          button = document.createElement("button");
          button.classList.add("cluster-map-button");
          if (keepGoing) {
            button.innerHTML = "pause";
            button.addEventListener("click", () => {
              keepGoing = false;
            });
          } else {
            button.innerHTML = "load all";
            button.addEventListener("click", () => {
              keepGoing = true;
              loadMarkers(
                next_url,
                map,
                markerClusterGroup,
                progressDiv,
                count,
                keepGoing
              );
            });
          }
          progressDiv.innerHTML = `Showing ${count.toLocaleString()} of ${data.filtered_table_rows_count.toLocaleString()}${percent} `;
          if (button) {
            progressDiv.appendChild(button);
          }
        } else {
          progressDiv.innerHTML = "";
        }
        if (next_url && keepGoing) {
          return loadMarkers(
            next_url,
            map,
            markerClusterGroup,
            progressDiv,
            count
          );
        }
      });
  };

  let el = document.createElement("div");
  el.style.width = "100%";
  el.style.height = "500px";
  let tiles = L.tileLayer(
      window.DATASETTE_CLUSTER_MAP_TILE_LAYER,
      window.DATASETTE_CLUSTER_MAP_TILE_LAYER_OPTIONS
    ),
    latlng = L.latLng(0, 0);
  let map = L.map(el, {
    //center: latlng,
    zoom: 13,
    layers: [tiles],
  });
  const container = window.DATASETTE_CLUSTER_MAP_CONTAINER;
  if (container && document.querySelector(container)) {
    document.querySelector(container).appendChild(el);
  } else {
    let table =
      document.querySelector(".table-wrapper") ||
      document.querySelector("table.rows-and-columns");
    table.parentNode.insertBefore(el, table);
  }
  let progressDiv = document.createElement("div");
  progressDiv.style.marginBottom = "2em";
  el.parentNode.insertBefore(progressDiv, el.nextSibling);
  let markerClusterGroup = L.markerClusterGroup({
    chunkedLoading: true,
    maxClusterRadius: 50,
  });
  map.addLayer(markerClusterGroup);
  let path = location.pathname + ".json" + location.search;
  if (path.indexOf("?") > -1) {
    path += "&_size=max&_labels=on&_shape=objects";
  } else {
    path += "?_size=max&_labels=on&_shape=objects";
  }
  loadMarkers(path, map, markerClusterGroup, progressDiv, 0);
};
