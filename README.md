# objective-z.org

The website for [Objective-Z](https://github.com/rodrigopex/objective-z) — an
Objective-C to C transpiler for Zephyr RTOS.

Hand-written static HTML, CSS and JavaScript. No framework, no build step, no
dependencies, no third-party requests. GitHub Pages serves `main` at the site
root; pushing to `main` is the deploy.

```
index.html            the whole site — one page, anchor navigation
404.html              not-found page, same shell
css/main.css          design tokens, layout, components
js/theme.js           theme toggle + narrow-screen nav (the only script)
js/tour.js            scroll-linked code tour (activates above 62rem only)
tools/highlight.py    authoring tool: bakes syntax-highlight spans into the
                      markup (never runs in the browser)
tools/gen_tour.py     authoring tool: slices the tour's code groups out of
                      examples/ so both columns stay verbatim
tools/check_examples.py
                      verifies every code pane still matches the example
                      files (run after editing either)
examples/tour/        the demonstrated .m and its real generated C
assets/               Citrinio logo pair, social card (+ its SVG source)
favicon.svg
CNAME                 objective-z.org
.nojekyll             serve files as-is, no Jekyll processing
```

The page has one code section, and it is the whole demonstration: a complete
example file on the left, the transpiler's actual output pinned on the right. As
you scroll — or hover — the generated C highlights the matching lines while the
caption says what the construct became and what it buys. Long-form material (full
benchmark tables, the alternative-language evaluations, limitations) sits in
closed `<details>` blocks so the page stays short for a first-time reader.

It needs no framework: `position: sticky`, one `IntersectionObserver` and a
`pointermove` handler. With JS off or on a narrow screen it degrades to a plain
listing with every caption shown and nothing dimmed.

## Local preview

```sh
python3 -m http.server 8080
# http://localhost:8080
```

That is the whole toolchain. There is nothing to install and nothing to compile.

## Editing rules

See [CLAUDE.md](CLAUDE.md) for the full set. The three that matter most:

1. **No third-party origins.** No CDN, webfont, analytics or JS library. Every
   byte the browser loads comes from this repo.
2. **No inline `<style>`, `<script>` or `on*=` attributes.** The Content Security
   Policy carries no `'unsafe-inline'`, and it must stay that way.
3. **Benchmark numbers are copied by hand** from the transpiler repo's
   `README.md`. That file is the single source of truth — re-audit the tables
   here whenever the benchmarks change, and keep the measurement footnote
   (nRF52833 DK, Cortex-M4F @ 64 MHz, DWT cycle counter, `-O2`) next to them.

### Syntax highlighting

Code blocks are highlighted at authoring time, not in the browser:

```sh
python3 tools/highlight.py index.html          # new blocks
python3 tools/highlight.py --force index.html  # redo all blocks
```

The spans are committed. Nothing highlights at runtime, so there is no library
to load, nothing to mis-tokenize on someone else's machine, and the code is
still coloured with JavaScript disabled.

### Security posture

The CSP is delivered as a `<meta http-equiv>` tag because GitHub Pages cannot set
HTTP response headers. Known gap: `frame-ancestors`, `report-uri` and `sandbox`
are ignored in meta form, so clickjacking protection is not available on this
host. Everything else — `default-src 'none'`, no inline execution, no outbound
connections, no forms, no cookies, no user-supplied content anywhere — holds.

There is deliberately no CI: no GitHub Actions means no workflow tokens and no
pinned third-party actions in the deploy chain.

### Social card

`assets/og-card.svg` is the source; the committed PNG is rendered locally so the
asset never passes through an online converter:

```sh
rsvg-convert -w 1200 -h 630 assets/og-card.svg -o assets/og-card.png
```

## Paths

`index.html` uses **relative** asset paths (`css/main.css`, not `/css/main.css`).
They resolve correctly at the domain root and at a `github.io/<repo>/` project
path, so the site can be previewed either way without edits. Leave them relative.

`404.html` keeps absolute paths on purpose: it answers arbitrary URLs, where a
relative path would resolve below the site root.

## Deployment

Push to `main`. GitHub Pages is configured as *Deploy from a branch* → `main` → `/ (root)`.

### DNS setup

`objective-z.org` is the canonical domain. Apex records — and **only** these;
any extra A/AAAA/ALIAS record on the apex or extra CNAME on `www` will stop
Let's Encrypt from issuing the certificate:

| Type  | Name | Value |
| ----- | ---- | ----- |
| A     | `@`  | `185.199.108.153` |
| A     | `@`  | `185.199.109.153` |
| A     | `@`  | `185.199.110.153` |
| A     | `@`  | `185.199.111.153` |
| AAAA  | `@`  | `2606:50c0:8000::153` |
| AAAA  | `@`  | `2606:50c0:8001::153` |
| AAAA  | `@`  | `2606:50c0:8002::153` |
| AAAA  | `@`  | `2606:50c0:8003::153` |
| CNAME | `www` | `rodrigopex.github.io` |

If the zone has any CAA record, at least one must allow `letsencrypt.org`.

### Certificate gotcha, learned the hard way

GitHub runs its DNS check **at the moment you save the custom domain**, and it does
not retry. Save the domain before DNS resolves and the check fails silently: no
certificate is ever requested, `https_certificate` is simply absent from the Pages
API payload, and the site serves GitHub's `*.github.io` wildcard forever — which
browsers report as *Not Secure*.

The fix is to re-save the domain **after** DNS resolves: Settings → Pages →
Custom domain → clear the field → Save → re-enter → Save. Writing the same value
back via the API is a no-op and will not trigger the check; it has to be a real
change. Once the check passes, the certificate is issued within minutes and
GitHub enables Enforce HTTPS itself.

So the order is: set DNS first, confirm it resolves (`dig +short objective-z.org`),
*then* set the custom domain.

Once Pages reports *DNS check successful*, tick **Enforce HTTPS**. The
certificate has to be issued after both the apex and `www` resolve, or the apex
will not be covered by it.

### HTTPS scope

Enforce HTTPS is on, so `http://` 301-redirects to `https://`. Port 80 cannot be
closed — Pages keeps it open to serve that redirect. Pages sends **no HSTS header**
for custom domains and gives no way to add one, so a visitor's first plain-`http://`
request is still in cleartext before the redirect. Closing that would mean putting
a proxy in front of Pages; deliberately not done.

`objectivez.org` (no hyphen) can be held defensively and 301-redirected to the
canonical domain at the registrar. It cannot be done on GitHub — Pages accepts
only one custom domain per repository.

## License

Site content and code: Apache-2.0, matching the Objective-Z project.
