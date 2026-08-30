# objective-z.org

Static website for the [Objective-Z](https://github.com/rodrigopex/objective-z) project
(Objective-C -> C transpiler for Zephyr RTOS).

Public repo `rodrigopex/objective-z.org`. GitHub Pages serves `main` at `/` (root).
No build step: what is committed is what is served.

## Hard rules

Do not break these. They are the reason the site exists in this shape.

1. **No third-party origins, ever.** No CDN, webfont, analytics, icon set, or JS
   library. System font stacks only. Every byte the browser fetches comes from
   this repo. Verify: `grep -rnE 'https?://' index.html 404.html css js` -- every
   hit must be an outbound `<a>` or a meta URL, never a fetched asset.
2. **No inline `<style>`, `<script>`, or `on*=` attributes.** The CSP has no
   `'unsafe-inline'` and must stay that way. All CSS in `css/`, all JS in `js/`.
3. **No build step, no GitHub Actions.** Nothing in the deploy chain but git push.
4. **Every outbound link** carries `rel="noopener noreferrer"`.
5. **Every `<table>` is wrapped** in `.table-scroll` (with `tabindex="0"`). The
   page body must never scroll horizontally -- the benchmark tables are wide.
6. **Theme tokens:** full light palette on bare `:root`. Dark overrides declared
   twice -- under `@media (prefers-color-scheme: dark)` guarded by
   `:root:not([data-theme="light"])`, and under `:root[data-theme="dark"]` -- so
   the manual toggle wins in both directions. Never give a color its only
   definition inside a media query or attribute block.

## Content

The page is **code-first**: a source/result split hero, then one pair per language
feature, then results. Long-form detail belongs in a closed `<details>` block or
on GitHub -- not in body copy. If a section grows past a short paragraph, that is
a signal to collapse it or link out.

Every line of generated C shown on the site is **real transpiler output**, kept in
`examples/` with the command that produced it. Never hand-write or "clean up" the
generated side of a pair -- regenerate it. Whitespace-only reflowing to fit the
code pane is fine; changing an identifier or dropping a line is not.

### Syntax highlighting

Token `<span>`s inside `<pre><code>` are **baked into the markup** by
`tools/highlight.py`. There is no runtime highlighter and no CDN library -- a
CSP with `script-src 'self'` and the no-third-party rule both forbid one.

After editing any code block:

```sh
python3 tools/highlight.py index.html            # new blocks only
python3 tools/highlight.py --force index.html     # strip and redo every block
```

Never hand-edit a token span. Token classes (`.k .t .fn .c .s .n .at .pp`) are
scoped to `pre code` in the stylesheet because they are short enough to collide
with layout classes otherwise.

Benchmark numbers are **copied by hand, not generated**. Single source of truth:
`README.md` in `rodrigopex/objective-z`. When OZ benchmarks change, re-audit every
table here against it.

Always keep the measurement footnote with the numbers: nRF52833 DK (ARM Cortex-M4F
@ 64 MHz), DWT cycle counter, `-O2`, overhead-calibrated, single inheritance.

Keep the "Where C++ still wins" panel honest and current. Showing the losses is
what makes the wins credible to embedded engineers.

## Brand

- Slate `#2C3D4F` -- ink and dark-theme surface base.
- Citrus `#D3CC4F` -- accent only: rules, stat highlights, focus rings, hover
  underlines. Never body-link text; it fails contrast on light backgrounds.

Citrinio logo is **unlinked**, theme-swapped pair in `assets/citrinio-{light,dark}.svg`.
Upstream source: `~/Cloud/Companies/Citrinio/assets/citrinio_white.svg` (325x89, tight
bounds, transparent). The dark variant is that same file with `#2C3D4F` recolored to
`#E8EEF4`, citrus accent untouched -- identical geometry in both themes, so toggling
causes no layout shift. Regenerate with:

```sh
sed 's/fill="#2C3D4F"/fill="#E8EEF4"/g' assets/citrinio-light.svg > assets/citrinio-dark.svg
```

The `citrinio_blue.svg` upstream variant is deliberately NOT used: it bakes in a
`#2C3D4F` background plate that would show as a box on a dark page.

## Local preview

```sh
python3 -m http.server 8080
```

## Deploy

Push to `main`. Nothing else.
