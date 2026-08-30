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
`examples/` with the command that produced it. The hero comes from
`examples/hero/hero.m` (class plus a `main` that uses it); the tour comes from
`examples/tour/thermostat.m`.

Run **`python3 tools/check_examples.py`** after touching either the page or the
examples. It asserts every code pane still traces to its source file, comparing
with whitespace removed and C line splices rejoined, so a reflow passes but a
renamed identifier or a dropped line fails.

The two examples sit in separate directories because the tour emits
`thermostat_ozm.c` and the hero emits `Thermostat_ozm.c` -- the same path on a
case-insensitive filesystem. Do not flatten them back together. Never hand-write or "clean up" the
generated side of a pair -- regenerate it. Whitespace-only reflowing to fit the
code pane is fine; changing an identifier or dropping a line is not.

### The code tour

**There is exactly one code section on the page.** The `#translate` section is a
scroll-linked walkthrough and it carries the whole demonstration: the left column
is the whole example file split into groups, the right column is the generated C
pinned in place with the matching region lit. Do not add a second code pair
elsewhere -- if a point needs code, it belongs in a tour step.

Captions are where the argument gets made. Each one says what the construct
became **and** what that buys, quoting the measured figure where there is one
("12 cycles", "zero bytes of RAM"). Numbers must come from the benchmark tables,
not from intuition. Both sides are **generated** by
`tools/gen_tour.py`, which slices exact line ranges out of `examples/` --

```sh
python3 tools/gen_tour.py <dir-with-thermostat.m-and-final/> /tmp/frag.html
```

-- and then the fragment is spliced into `index.html`. Do not hand-edit the
`<span class="g" data-step="N">` groups or the line content inside them; change
the STEPS table in the generator and re-slice. The generator asserts that every
whitespace reflow it applies actually matched, so a stale line range fails loudly
instead of silently emitting the wrong code.

Code the transpiler inserted gets the `.add` callout with an `.add-tag` label.
Two ways to ask for it in `tools/gen_tour.py`:

- one line inside a block -> add it to the `EMPHASIS` map, keyed by step;
- a whole block -> give that block's spec a fifth element, the label, e.g.
  `("thermostat_ozm.c", OZM, 160, 166, "added by the transpiler")`. The tag lands
  on the block's first line.

Use it only for code with no counterpart in the source -- an injected release, or
a whole function like `dealloc` that the author never wrote -- never for an
ordinary translation.

Left group N, caption N and right group N must always exist as a set. The step
numbers are the only contract between the markup and `js/tour.js`.

The step ranges must **tile the source file exactly** -- the generator asserts
that the left column renders the same number of lines the file has, because an
off-by-one silently duplicates a line at every group boundary.

Pointer and scroll both drive it, arbitrated by whichever the reader used last:
`pointermove` over a group takes control, and any scroll hands it straight back.
It has to be `pointermove`, not `pointerover` -- a cursor left resting over the
column would otherwise hijack the highlight as content slid underneath it.

`js/tour.js` activates only above `62rem` and only by setting
`data-tour="on"`; every interactive CSS rule is gated on both. With JS off or on
a narrow screen the tour is a plain listing with all captions shown and nothing
dimmed. Keep it that way.

**Splicing gotcha:** the hero pane and the tour pane are both labelled
`thermostat.m`. Anchoring a replacement on that string alone hits the hero
first. Anchor on `class="tour-code"` / `<section class="hero">` instead.

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

The highlighter passes existing markup through, so the tour's `class="g"`
wrappers survive both a highlight and a `--force` re-highlight. Only token spans
are stripped and rebuilt.

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

## Paths

`index.html` uses **relative** asset paths so it works both at a domain root and
at the `github.io/objective-z.org/` project path it is served from until the
domain is registered. Do not make them absolute again.

`404.html` keeps absolute paths on purpose — it answers arbitrary URLs, where
relative paths would resolve below the site root.

`CNAME` holds `objective-z.org`. Pages rewrites this file from the Settings
field, so change the domain there, not here.

## Local preview

```sh
python3 -m http.server 8080
```

## Deploy

Push to `main`. Nothing else.
