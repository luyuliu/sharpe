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
  zoom: 13,
  center: [39.98, -83],
  layers: [baseLayer],
  zoomControl: false,
  attributionControl: false,
  maxZoom: 18
});

function createCORSRequest(method, url) {
  var xhr = new XMLHttpRequest();
  if ("withCredentials" in xhr) {
    xhr.open(method, url, true);

  } else if (typeof XDomainRequest != "undefined") {
    xhr = new XDomainRequest();
    xhr.open(method, url);

  } else {
    xhr = null;

  }
  return xhr;
}

var scooterIcon = L.icon({
  iconUrl: './img/s.svg',
  iconSize: [20, 20], // size of the icon
});

var stopIcon = L.icon({
  iconUrl: './img/stop.png',
  iconSize: [20, 20], // size of the icon
})

var electronicIcon = L.icon({
  iconUrl: './img/e.png',
  iconSize: [20, 20], // size of the icon
});

$("#add-btn").click(function () {
  $("#time-input").val(parseInt($("#time-input").val()) + 120)
});

var select = document.getElementById("stop-select");
var options = ['MOREASS', 'HIGCOON', '4TH15TN', 'TREZOLS', 'KARPAUN', 'LIVGRAE', 'GRESHEW', 'MAIOHIW', 'AGL540W', 'WHIJAEE', '3RDCAMW', 'HARZETS', 'MAIBRICE', 'SAI2NDS', '3RDMAIS', 'STYCHAS', 'LOC230N', 'BETDIEW', 'STEMCCS', 'INNWESE', 'HANMAIN', 'HIGINDN', '4THCHIN', 'RIDSOME', 'KARHUYN', 'LIVBURE', 'LONWINE', 'MAICHAW', 'BROHAMIW', 'WHI3RDE', '1STLINW', 'MAINOEW', 'MAIIDLE', '5THCLEE', '3RDTOWS', 'STYGAMS', 'KOE113W', 'TAM464S', 'CAS150S', 'BROOUTE', 'ALUGLENS', 'FRABREN', 'SOU340N', 'HILTINS', 'STRHOVE', 'SAWCOPN', 'HAMWORN', 'DALDUBN', 'MCNCHEN', 'HILBEAS', 'NOROWEN', 'SOUTER2A', 'GENSHAN', 'VACLINIC', 'MORHEATE', 'KOEEDSW1', 'TRAMCKW', 'FAISOUN', 'SAWSAWN', 'CLIHOLE', 'CHAMARN', 'CLE24THN']

for (var i = 0; i < options.length; i++) {
  var opt = options[i];
  var el = document.createElement("option");
  el.textContent = opt;
  el.value = opt;
  select.appendChild(el);
}

normalMarkers = []
scooterMarkers = []
scooterLocationMarker = []
scooterLocationFlag = false
startStop = null
queryStop = null


timeBudget = 60 * 60
theTimeStamp = 1561932000
theScooterDate = "20190630"

$("#start-btn").click(function () {
  todayDate = $("#date-input").val().replace('-', '').replace('-', '')
  console.log(todayDate)
  timestamp = parseInt($("#time-input").val())

  $.get('http://127.0.0.1:50022/lime_location?where={"ts":' + timestamp + '}', function (rawstops) {
    stops = rawstops._items
    console.log(stops)

    for (var i = 0; i < stops.length; i++) {
      var stop = stops[i];
      if (stop.type_name == "scooter") {
        var point = L.marker([stop.latitude, stop.longitude], { icon: scooterIcon }).addTo(map);
      }
      else {
        var point = L.marker([stop.latitude, stop.longitude], { icon: electronicIcon }).addTo(map);
      }
      point.bindPopup("<b>Meter range: " + stop.meter_range + "</b><br><b>Battery level: " + stop.battery_level + "</b><br><b>Last Three: " + stop.last_three + "</b>")

    }

  });
});

$("#scooter-btn").click(scooterButtonEvent);

function scooterButtonEvent() {
  // todayDate = $("#cota-date-input").val().replace('-', '').replace('-', '')
  // console.log(todayDate)
  // timestamp = parseInt($("#cota-time-input").val())
  timestamp = theTimeStamp
  timeDeltaLimit = timeBudget;
  walkingSpeed = 1.4
  walkingDistanceLimit = 700
  walkingTimeLimit = walkingDistanceLimit / walkingSpeed
  startStopID = $("#stop-select").val()
  console.log("Start", startStopID)
  var queryURL = 'http://127.0.0.1:20196/abtest_scooter_' + timestamp + '?where={"startStopID":"' + startStopID + '"}'
  console.log(queryURL)
  $.get(queryURL, function (rawstops) {
    stops = rawstops._items
    // console.log(stops)

    for (var i = 0; i < stops.length; i++) {
      var stop = stops[i];
      var radius = (timeDeltaLimit - (stop.time)) * walkingSpeed / 20

      if (radius < 0) {
        radius = 0
      }
      if (radius > walkingDistanceLimit) {
        radius = walkingDistanceLimit
      }
      // console.log(stop)
      // console.log(stop.accessible_stop_id, radius)
      var marker1 = L.circle([stop.stop_lat, stop.stop_lon], {
        color: "red",
        radius: radius,
        stroke: 0,
        opacity: 1
      }).addTo(map);
      marker1.bindPopup("<b>stop ID: " + stop.receivingStopID + "</b><br><b>busTime: " + stop.busTime + "</b><br><b>scooterTime: " + stop.scooterTime + "</b><br><b>walkTime: " + stop.walkTime + "</b><br><b>firstScooterIncrement: " + stop.firstScooterIncrement + "</b><br><b>firstmile scooter ID: " + stop.firstScooterID + "</b> " + "<br><b>lastmile scooter increment: " + stop.lastmileScooterID + "</b>" + "<br><b>lastmile scooter ID: " + stop.lastmileScooterIncrement + "</b>" + "<br><b>time: " + stop.time + "</b>")
      scooterMarkers.push(marker1)
    }

  });
}

$("#normal-btn").click(normalButtonEvent);

function normalButtonEvent() {
  // todayDate = $("#cota-date-input").val().replace('-', '').replace('-', '')
  // console.log(todayDate)
  // timestamp = parseInt($("#cota-time-input").val())
  timestamp = theTimeStamp;
  timeDeltaLimit = timeBudget;
  walkingSpeed = 1.4
  walkingDistanceLimit = 700
  walkingTimeLimit = walkingDistanceLimit / walkingSpeed
  console.log("Start")
  startStopID = $("#stop-select").val()
  var queryURL = 'http://127.0.0.1:20196/abtest_normal_' + timestamp + '?where={"startStopID":"' + startStopID + '"}'
  console.log(queryURL)
  $.get(queryURL, function (rawstops) {
    stops = rawstops._items
    // console.log(stops)

    for (var i = 0; i < stops.length; i++) {
      var stop = stops[i];
      var radius = (timeDeltaLimit - (stop.time)) * walkingSpeed / 20

      if (radius < 0) {
        radius = 0
      }
      if (radius > walkingDistanceLimit) {
        radius = walkingDistanceLimit
      }
      // console.log(stop.stop_id, radius)
      var marker = L.circle([stop.stop_lat, stop.stop_lon], {
        radius: radius,
        stroke: 0,
        opacity: 1
      }).addTo(map);
      marker.bindPopup("<b>stop ID: " + stop.accessible_stop_id + "</b><br><b>busTime: " + stop.busTime + "</b><br><b>scooterTime: " + stop.scooterTime + "</b><br><b>walkTime: " + stop.walkTime + "</b><br><b>transferTime: " + stop.transferTime + "</b><br><b>firstmile scooter ID: " + stop.firstmileScooterID + "</b> " + "<br><b>lastmile scooter ID: " + stop.lastmileScooterID + "</b>" + "<br><b>time: " + stop.time + "</b>")
      normalMarkers.push(marker)

      if (stop.accessible_stop_id == startStopID) {
        console.log("Add Icon")
        startStop = L.marker([stop.stop_lat, stop.stop_lon], { icon: stopIcon }).addTo(map);
      }
    }

  });
}

function scooterVisualization() {
  timestamp = theTimeStamp
  var url = 'http://127.0.0.1:50022/' + theScooterDate + '?where={"ts":' + timestamp + '}';
  console.log(url)
  $.get(url, function (rawstops) {
    stops = rawstops._items
    console.log(stops)

    for (var i = 0; i < stops.length; i++) {
      var stop = stops[i];
      var point = L.marker([stop.latitude, stop.longitude], { icon: scooterIcon }).addTo(map);
      point.bindPopup("<b>ID: " + stop.new_id + "</b><br><b>Battery level: " + stop.meter_range + "</b>")
      scooterLocationMarker.push(point);

    }

  });
}

$('#stop-select').change(function () {
  removeMarker();
  scooterButtonEvent();
  normalButtonEvent();
  if (!scooterLocationFlag) {
    scooterVisualization();
    scooterLocationFlag = true;
  }
  document.getElementById("scooter-checkbox").checked = true;
  document.getElementById("normal-checkbox").checked = true;

})

function removeMarker() {
  for (var i = 0; i < normalMarkers.length; i++) {
    map.removeLayer(normalMarkers[i])
  }
  for (var i = 0; i < scooterMarkers.length; i++) {
    map.removeLayer(scooterMarkers[i])
  }
  try {
    map.removeLayer(startStop)
  }
  catch (e) {
  }
}

$("#scooter-checkbox").click(function () {
  if ($(this).is(':checked')) {
    console.log("scooter open!")
    for (var i = 0; i < normalMarkers.length; i++) {
      scooterMarkers[i].setStyle({
        fillOpacity: 0.2
      })
    }
  } else {
    for (var i = 0; i < normalMarkers.length; i++) {
      scooterMarkers[i].setStyle({
        fillOpacity: 0
      })
    }
  }
});

$("#normal-checkbox").click(function () {
  if ($(this).is(':checked')) {
    console.log("scooter open!")
    for (var i = 0; i < normalMarkers.length; i++) {
      normalMarkers[i].setStyle({
        fillOpacity: 0.2
      })
    }

  } else {
    console.log("scooter close!")
    for (var i = 0; i < normalMarkers.length; i++) {
      normalMarkers[i].setStyle({
        fillOpacity: 0
      })
    }

  }
});

$("#scooterlocation-checkbox").click(function () {
  if ($(this).is(':checked')) {
    console.log("scooterlocation open!")
    for (var i = 0; i < scooterLocationMarker.length; i++) {
      scooterLocationMarker[i].setStyle({
        fillOpacity: 1
      })
    }

  } else {
    console.log("scooterlocation close!")
    for (var i = 0; i < scooterLocationMarker.length; i++) {
      scooterLocationMarker[i].setStyle({
        fillOpacity: 0
      })
    }

  }
});

$('#stop-input').keypress(function (e) {
  if (e.which == 13) {
    var stop_id = $("#stop-input").val();
    var queryURL = 'http://127.0.0.1:5555/1559154545_stops?where={"stop_id":"' + stop_id + '"}'
    $.get(queryURL, function (rawstops) {
      var stop = rawstops._items[0];
      console.log(stop)
      try {
        map.removeLayer(queryStop)
      }
      catch (e) {
      }
      queryStop = L.marker([stop.stop_lat, stop.stop_lon], { icon: stopIcon }).addTo(map);


    });
  }
});

$('#show-tragectory-button').click(function () {
  var start_stop = $("#start-stop-input").val();
  var start_stop = "3RDMAIS"
  var end_stop = $("#end-stop-input").val();

  var queryURL = 'http://127.0.0.1:20196/acctest_scooter_20190701_1561982400?where={"startStopID":"' + start_stop + '"}';

  $.get(queryURL, function (rawstops) {
    var stops = rawstops._items;
    // console.log(stops)
    var stopsDic = {}
    for (var i = 0; i < stops.length; i++) {
      var stop = stops[i];
      var receivingStopID = stop["receivingStopID"];
      stopsDic[receivingStopID] = stop;
    }

    var endPointID = end_stop;
    var count = 0;

    console.log(stopsDic[endPointID]["transferCount"], stopsDic[endPointID]["transferCountOG"])
    while (true) {
      // console.log(stopsDic)
      var endPoint = stopsDic[endPointID];
      var endPointLatLng = [endPoint["stop_lat"], endPoint["stop_lon"]];
      var startPointID = stopsDic[endPointID]["generatingStopID"];
      var startPoint = stopsDic[startPointID];
      if (startPoint == null) {
        break;
      }
      var startPointLatLng = [startPoint["stop_lat"], startPoint["stop_lon"]];

      var latlngs = [
        startPointLatLng,
        endPointLatLng
      ];

      var polyline = L.polyline(latlngs, { color: 'red', weight: 9 }).addTo(map);
      polyline.bindPopup("<b>trip type: " + endPoint["lastTripType"] + "   " + endPoint["lastTripID"])
      endPointID = startPointID;


      var marker = L.circle([endPoint["stop_lat"], endPoint["stop_lon"]], {
        radius: 100,
        color: "red"
      }).addTo(map);

      count++;
      if (count > 2000) {
        break
      }
    }

    var endPointID = end_stop;
    var count = 0;
    while (true) {
      // console.log(stopsDic)
      var endPoint = stopsDic[endPointID];
      var endPointLatLng = [endPoint["stop_lat"], endPoint["stop_lon"]];
      var startPointID = stopsDic[endPointID]["generatingStopIDOG"];
      var startPoint = stopsDic[startPointID];
      if (startPoint == null) {
        break;
      }
      var startPointLatLng = [startPoint["stop_lat"], startPoint["stop_lon"]];

      var latlngs = [
        startPointLatLng,
        endPointLatLng
      ];

      var polyline = L.polyline(latlngs, { color: 'blue', weight: 9 }).addTo(map);

      polyline.bindPopup("<b>trip type: " + endPoint["lastTripTypeOG"] + "   " + endPoint["lastTripIDOG"])
      endPointID = startPointID;

      var marker = L.circle([endPoint["stop_lat"], endPoint["stop_lon"]], {
        radius: 80
      }).addTo(map);
      count++;
      if (count > 2000) {
        break
      }
    }

    var queryURL2 = 'http://127.0.0.1:5555/1517430037_stops?where={"stop_id":"' + start_stop + '"}'
    console.log(queryURL2)
    $.get(queryURL2, function (rawstops) {
      stop = rawstops._items[0]
      // console.log(stops)
      var marker = L.circle([stop.stop_lat, stop.stop_lon], {
        radius: 100,
        stroke: 0,
        opacity: 1
      }).addTo(map);


    });

  })

})

// $('#stop-select').val('3RDMAIS').trigger('change');

$("#all-stop-button").click(function () {
  sampledStopsList = ['MOREASS', 'HIGCOON', '4TH15TN', 'TREZOLS', 'KARPAUN', 'LIVGRAE', 'GRESHEW', 'MAIOHIW', 'AGL540W', 'WHIJAEE', '3RDCAMW', 'HARZETS', 'MAIBRICE', 'SAI2NDS', '3RDMAIS', 'STYCHAS', 'LOC230N', 'BETDIEW', 'STEMCCS', 'INNWESE', 'HANMAIN', 'HIGINDN', '4THCHIN', 'RIDSOME', 'KARHUYN', 'LIVBURE', 'LONWINE', 'MAICHAW', 'BROHAMIW', 'WHI3RDE', '1STLINW', 'MAINOEW', 'MAIIDLE', '5THCLEE', '3RDTOWS', 'STYGAMS', 'KOE113W', 'TAM464S', 'CAS150S', 'BROOUTE', 'ALUGLENS', 'FRABREN', 'SOU340N', 'HILTINS', 'STRHOVE', 'SAWCOPN', 'HAMWORN', 'DALDUBN', 'MCNCHEN', 'HILBEAS', 'NOROWEN', 'SOUTER2A', 'GENSHAN', 'VACLINIC', 'MORHEATE', 'KOEEDSW1', 'TRAMCKW', 'FAISOUN', 'SAWSAWN', 'CLIHOLE', 'CHAMARN', 'CLE24THN']
  for (var i = 0; i < sampledStopsList.length; i++) {
    var startStopID = sampledStopsList[i]
    var queryURL = 'http://127.0.0.1:5555/1517430037_stops?where={"stop_id":"' + startStopID + '"}'
    console.log(queryURL)
    $.get(queryURL, function (rawstops) {
      stop = rawstops._items[0]
      // console.log(stops)
      var marker = L.circle([stop.stop_lat, stop.stop_lon], {
        radius: 1000,
        stroke: 0,
        opacity: 1
      }).addTo(map);


    });
  }

})

window.onload = function (e) {
  d3.text("idw_05_current.asc", function (asc) {
    var s = L.ScalarField.fromASCIIGrid(asc);
    var layer = L.canvasLayer.scalarField(s, {
      color: chroma.scale(['730000', 'e60000', 'e69800', 'fed37f', 'fefe00', 'ffffff', 'aaf596', '4ce600', '38a800', '145a00', '002673']).classes([0, 0.02, 0.05, 0.1, 0.2, 0.3, 0.7, 0.8, 0.9, 0.95, 0.98, 1]),
      opacity: 0.75
    }).addTo(mymap);
    layer.on('click', function (e) {
      if (e.value !== null) {
        let v = d3.format(".2f")(e.value.toFixed(4) * 100); let html = `<span class = "popupText" style="font-family:sans-serif"> <b>Percentile (5cm):</b> ${v}%</span>`;
        L.popup().setLatLng(e.latlng).setContent(html).openOn(mymap);
      };
    });
  });
}