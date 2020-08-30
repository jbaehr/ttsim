/**
 * This function has to be attached to a mouse event of the SVG's root element.
 */
function svg_click(evt) {
  var intersections = getElementsUnderCurser(evt);
  var xmlIdsOfFillPatterns = extractXmlIdsOfFillPatterns(intersections);

  var svg_root = evt.currentTarget;
  function getOidFromPatternElement(xmlIdOfPattern) {
    // Variant A: we have the OID in the SVG, in a didicated attribtue in "our" name space.
    var patternElement = svg_root.getElementById(xmlIdOfPattern);
    // WTF, HTML5 does not support name spaces! cf. https://developer.mozilla.org/en-US/docs/Web/API/Element/getAttributeNS
    //var tttNs = "http://tttool.entropia.de";
    //var oid = patternElement.getAttributeNS(tttNs, "oid");
    var oid = patternElement.getAttribute("ttt:oid");
    return oid;
  }

  function getOidFromXmlId(xmlId) {
    // Variant B: we extract the OID from the XML-ID, that has to follow a "known" pattern
    var start = xmlId.lastIndexOf("-")
    var oid = xmlId.slice(start + 1);
    return oid;
  }

  //var oids = xmlIdsOfFillPatterns.map(getOidFromPatternElement);
  var oids = xmlIdsOfFillPatterns.map(getOidFromXmlId);

  handle_clicked_oids(oids);
}

function getElementsUnderCurser(mouseEvent) {
  // I found the outline at http://dahlström.net/svg/interactivity/intersection/sandbox_hover.svg thanks a lot!
  // The current implementation has one severe flaw, though:
  // It finds the elements which *bounding box* (a rectangle) is under the curser. 
  // For "complex" shapes this also finds elements where the actual filled area is *not* hit.
  var svgRoot = mouseEvent.currentTarget;
  var clickedRect = svgRoot.createSVGRect();
  clickedRect.x = mouseEvent.clientX;
  clickedRect.y = mouseEvent.clientY;
  clickedRect.width = clickedRect.height = 1;
  var intersections = svgRoot.getIntersectionList(clickedRect, null);
  return intersections;
}

function extractXmlIdsOfFillPatterns(svgElements) {
  var xmlIdsOfFillPatterns = []
  for (let e of svgElements) {
    if (e.style.fill) {
      // parse the id from 'url("#some-id")'
      var regex = /url\(['"]?#([a-z_][a-z0-9._-]*)['"]?\)/i
      var match = regex.exec(e.style.fill);
      if (match) {
        var id = match[1];
        xmlIdsOfFillPatterns.push(id);
      }
    }
  }

  return xmlIdsOfFillPatterns;
}

function handle_clicked_oids(oids) {
  if (oids.length == 0) {
    alert("No OID clicked.");
  }
  else if (oids.length > 1) {
    alert("More then one OIDs clicked: " + oids);
  }
  else {
    alert("Clicked OID: " + oids[0]);
    send_play(oids[0]);
  }
}

function send_play(oid) {
  var xhttp = new XMLHttpRequest();
  xhttp.onreadystatechange = function() {
    if (this.readyState == 4 && this.status == 200) {
      handle_play_response(this.responseText);
    }
    else if (this.readyState == 4 && this.status >= 500 && this.status < 600) {
      alert("Something went wrong:\n" + this.responseText)
    }
  };
  xhttp.open("POST", "play", true);
  xhttp.setRequestHeader("Content-type", "text/plain");
  xhttp.setRequestHeader("Accept", "text/plain");
  var body = oid + "\n";
  //xhttp.setRequestHeader("Content-Length", body.Length);
  xhttp.send(body);
}

function handle_play_response(responseText) {
  alert(responseText);
}
