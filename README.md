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
assets/               Citrinio logo pair, social card (+ its SVG source)
favicon.svg
CNAME                 objective-z.org
.nojekyll             serve files as-is, no Jekyll processing
```

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

Once Pages reports *DNS check successful*, tick **Enforce HTTPS**. The
certificate has to be issued after both the apex and `www` resolve, or the apex
will not be covered by it.

`objectivez.org` (no hyphen) is held defensively and 301-redirects to the
canonical domain at the registrar. It cannot be done on GitHub — Pages accepts
only one custom domain per repository.

## License

Site content and code: Apache-2.0, matching the Objective-Z project.
