$("#sidebar-hide-btn").click(function () {
  animateSidebar();
  $('.mini-submenu').fadeIn();
  return false;
});


$('.mini-submenu').on('click', function () {
  animateSidebar();
  $('.mini-submenu').hide();
})

function animateSidebar() {
  $("#sidebar").animate({
    width: "toggle"
  }, 350, function () {
    map.invalidateSize();
  });
}


var baseLayer = L.esri.basemapLayer('Topographic')
map = L.map("map", {
  zoom: 4,
  center: [39.98, -90],
  layers: [baseLayer],
  zoomControl: false,
  attributionControl: false,
  maxZoom: 18
});

var layer = null;

var select = document.getElementById("map-select");
var options = ["10km", "3km"]

for (var i = 0; i < options.length; i++) {
  var opt = options[i];
  var el = document.createElement("option");
  el.textContent = opt;
  el.value = opt;
  select.appendChild(el);
}

// $('#stop-select').val('3RDMAIS').trigger('change');

$("#map-select").change(function (val) {
  var resolution = $("#map-select").val();
  addLayer(resolution);

})

function addLayer(resolution) {

  var base_url = "https://luyuliu.github.io/sharpe/visualization/data/";
  var full_url = base_url + "ascii_" + resolution + ".asc";

  try {
    map.removeLayer(layer);
  } catch (error) {
    console.error("Start.");
  }

  d3.text(full_url, function (asc) {
    var s = L.ScalarField.fromASCIIGrid(asc);
    layer = L.canvasLayer.scalarField(s, {
      color: chroma.scale(['730000', 'e60000', 'e69800', 'fed37f', 'fefe00', 'ffffff', 'aaf596', '4ce600', '38a800', '145a00', '002673']).classes([0, 0.02, 0.05, 0.1, 0.2, 0.3, 0.7, 0.8, 0.9, 0.95, 0.98, 1]),
      opacity: 0.75
    }).addTo(map);
    layer.on('click', function (e) {
      if (e.value !== null) {
        let v = d3.format(".2f")(e.value.toFixed(4) * 100); let html = `<span class = "popupText" style="font-family:sans-serif"> <b>Percentile (5cm):</b> ${v}%</span>`;
        L.popup().setLatLng(e.latlng).setContent(html).openOn(mymap);
      };
    });
  });

}


window.onload = function (e) {
  $('#map-select').val('10km').trigger('change');
}