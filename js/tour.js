/* Scroll-linked code tour for objective-z.org.
 *
 * The left column is the whole example file, split into groups. The right
 * column is the generated C, pinned, with the matching group lit up. An
 * IntersectionObserver watches a thin band across the middle of the viewport;
 * whichever left group crosses it becomes the active step.
 *
 * Progressive enhancement: this only activates above the two-column
 * breakpoint. Without it the markup is a plain listing with every caption
 * visible and nothing dimmed, which is also what a JS-off reader gets.
 *
 * No dependencies.
 */
(function () {
  "use strict";

  var WIDE = "(min-width: 62rem)";
  var REDUCED = "(prefers-reduced-motion: reduce)";

  var tour = document.getElementById("tour");
  if (!tour) {
    return;
  }

  var code = tour.querySelector(".tour-code");
  var out = tour.querySelector(".tour-out");
  var outPre = out && out.querySelector("pre");
  var fileLabel = document.getElementById("tour-file");
  if (!code || !out || !outPre) {
    return;
  }

  var leftGroups = [].slice.call(code.querySelectorAll(".g[data-step]"));
  var notes = [].slice.call(tour.querySelectorAll(".tour-note[data-step]"));
  if (!leftGroups.length) {
    return;
  }

  var wide = window.matchMedia(WIDE);
  var observer = null;
  var current = null;

  function setActive(step) {
    if (step === current) {
      return;
    }
    current = step;

    var mark = function (el) {
      var on = el.getAttribute("data-step") === step;
      el.classList.toggle("is-active", on);
      return on;
    };

    leftGroups.forEach(mark);
    notes.forEach(mark);

    var active = null;
    [].forEach.call(out.querySelectorAll(".g[data-step]"), function (el) {
      if (mark(el)) {
        active = el;
      }
    });

    if (!active) {
      return;
    }

    if (fileLabel) {
      fileLabel.textContent = active.getAttribute("data-file") || "";
    }

    /* Keep the lit region inside the panel's own scroll box. offsetTop is an
       absolute offset within the scroll container (the pre is positioned), so
       this stays correct even if a previous smooth scroll is still running --
       a delta from the live scroll position does not. */
    outPre.scrollTo({
      top: Math.max(0, active.offsetTop - 14),
      behavior: window.matchMedia(REDUCED).matches ? "auto" : "smooth"
    });
  }

  function enable() {
    if (observer) {
      return;
    }
    tour.setAttribute("data-tour", "on");

    /* Track everything currently crossing the band, not just what changed in
       this callback -- a batch containing only "left the band" entries would
       otherwise leave the previous step stuck on. */
    var inBand = [];

    observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        var i = inBand.indexOf(e.target);
        if (e.isIntersecting && i === -1) {
          inBand.push(e.target);
        } else if (!e.isIntersecting && i !== -1) {
          inBand.splice(i, 1);
        }
      });

      if (!inBand.length) {
        return;
      }

      /* Topmost group in the band wins, so scrolling down advances cleanly. */
      var hit = inBand.reduce(function (best, el) {
        return el.getBoundingClientRect().top < best.getBoundingClientRect().top
          ? el : best;
      });
      setActive(hit.getAttribute("data-step"));
    }, { rootMargin: "-45% 0px -50% 0px", threshold: 0 });

    leftGroups.forEach(function (g) { observer.observe(g); });
    setActive(leftGroups[0].getAttribute("data-step"));
  }

  function disable() {
    if (!observer) {
      return;
    }
    observer.disconnect();
    observer = null;
    tour.removeAttribute("data-tour");
    current = null;
    leftGroups.concat(notes, [].slice.call(out.querySelectorAll(".g")))
      .forEach(function (el) { el.classList.remove("is-active"); });
  }

  function sync() {
    if (wide.matches) {
      enable();
    } else {
      disable();
    }
  }

  sync();
  if (wide.addEventListener) {
    wide.addEventListener("change", sync);
  } else if (wide.addListener) {
    wide.addListener(sync);
  }
})();
