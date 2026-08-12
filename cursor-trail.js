(function () {
  'use strict';

  var canHover = window.matchMedia('(hover: hover) and (pointer: fine)');
  var reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
  if (!canHover.matches || reduceMotion.matches) return;

  var canvas = document.createElement('canvas');
  var ctx = canvas.getContext('2d');
  if (!ctx) return;

  canvas.setAttribute('aria-hidden', 'true');
  canvas.style.cssText = [
    'position:fixed',
    'inset:0',
    'width:100%',
    'height:100%',
    'pointer-events:none',
    'z-index:2147483646'
  ].join(';');
  document.body.appendChild(canvas);

  var points = [];
  var pointer = { x: 0, y: 0, visible: false };
  var frame = 0;
  var dpr = 1;
  var life = 720;
  var maxPoints = 64;

  function resize() {
    dpr = Math.min(window.devicePixelRatio || 1, 2);
    canvas.width = Math.round(window.innerWidth * dpr);
    canvas.height = Math.round(window.innerHeight * dpr);
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    ctx.lineCap = 'round';
    ctx.lineJoin = 'round';
  }

  function addPoint(x, y, time) {
    var previous = points[points.length - 1];
    if (previous) {
      var dx = x - previous.x;
      var dy = y - previous.y;
      var distance = Math.sqrt(dx * dx + dy * dy);
      var steps = Math.min(8, Math.floor(distance / 8));
      for (var i = 1; i < steps; i++) {
        var ratio = i / steps;
        points.push({
          x: previous.x + dx * ratio,
          y: previous.y + dy * ratio,
          born: time - (steps - i)
        });
      }
    }
    points.push({ x: x, y: y, born: time });
    if (points.length > maxPoints) points.splice(0, points.length - maxPoints);
  }

  function drawRibbon(now, glow) {
    if (points.length < 2) return;

    var newest = points[points.length - 1];
    var fade = Math.max(0, 1 - (now - newest.born) / life);
    if (!fade) return;

    var left = [];
    var right = [];
    var normalX = 0;
    var normalY = 1;

    for (var i = 0; i < points.length; i++) {
      var previous = points[Math.max(0, i - 1)];
      var next = points[Math.min(points.length - 1, i + 1)];
      var dx = next.x - previous.x;
      var dy = next.y - previous.y;
      var distance = Math.sqrt(dx * dx + dy * dy);
      if (distance > 0.01) {
        normalX = -dy / distance;
        normalY = dx / distance;
      }

      var progress = i / (points.length - 1);
      var growth = Math.pow(progress, 0.72);
      var halfWidth = glow
        ? 0.8 + 4.7 * growth
        : 0.18 + 2.15 * growth;
      left.push({
        x: points[i].x + normalX * halfWidth,
        y: points[i].y + normalY * halfWidth
      });
      right.push({
        x: points[i].x - normalX * halfWidth,
        y: points[i].y - normalY * halfWidth
      });
    }

    ctx.beginPath();
    ctx.moveTo(left[0].x, left[0].y);
    for (var j = 1; j < left.length - 1; j++) {
      ctx.quadraticCurveTo(
        left[j].x,
        left[j].y,
        (left[j].x + left[j + 1].x) / 2,
        (left[j].y + left[j + 1].y) / 2
      );
    }
    ctx.lineTo(left[left.length - 1].x, left[left.length - 1].y);
    ctx.lineTo(right[right.length - 1].x, right[right.length - 1].y);
    for (var k = right.length - 2; k > 0; k--) {
      ctx.quadraticCurveTo(
        right[k].x,
        right[k].y,
        (right[k].x + right[k - 1].x) / 2,
        (right[k].y + right[k - 1].y) / 2
      );
    }
    ctx.lineTo(right[0].x, right[0].y);
    ctx.closePath();

    var first = points[0];
    var gradient = ctx.createLinearGradient(first.x, first.y, newest.x, newest.y);
    if (glow) {
      gradient.addColorStop(0, 'rgba(112, 139, 105, 0)');
      gradient.addColorStop(0.3, 'rgba(112, 139, 105, ' + (0.04 * fade) + ')');
      gradient.addColorStop(0.65, 'rgba(91, 122, 83, ' + (0.1 * fade) + ')');
      gradient.addColorStop(1, 'rgba(73, 104, 68, ' + (0.17 * fade) + ')');
    } else {
      gradient.addColorStop(0, 'rgba(112, 139, 105, 0)');
      gradient.addColorStop(0.25, 'rgba(112, 139, 105, ' + (0.14 * fade) + ')');
      gradient.addColorStop(0.62, 'rgba(91, 122, 83, ' + (0.58 * fade) + ')');
      gradient.addColorStop(1, 'rgba(73, 104, 68, ' + (0.86 * fade) + ')');
    }
    ctx.fillStyle = gradient;
    ctx.fill();
  }

  function render(now) {
    frame = 0;
    ctx.clearRect(0, 0, window.innerWidth, window.innerHeight);

    points = points.filter(function (point) {
      return now - point.born < life;
    });

    drawRibbon(now, true);
    drawRibbon(now, false);

    if (points.length) requestFrame();
  }

  function requestFrame() {
    if (!frame) frame = requestAnimationFrame(render);
  }

  function clearTrail() {
    pointer.visible = false;
    requestFrame();
  }

  document.addEventListener('pointermove', function (event) {
    if (event.pointerType && event.pointerType !== 'mouse' && event.pointerType !== 'pen') return;
    pointer.x = event.clientX;
    pointer.y = event.clientY;
    pointer.visible = true;
    addPoint(pointer.x, pointer.y, performance.now());
    requestFrame();
  }, { passive: true });

  document.addEventListener('pointerleave', clearTrail);
  window.addEventListener('blur', clearTrail);
  window.addEventListener('resize', resize, { passive: true });
  reduceMotion.addEventListener('change', function (event) {
    canvas.style.display = event.matches ? 'none' : '';
    if (event.matches) {
      points = [];
      clearTrail();
    }
  });

  resize();
})();
