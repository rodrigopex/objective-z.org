/* Theme + nav for objective-z.org.
 *
 * Loaded synchronously in <head>: the stored theme is applied before first
 * paint, so there is no flash. Everything that touches the DOM below <head>
 * waits for DOMContentLoaded.
 *
 * No dependencies. Only storage key used: "oz-theme".
 */
(function () {
  "use strict";

  var KEY = "oz-theme";
  var ORDER = ["auto", "light", "dark"];
  var LABELS = { auto: "System", light: "Light", dark: "Dark" };
  var root = document.documentElement;

  function read() {
    try {
      var v = window.localStorage.getItem(KEY);
      return v === "light" || v === "dark" ? v : "auto";
    } catch (e) {
      /* Private mode, blocked site data — fall back to system. */
      return "auto";
    }
  }

  function write(mode) {
    try {
      if (mode === "auto") {
        window.localStorage.removeItem(KEY);
      } else {
        window.localStorage.setItem(KEY, mode);
      }
    } catch (e) {
      /* Not fatal: the theme still applies for this page view. */
    }
  }

  function apply(mode) {
    if (mode === "auto") {
      root.removeAttribute("data-theme");
    } else {
      root.setAttribute("data-theme", mode);
    }
  }

  /* Phase 1 — before paint. */
  var current = read();
  apply(current);

  /* Phase 2 — wire up controls. */
  function ready() {
    var btn = document.getElementById("theme-btn");
    if (btn) {
      var label = btn.querySelector(".theme-label");

      var sync = function () {
        if (label) {
          label.textContent = LABELS[current];
        }
        btn.setAttribute(
          "aria-label",
          "Color theme: " + LABELS[current] + ". Activate to change."
        );
      };

      btn.hidden = false;
      sync();

      btn.addEventListener("click", function () {
        current = ORDER[(ORDER.indexOf(current) + 1) % ORDER.length];
        apply(current);
        write(current);
        sync();
      });
    }

    var navBtn = document.getElementById("nav-btn");
    var nav = document.getElementById("nav");
    if (navBtn && nav) {
      var setOpen = function (open) {
        navBtn.setAttribute("aria-expanded", open ? "true" : "false");
      };

      navBtn.hidden = false;
      setOpen(false);

      navBtn.addEventListener("click", function () {
        setOpen(navBtn.getAttribute("aria-expanded") !== "true");
      });

      nav.addEventListener("click", function (event) {
        if (event.target.closest("a")) {
          setOpen(false);
        }
      });

      document.addEventListener("keydown", function (event) {
        if (event.key === "Escape") {
          setOpen(false);
        }
      });
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", ready);
  } else {
    ready();
  }
})();
