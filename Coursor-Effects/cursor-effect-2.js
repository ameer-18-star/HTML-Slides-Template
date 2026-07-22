/* ============================================================
   CUSTOM GLOWING CURSOR v2 — Dark Slide Template
   Features: Glowing dot + trailing tail + particle burst on click
   Add <script src="cursor-v2.js"></script> before </body>
   ============================================================ */

(function () {
  "use strict";

  /* ── Config — tweak these freely ───────────────────────────── */
  const CONFIG = {

    /* Trail settings */
    trailSpawnInterval : 2,       // spawn trail dot every N mousemove events
    trailMinSize       : 3,       // px
    trailMaxSize       : 8,       // px
    trailDuration      : 550,     // ms — must match CSS animation duration
    trailColors: [
      "rgba(255, 255, 255, 0.85)",
      "rgba(180, 220, 255, 0.70)",
      "rgba(120, 180, 255, 0.55)",
      "rgba(80,  150, 255, 0.35)",
      "rgba(60,  120, 255, 0.18)",
    ],

    /* Click burst settings */
    burstParticleCount : 18,      // number of particles per click
    burstMinSize       : 4,       // px
    burstMaxSize       : 10,      // px
    burstMinDistance   : 45,      // px — how far particles travel (min)
    burstMaxDistance   : 110,     // px — how far particles travel (max)
    burstDuration      : 600,     // ms — lifetime of each burst particle
    burstColors: [
      "#ffffff",
      "#c8e6ff",
      "#90c8ff",
      "#5aaaff",
      "#3d8bff",
      "#ffdd88",   // occasional warm flash for contrast
      "#ff8c6b",
    ],

    /* Hover selector */
    hoverSelectors: "a, button, label, input, select, textarea, [role='button'], [tabindex]",
  };

  /* ── Reduced-motion guard ───────────────────────────────────── */
  if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;

  /* ── Create the main cursor dot ────────────────────────────── */
  const dot = document.createElement("div");
  dot.id = "cursor-dot";
  document.body.appendChild(dot);

  /* ── State ──────────────────────────────────────────────────── */
  let mouseX      = -200;
  let mouseY      = -200;
  let moveCounter = 0;
  let trailColorIdx = 0;

  /* ── Smooth dot position via rAF ───────────────────────────── */
  (function loop() {
    dot.style.left = mouseX + "px";
    dot.style.top  = mouseY + "px";
    requestAnimationFrame(loop);
  })();

  /* ── Helpers ────────────────────────────────────────────────── */
  function rand(min, max) {
    return min + Math.random() * (max - min);
  }

  function pickFrom(arr) {
    return arr[Math.floor(Math.random() * arr.length)];
  }

  /* ── Spawn a single trail particle ─────────────────────────── */
  function spawnTrail(x, y) {
    const p = document.createElement("div");
    p.className = "cursor-trail";

    const size  = rand(CONFIG.trailMinSize, CONFIG.trailMaxSize);
    const color = CONFIG.trailColors[trailColorIdx % CONFIG.trailColors.length];
    trailColorIdx++;

    p.style.cssText = `
      left: ${x}px;
      top: ${y}px;
      width: ${size}px;
      height: ${size}px;
      background: ${color};
      box-shadow: 0 0 ${size * 2}px ${color};
    `;

    document.body.appendChild(p);
    setTimeout(() => p.remove(), CONFIG.trailDuration + 50);
  }

  /* ── Spawn particle burst on click ─────────────────────────── */
  function spawnBurst(x, y) {
    for (let i = 0; i < CONFIG.burstParticleCount; i++) {

      const p = document.createElement("div");
      p.className = "click-particle";

      const size     = rand(CONFIG.burstMinSize, CONFIG.burstMaxSize);
      const color    = pickFrom(CONFIG.burstColors);
      const angle    = (360 / CONFIG.burstParticleCount) * i + rand(-10, 10);
      const distance = rand(CONFIG.burstMinDistance, CONFIG.burstMaxDistance);
      const rad      = (angle * Math.PI) / 180;
      const tx       = Math.cos(rad) * distance;
      const ty       = Math.sin(rad) * distance;
      const duration = rand(CONFIG.burstDuration * 0.6, CONFIG.burstDuration);
      const delay    = rand(0, 60);

      p.style.cssText = `
        left: ${x}px;
        top: ${y}px;
        width: ${size}px;
        height: ${size}px;
        background: ${color};
        box-shadow: 0 0 ${size + 4}px ${color};
      `;

      document.body.appendChild(p);

      /* Animate with the Web Animations API */
      p.animate(
        [
          {
            transform : "translate(-50%, -50%) scale(1)",
            opacity   : 1,
          },
          {
            transform : `translate(calc(-50% + ${tx}px), calc(-50% + ${ty}px)) scale(0.15)`,
            opacity   : 0,
          },
        ],
        {
          duration : duration,
          delay    : delay,
          easing   : "cubic-bezier(0.25, 0.46, 0.45, 0.94)",
          fill     : "forwards",
        }
      ).finished.then(() => p.remove());
    }
  }

  /* ── Mouse move — update position + trail ───────────────────── */
  document.addEventListener("mousemove", function (e) {
    mouseX = e.clientX;
    mouseY = e.clientY;
    document.body.classList.remove("cursor-hidden");

    moveCounter++;
    if (moveCounter % CONFIG.trailSpawnInterval === 0) {
      spawnTrail(mouseX, mouseY);
    }
  });

  /* ── Mouse click — burst ────────────────────────────────────── */
  document.addEventListener("mousedown", function (e) {
    document.body.classList.add("cursor-clicking");
    spawnBurst(e.clientX, e.clientY);
  });

  document.addEventListener("mouseup", function () {
    document.body.classList.remove("cursor-clicking");
  });

  /* ── Hide / show cursor when leaving / entering window ──────── */
  document.addEventListener("mouseleave", function () {
    document.body.classList.add("cursor-hidden");
  });

  document.addEventListener("mouseenter", function () {
    document.body.classList.remove("cursor-hidden");
  });

  /* ── Grow cursor on interactive elements ────────────────────── */
  document.addEventListener("mouseover", function (e) {
    if (e.target.closest(CONFIG.hoverSelectors)) {
      document.body.classList.add("cursor-hover");
    }
  });

  document.addEventListener("mouseout", function (e) {
    if (e.target.closest(CONFIG.hoverSelectors)) {
      document.body.classList.remove("cursor-hover");
    }
  });

})();
