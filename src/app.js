import { Loader } from '@googlemaps/js-api-loader';
const apiKey = require('./keys.json').apiKey;

const styleOptions = {
  strokeColor: 'green',
  strokeWeight: 2,
  strokeOpacity: 1,
  fillColor: 'green',
  fillOpacity: 0.3,
};

const loader = new Loader({
  apiKey: apiKey,
  version: 'weekly',
  libraries: ['places']
});

function fetchMarkers() {
  // Uncomment the code below to fetch data from a URL
  /*
  fetch('https://example.com/data')
    .then(response => response.json())
    .then(data => {
      // Process the fetched data
      // Replace the markers array with the fetched data
      const markers = data;
      // Rest of the code...
    })
    .catch(error => {
      console.error('Error fetching data:', error);
    });
  */

  // Mocking the response with a simple list of 3 examples
  const markers = [
    {
      type: 'Feature',
      geometry: {
        type: 'Point',
        coordinates: [14.860664, 46.208138]
      },
      properties: {
        name: 'Marker 1',
        description: 'This is marker 1',
        severity: 1
      }
    },
    {
      type: 'Feature',
      geometry: {
        type: 'Point',
        coordinates: [14.862345, 46.209876]
      },
      properties: {
        name: 'Marker 2',
        description: 'This is marker 2',
        severity: 2
      }
    },
    {
      type: 'Feature',
      geometry: {
        type: 'Point',
        coordinates: [14.865432, 46.207654]
      },
      properties: {
        name: 'Marker 3',
        description: 'This is marker 3',
        severity: 3
      }
    }
  ];

  return markers;
}

loader.load().then(() => {
  console.log('Maps JS API loaded');
  const map = displayMap();
  map.data.loadGeoJson("test.json");
  map.data.addListener('click', function(event) {
    const position = event.latLng;
    const content = "<img src='.data/test_img.png' width='200px' height='200px'>";
    const infoWindow = new google.maps.InfoWindow({
      position: position,
      content: content
    });
    infoWindow.open(map);
  });
  const markers = fetchMarkers();

  const marker_list = document.getElementById('marker_list');
  markers.forEach(marker => {
    const listItem = document.createElement('a');
    listItem.classList.add('w3-bar-item', "w3-button");
    switch (marker.properties.severity) {
      case 1:
        listItem.classList.add('w3-yellow');
        break;
      case 2:
        listItem.classList.add('w3-orange');
        break;
      case 3:
        listItem.classList.add('w3-red');
        break;
    }
    listItem.textContent = marker.properties.name;
    marker_list.appendChild(listItem);
    listItem.addEventListener('click', function() {
      const coordinates = new google.maps.LatLng(marker.geometry.coordinates[1], marker.geometry.coordinates[0]);
      map.setCenter(coordinates);
    });
  });

});

function displayMap() {
  const mapOptions = {
    center: { lat: 46.208138, lng: 14.860664},
    zoom: 14,
    mapId: '6c66ec448a80214c'
  };
  const mapDiv = document.getElementById('map');
  return new google.maps.Map(mapDiv, mapOptions);
}