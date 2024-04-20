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

loader.load().then(() => {
  console.log('Maps JS API loaded');
  const map = displayMap();
  map.data.loadGeoJson("test.json");
  
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