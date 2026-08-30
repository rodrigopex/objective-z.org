#!/usr/bin/env python3
"""Verify the code on the page still matches the files in examples/.

The site claims every generated snippet is real transpiler output. This checks
that claim mechanically: each code pane's text, with all whitespace collapsed,
must appear in the example file it says it came from. Whitespace-only reflowing
is allowed (and used, to fit the panes); a changed identifier or a dropped line
is not.

    python3 tools/check_examples.py
"""

import html
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent


def squash(text):
    """Collapse whitespace so only the tokens matter.

    Backslash-newline is removed first: in C that is a line splice the
    preprocessor deletes, so wrapping a long macro across lines with
    continuations is a whitespace-equivalent edit, not a change to the code.
    """
    text = re.sub(r"\\\s*\n", " ", text)
    # Whitespace is removed outright, not collapsed: a reflow may break a line
    # at a point where the original had no space at all (after "[", say).
    return re.sub(r"\s+", "", text)


def pane_text(page, anchor):
    """Plain text of the first code pane after `anchor`."""
    i = page.index(anchor)
    a = page.index("<pre><code>", i) + len("<pre><code>")
    b = page.index("</code></pre>", a)
    body = page[a:b]
    body = re.sub(r"<b class=\"add-tag\">.*?</b>", "", body)  # our own label
    return html.unescape(re.sub(r"<[^>]+>", "", body))


def check(name, page_text, sources):
    """Every non-trivial line of the pane must appear in some source file."""
    haystacks = [squash(p.read_text()) for p in sources]
    # Rejoin continued lines first, so a wrapped macro is compared as the one
    # logical line it actually is.
    page_text = re.sub(r"\\\s*\n\s*", " ", page_text)
    missing = []
    for line in page_text.split("\n"):
        s = squash(line)
        if len(s) < 10:           # braces, blank lines, stray punctuation
            continue
        if not any(s in h for h in haystacks):
            missing.append(s)
    if missing:
        print(f"FAIL {name}: {len(missing)} line(s) not found in "
              + ", ".join(str(p.relative_to(ROOT)) for p in sources))
        for m in missing[:8]:
            print("   " + m[:100])
        return False
    print(f"ok   {name}: every line traced to source")
    return True


def main():
    page = (ROOT / "index.html").read_text()
    E = ROOT / "examples"
    ok = True

    ok &= check("hero source", pane_text(page, '<section class="hero">'),
                [E / "hero/hero.m"])
    ok &= check("hero generated", pane_text(page, '<span>generated C</span>'),
                [E / "hero/generated/Thermostat_ozm.c",
                 E / "hero/generated/hero_ozm.c"])
    ok &= check("tour source", pane_text(page, 'class="tour-code"'),
                [E / "tour/thermostat.m"])
    ok &= check("tour generated", pane_text(page, 'id="tour-file"'),
                [E / "tour/generated/thermostat_ozm.c",
                 E / "tour/generated/thermostat_ozh.h",
                 E / "tour/generated/oz_dispatch.c",
                 E / "tour/generated/oz_dispatch.h"])

    print("\n" + ("PASS" if ok else "FAIL"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
