/* ============================================================
   CUSTOM GLOWING CURSOR — Dark Slide Template
   Add <script src="cursor-effect.js"></script> before </body>
   ============================================================ */

(function () {
  "use strict";

  /* ── Config — tweak these values to taste ─────────────────── */
  const CONFIG = {
    trailCount: 12,          // number of trail dots per move
    trailSpawnInterval: 2,   // spawn a trail dot every N mousemove events
    trailMinSize: 3,         // minimum trail dot diameter (px)
    trailMaxSize: 8,         // maximum trail dot diameter (px)
    trailColors: [           // cycle through these colors for the tail
      "rgba(255, 255, 255, 0.8)",
      "rgba(180, 220, 255, 0.7)",
      "rgba(120, 180, 255, 0.6)",
      "rgba(80,  150, 255, 0.4)",
      "rgba(60,  120, 255, 0.2)",
    ],
    hoverSelectors: "a, button, label, input, select, textarea, [role='button'], [tabindex]",
  };

  /* ── Create the main cursor dot ───────────────────────────── */
  const dot = document.createElement("div");
  dot.id = "cursor-dot";
  document.body.appendChild(dot);

  /* ── State ─────────────────────────────────────────────────── */
  let mouseX = -100;
  let mouseY = -100;
  let moveCounter = 0;
  let colorIndex = 0;
  let rafId = null;

  /* ── Smooth dot position via rAF ───────────────────────────── */
  function moveDot() {
    dot.style.left = mouseX + "px";
    dot.style.top  = mouseY + "px";
    rafId = requestAnimationFrame(moveDot);
  }
  rafId = requestAnimationFrame(moveDot);

  /* ── Spawn a single trail particle ─────────────────────────── */
  function spawnTrail(x, y) {
    const particle = document.createElement("div");
    particle.className = "cursor-trail";

    const size = CONFIG.trailMinSize +
      Math.random() * (CONFIG.trailMaxSize - CONFIG.trailMinSize);
    const color = CONFIG.trailColors[colorIndex % CONFIG.trailColors.length];
    colorIndex++;

    particle.style.cssText = `
      left: ${x}px;
      top: ${y}px;
      width: ${size}px;
      height: ${size}px;
      background: ${color};
      box-shadow: 0 0 ${size * 2}px ${color};
    `;

    document.body.appendChild(particle);

    /* Remove after animation ends */
    particle.addEventListener("animationend", () => particle.remove(), { once: true });
  }

  /* ── Track mouse movement ───────────────────────────────────── */
  document.addEventListener("mousemove", function (e) {
    mouseX = e.clientX;
    mouseY = e.clientY;
    document.body.classList.remove("cursor-hidden");

    moveCounter++;
    if (moveCounter % CONFIG.trailSpawnInterval === 0) {
      spawnTrail(mouseX, mouseY);
    }
  });

  /* ── Hide cursor when mouse leaves window ───────────────────── */
  document.addEventListener("mouseleave", function () {
    document.body.classList.add("cursor-hidden");
  });

  document.addEventListener("mouseenter", function () {
    document.body.classList.remove("cursor-hidden");
  });

  /* ── Grow cursor on hover over interactive elements ─────────── */
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

  /* ── Respect reduced-motion preference ─────────────────────── */
  const prefersReduced = window.matchMedia("(prefers-reduced-motion: reduce)");
  if (prefersReduced.matches) {
    cancelAnimationFrame(rafId);
    dot.remove();
    document.querySelectorAll("*, *::before, *::after").forEach(el => {
      el.style.cursor = "";
    });
  }

})();
