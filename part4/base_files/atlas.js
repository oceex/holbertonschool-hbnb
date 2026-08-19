/* Decorative atlas for the index page, plus the restrained motion effects used
   across the site. No third-party libraries: the outline is a simplified
   Natural Earth polygon and everything else is plain SVG.

   scripts.js supplies the places, so each pin carries a real place id and
   leads to that place's detail page. */
(function () {
  "use strict";

  var reduce = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var SVGNS = "http://www.w3.org/2000/svg";
  var W = 600, H = 560;
  var BOUNDS = { minLng: 34.63, maxLng: 55.67, minLat: 16.34, maxLat: 32.17 };
  var number = new Intl.NumberFormat("en-SA", { maximumFractionDigits: 0 });

  /* Natural Earth 1:110m, simplified Saudi Arabia outline (public domain). */
  var COUNTRY = [
    [42.779,16.348],[42.650,16.775],[42.348,17.076],[42.271,17.475],[41.754,17.833],
    [41.221,18.672],[40.939,19.486],[40.248,20.175],[39.802,20.339],[39.139,21.292],
    [39.024,21.987],[39.066,22.580],[38.493,23.688],[38.024,24.079],[37.484,24.285],
    [37.155,24.858],[37.209,25.085],[36.932,25.603],[36.640,25.826],[36.249,26.570],
    [35.640,27.377],[35.130,28.063],[34.632,28.059],[34.788,28.607],[34.832,28.957],
    [34.956,29.357],[36.069,29.197],[36.501,29.505],[36.741,29.865],[37.504,30.004],
    [37.668,30.339],[37.999,30.509],[37.002,31.508],[39.005,32.010],[39.195,32.161],
    [40.400,31.890],[41.890,31.190],[44.709,29.179],[46.569,29.099],[47.460,29.003],
    [47.709,28.526],[48.416,28.552],[48.808,27.690],[49.300,27.461],[49.471,27.110],
    [50.152,26.690],[50.213,26.277],[50.113,25.944],[50.240,25.608],[50.527,25.328],
    [50.661,25.000],[50.810,24.755],[51.112,24.556],[51.390,24.627],[51.580,24.245],
    [51.618,24.014],[52.001,23.001],[55.007,22.497],[55.208,22.708],[55.667,22.000],
    [55.000,20.000],[52.000,19.000],[49.117,18.617],[48.183,18.167],[47.467,17.117],
    [47.000,16.950],[46.750,17.283],[46.367,17.233],[45.400,17.333],[45.217,17.433],
    [44.063,17.410],[43.792,17.320],[43.381,17.580],[43.116,17.088],[43.218,16.667]
  ];

  /* Each colour fills a pin behind a cream numeral, so all of them are dark
     enough to clear the 4.5:1 contrast minimum against that numeral. */
  var CULTURES = {
    "northwest": { short: "Northwest", color: "#9F5137" },
    "hejaz": { short: "Hejaz", color: "#30496A" },
    "asir": { short: "Asir", color: "#B94138" },
    "eastern": { short: "Eastern oasis", color: "#47705A" },
    "najd": { short: "Najd", color: "#98622E" },
    "south-coast": { short: "Southern coast", color: "#2D7780" },
    "atlas": { short: "Saudi atlas", color: "#B5562E" }
  };

  function el(tag, attrs, text) {
    var node = document.createElementNS(SVGNS, tag);
    if (attrs) Object.keys(attrs).forEach(function (key) { node.setAttribute(key, attrs[key]); });
    if (text != null) node.textContent = text;
    return node;
  }

  function project(coord) {
    var xPad = 48, yPad = 42;
    return [
      xPad + (coord[0] - BOUNDS.minLng) / (BOUNDS.maxLng - BOUNDS.minLng) * (W - xPad * 2),
      yPad + (BOUNDS.maxLat - coord[1]) / (BOUNDS.maxLat - BOUNDS.minLat) * (H - yPad * 2)
    ];
  }

  function pathFrom(coords, close) {
    return coords.map(function (coord, i) {
      var p = project(coord);
      return (i ? "L" : "M") + p[0].toFixed(1) + " " + p[1].toFixed(1);
    }).join(" ") + (close ? " Z" : "");
  }

  function cultureOf(place) {
    return place.heritage && place.heritage.key ? place.heritage.key : "atlas";
  }

  function drawDefinitions(svg, countryPath) {
    var defs = el("defs");
    var gradient = el("linearGradient", { id: "atlas-fill", x1: "0", y1: "0", x2: "1", y2: "1" });
    gradient.appendChild(el("stop", { offset: "0", "stop-color": "#EEE5CD" }));
    gradient.appendChild(el("stop", { offset: ".56", "stop-color": "#DCD3B8" }));
    gradient.appendChild(el("stop", { offset: "1", "stop-color": "#CDBF9C" }));
    defs.appendChild(gradient);

    var pattern = el("pattern", { id: "atlas-lattice", width: "18", height: "18", patternUnits: "userSpaceOnUse", patternTransform: "rotate(45)" });
    pattern.appendChild(el("path", { d: "M0 0V18 M9 0V18", class: "atlas-lattice-line" }));
    defs.appendChild(pattern);

    var clip = el("clipPath", { id: "ksa-clip" });
    clip.appendChild(el("path", { d: countryPath }));
    defs.appendChild(clip);
    svg.appendChild(defs);
  }

  function drawGrid(svg) {
    var grid = el("g", { class: "atlas-grid", "aria-hidden": "true" });
    [36,40,44,48,52].forEach(function (lng) {
      var a = project([lng, BOUNDS.minLat]), b = project([lng, BOUNDS.maxLat]);
      grid.appendChild(el("line", { x1: a[0], y1: a[1], x2: b[0], y2: b[1] }));
    });
    [18,22,26,30].forEach(function (lat) {
      var a = project([BOUNDS.minLng, lat]), b = project([BOUNDS.maxLng, lat]);
      grid.appendChild(el("line", { x1: a[0], y1: a[1], x2: b[0], y2: b[1] }));
    });
    svg.appendChild(grid);
  }

  function drawCompass(svg) {
    var group = el("g", { class: "atlas-compass", transform: "translate(516 88)", "aria-hidden": "true" });
    group.appendChild(el("circle", { r: "28" }));
    group.appendChild(el("path", { d: "M0 -23 L5 -4 L0 0 L-5 -4 Z M0 23 L4 5 L0 1 L-4 5 Z" }));
    group.appendChild(el("text", { x: "0", y: "-34" }, "N"));
    svg.appendChild(group);
  }

  function routePath(points) {
    if (!points.length) return "";
    var d = "M" + points[0][0].toFixed(1) + " " + points[0][1].toFixed(1);
    for (var i = 1; i < points.length; i++) {
      var prev = points[i - 1], next = points[i];
      var bend = i % 2 ? -18 : 18;
      var cx = (prev[0] + next[0]) / 2 + bend;
      var cy = (prev[1] + next[1]) / 2 - bend * 0.55;
      d += " Q" + cx.toFixed(1) + " " + cy.toFixed(1) + " " + next[0].toFixed(1) + " " + next[1].toFixed(1);
    }
    return d;
  }

  function renderRegionKey(places) {
    var root = document.getElementById("atlas-regions");
    if (!root) return;
    root.innerHTML = "";
    places.forEach(function (place) {
      var key = cultureOf(place), meta = CULTURES[key] || CULTURES.atlas;
      var button = document.createElement("button");
      button.type = "button";
      button.className = "atlas-region-key";
      button.dataset.id = place.id;
      button.dataset.name = place.name;
      button.dataset.culture = key;
      button.style.setProperty("--region-color", meta.color);
      button.setAttribute("aria-label", "Open " + place.name + ", " + place.location);
      button.innerHTML = '<span aria-hidden="true"></span>' + meta.short;
      button.addEventListener("click", function () {
        location.href = "place.html?id=" + encodeURIComponent(place.id);
      });
      root.appendChild(button);
    });
  }

  window.__hbnbMap = function (places) {
    var svg = document.getElementById("atlas-svg");
    var status = document.getElementById("map-status");
    if (!svg || svg.dataset.drawn) return;
    svg.dataset.drawn = "1";

    /* An empty catalogue is normal on a fresh database; a map with no pins
       would read as a failure instead. */
    if (!places.length) {
      if (status) status.textContent = "No stays to plot yet.";
      return;
    }

    var title = svg.querySelector("title") ? svg.querySelector("title").textContent : "Saudi stay atlas";
    var description = svg.querySelector("desc") ? svg.querySelector("desc").textContent : "Interactive map of stays";
    svg.innerHTML = "";
    svg.appendChild(el("title", { id: "atlas-title" }, title));
    svg.appendChild(el("desc", { id: "atlas-description" }, description));

    var countryPath = pathFrom(COUNTRY, true);
    drawDefinitions(svg, countryPath);
    drawGrid(svg);
    svg.appendChild(el("path", { d: countryPath, class: "atlas-land" }));
    svg.appendChild(el("path", { d: countryPath, class: "atlas-lattice", "clip-path": "url(#ksa-clip)" }));

    var points = places.map(function (place) {
      return project([place.coordinates.lng, place.coordinates.lat]);
    });
    svg.appendChild(el("path", { d: routePath(points), class: "atlas-route", "aria-hidden": "true" }));
    drawCompass(svg);

    var tooltip = document.getElementById("map-tooltip");
    var coordsOut = document.getElementById("map-coords");
    var mapFrame = svg.closest(".map-frame");
    var pinNodes = [];

    places.forEach(function (place, i) {
      var point = points[i], key = cultureOf(place), meta = CULTURES[key] || CULTURES.atlas;
      var group = el("g", {
        class: "atlas-pin",
        tabindex: "0",
        role: "button",
        "data-id": place.id,
        "data-name": place.name,
        "data-culture": key,
        "aria-label": place.name + ", " + place.location + ", SAR " + place.price + " per night",
        transform: "translate(" + point[0].toFixed(1) + " " + point[1].toFixed(1) + ")"
      });
      group.style.setProperty("--pin-color", meta.color);
      /* The visible dot is about 11px on screen, too small to click reliably.
         This invisible circle widens the target without changing the design. */
      group.appendChild(el("circle", { class: "atlas-pin-hit", r: "18" }));
      group.appendChild(el("circle", { class: "atlas-pin-ring", r: "8" }));
      group.appendChild(el("circle", { class: "atlas-pin-dot", r: "7" }));
      group.appendChild(el("text", { class: "atlas-pin-num", x: "0", y: "4" }, String(i + 1)));
      svg.appendChild(group);
      pinNodes.push(group);

      function show() {
        group.classList.add("active");
        if (mapFrame) mapFrame.dataset.culture = key;
        if (tooltip) {
          tooltip.innerHTML = "<strong>" + place.name + "</strong><br>" + place.location + " · SAR " + number.format(place.price) + "<small>" + (place.heritage ? place.heritage.motif : meta.short) + "</small>";
          tooltip.style.left = (point[0] / W * 100) + "%";
          tooltip.style.top = (point[1] / H * 100) + "%";
          tooltip.hidden = false;
        }
        if (coordsOut) coordsOut.textContent = place.coordinates.lat.toFixed(4) + "° N · " + place.coordinates.lng.toFixed(4) + "° E";
      }

      function hide() {
        group.classList.remove("active");
        if (mapFrame) delete mapFrame.dataset.culture;
        if (tooltip) tooltip.hidden = true;
        if (coordsOut) {
          coordsOut.textContent = places.length +
            (places.length === 1 ? " stay" : " stays") + " across the Kingdom";
        }
      }

      function go() {
        location.href = "place.html?id=" + encodeURIComponent(place.id);
      }

      group.addEventListener("mouseenter", show);
      group.addEventListener("mouseleave", hide);
      group.addEventListener("focus", show);
      group.addEventListener("blur", hide);
      group.addEventListener("click", go);
      group.addEventListener("keydown", function (event) {
        if (event.key === "Enter" || event.key === " ") { event.preventDefault(); go(); }
      });
    });

    /* Called by the price filter so the atlas dims the same stays the list
       hides, instead of contradicting it. */
    window.__hbnbMapFilter = function (visibleNames) {
      pinNodes.forEach(function (pin) {
        pin.classList.toggle("is-muted", visibleNames.indexOf(pin.dataset.name) === -1);
      });
      document.querySelectorAll(".atlas-region-key").forEach(function (key) {
        key.classList.toggle("is-muted", visibleNames.indexOf(key.dataset.name) === -1);
      });
    };

    renderRegionKey(places);
    if (status) status.hidden = true;

    if (!reduce) {
      var land = svg.querySelector(".atlas-land"), route = svg.querySelector(".atlas-route");
      [land, route].forEach(function (node, index) {
        var length = node.getTotalLength();
        node.style.strokeDasharray = index ? "5 7" : String(length);
        node.style.strokeDashoffset = String(length);
        requestAnimationFrame(function () { node.classList.add("is-drawn"); });
      });
      pinNodes.forEach(function (pin, index) {
        pin.style.setProperty("--pin-delay", (520 + index * 70) + "ms");
        pin.classList.add("is-entering");
      });
    }
  };

  function initTilt() {
    if (reduce || !window.matchMedia("(pointer: fine)").matches) return;
    document.querySelectorAll(".place-card").forEach(function (card) {
      if (card.__tilt) return;
      card.addEventListener("pointermove", function (event) {
        var rect = card.getBoundingClientRect();
        var x = (event.clientX - rect.left) / rect.width - 0.5;
        var y = (event.clientY - rect.top) / rect.height - 0.5;
        card.style.setProperty("--tilt-x", (-y * 2.6).toFixed(2) + "deg");
        card.style.setProperty("--tilt-y", (x * 3.2).toFixed(2) + "deg");
        card.style.setProperty("--pointer-x", ((x + 0.5) * 100).toFixed(1) + "%");
        card.style.setProperty("--pointer-y", ((y + 0.5) * 100).toFixed(1) + "%");
      });
      card.addEventListener("pointerleave", function () {
        card.style.removeProperty("--tilt-x");
        card.style.removeProperty("--tilt-y");
      });
      card.__tilt = true;
    });
  }

  function initReveal() {
    var targets = document.querySelectorAll(".place-card, .review-card, .place-highlight, .heritage-note");
    if (reduce || !("IntersectionObserver" in window)) {
      targets.forEach(function (target) { target.classList.add("is-in-view"); });
      return;
    }
    var observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        entry.target.classList.add("is-in-view");
        observer.unobserve(entry.target);
      });
    }, { threshold: 0.14, rootMargin: "0px 0px -6%" });
    targets.forEach(function (target, index) {
      if (target.__reveal) return;
      target.__reveal = true;
      target.style.setProperty("--reveal-delay", ((index % 3) * 55) + "ms");
      target.classList.add("motion-ready");
      observer.observe(target);
    });
  }

  function initSurfaceParallax() {
    if (reduce || !window.matchMedia("(pointer: fine)").matches) return;
    document.querySelectorAll(".form-visual, .place-image-window").forEach(function (surface) {
      if (surface.__parallax) return;
      var rect;
      surface.addEventListener("pointerenter", function () { rect = surface.getBoundingClientRect(); });
      surface.addEventListener("pointermove", function (event) {
        if (!rect) return;
        var x = ((event.clientX - rect.left) / rect.width - 0.5) * -10;
        var y = ((event.clientY - rect.top) / rect.height - 0.5) * -8;
        var xName = surface.classList.contains("form-visual") ? "--visual-x" : "--image-x";
        var yName = surface.classList.contains("form-visual") ? "--visual-y" : "--image-y";
        surface.style.setProperty(xName, x.toFixed(1) + "px");
        surface.style.setProperty(yName, y.toFixed(1) + "px");
      });
      surface.addEventListener("pointerleave", function () {
        surface.style.removeProperty("--visual-x");
        surface.style.removeProperty("--visual-y");
        surface.style.removeProperty("--image-x");
        surface.style.removeProperty("--image-y");
        rect = null;
      });
      surface.__parallax = true;
    });
  }

  function initHeaderMotion() {
    var header = document.querySelector(".site-header");
    if (!header || header.__motion) return;
    var queued = false;
    function update() {
      header.classList.toggle("is-scrolled", window.scrollY > 24);
      queued = false;
    }
    window.addEventListener("scroll", function () {
      if (queued) return;
      queued = true;
      requestAnimationFrame(update);
    }, { passive: true });
    update();
    header.__motion = true;
  }

  function initMotion() {
    initHeaderMotion();
    initSurfaceParallax();
    initReveal();
  }

  window.__hbnbTilt = initTilt;
  window.__hbnbReveal = initReveal;
  window.__hbnbMotion = initMotion;

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", initMotion);
  else initMotion();
})();
