#!/usr/bin/env python3
"""Rebuild the hero's source/result split in index.html from examples/hero/.

Both panes are assembled from the real files: the left is hero.m verbatim, the
right is the struct, the slab pool, the accessors and main, in the same order the
source declares them. Long lines are reflowed (whitespace only) to fit the pane,
and the release ARC inserts is wrapped in the callout.

    python3 tools/gen_hero.py

Verify afterwards with tools/check_examples.py.
"""

import html
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
E = ROOT / "examples/hero"

SRC = (E / "hero.m").read_text().rstrip("\n")
OZH = (E / "generated/Thermostat_ozh.h").read_text().split("\n")
OZM = (E / "generated/Thermostat_ozm.c").read_text().split("\n")
MAIN = (E / "generated/hero_ozm.c").read_text().split("\n")

FILES = "Thermostat_ozh.h · Thermostat_ozm.c · hero_ozm.c"

# Line ranges, in the order the source declares things.
BLOCKS = [
    (OZH, 9, 13),     # struct Thermostat -- what @interface became
    (OZM, 5, 5),      # the slab pool its instances come from
    (OZM, 7, 14),     # atomic getter, with the spinlock guard
    (OZM, 21, 24),    # the custom-named getter
    (MAIN, 11, 20),   # main
]

REFLOW = {
"    struct Thermostat * unit = (struct Thermostat *)OZObject_init((struct OZObject *)Thermostat_alloc());":
"    struct Thermostat * unit = (struct Thermostat *)\n        OZObject_init((struct OZObject *)Thermostat_alloc());",
'    OZLog("setpoint=%d heating=%d", Thermostat_setpoint(unit), Thermostat_isHeating(unit));':
'    OZLog("setpoint=%d heating=%d",\n          Thermostat_setpoint(unit), Thermostat_isHeating(unit));',
"OZ_SLAB_DEFINE(oz_slab_Thermostat, sizeof(struct Thermostat), 1, 4);":
"OZ_SLAB_DEFINE(oz_slab_Thermostat,\n               sizeof(struct Thermostat), 1, 4);",
}

RELEASE = "    OZObject_release((struct OZObject *)unit);"
LABEL = "added by the transpiler"

esc = lambda s: html.escape(s, quote=False)


def build():
    parts = []
    for buf, a, b in BLOCKS:
        parts.append("\n".join(l.replace("\t", "    ") for l in buf[a - 1:b]))
    gen = "\n\n".join(parts)

    for old, new in REFLOW.items():
        assert old in gen, f"reflow pattern missing: {old[:60]}"
        gen = gen.replace(old, new)

    assert RELEASE in gen, "release line not found"
    head, _, tail = gen.partition(RELEASE)
    return (esc(head) + '<span class="add">' + esc(RELEASE)
            + f'<b class="add-tag">{esc(LABEL)}</b></span>' + esc(tail))


def splice(page, gen_html):
    i = page.index('<section class="hero">')
    a = page.index('    <div class="split">', i)
    b = page.index('    <p class="hero-note">', a)
    split = f'''    <div class="split">
      <div class="pane">
        <p class="pane-head"><span>hero.m</span> <span class="pane-tag">you write</span></p>
<pre><code>{esc(SRC)}</code></pre>
      </div>
      <div class="pane">
        <p class="pane-head"><span>generated C</span> <span class="pane-tag pane-file">{FILES}</span></p>
<pre><code>{gen_html}</code></pre>
      </div>
    </div>

'''
    return page[:a] + split + page[b:]


def main():
    page_path = ROOT / "index.html"
    page = page_path.read_text()
    page_path.write_text(splice(page, build()))

    widest = max(len(l) for l in re.sub(r"<[^>]+>", "", build()).split("\n"))
    print(f"hero rebuilt — generated pane longest line {widest} chars")
    print("now run: python3 tools/highlight.py --force index.html")
    return 0


if __name__ == "__main__":
    sys.exit(main())
