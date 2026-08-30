#!/usr/bin/env python3
"""Pre-highlight the <pre><code> blocks in the site's HTML.

The site ships no JavaScript highlighter and loads nothing from a CDN, so the
token spans are baked into the markup instead. Run this after editing a code
block; it is idempotent and skips any block that already carries spans.

    python3 tools/highlight.py index.html
    python3 tools/highlight.py --force index.html   # strip and redo every block

Token classes are styled in css/main.css under "syntax".
"""

import html
import re
import sys

C_KEYWORDS = {
    "auto", "break", "case", "char", "const", "continue", "default", "do",
    "double", "else", "enum", "extern", "float", "for", "goto", "if", "inline",
    "int", "long", "register", "restrict", "return", "short", "signed",
    "sizeof", "static", "struct", "switch", "typedef", "union", "unsigned",
    "void", "volatile", "while", "_Bool", "bool", "true", "false",
    # Objective-C property attributes and friends
    "nonatomic", "atomic", "strong", "weak", "copy", "assign", "readonly",
    "readwrite", "unsafe_unretained", "instancetype", "id", "self", "super",
    "nil", "YES", "NO",
}

TOKEN_RE = re.compile(
    r"""
      (?P<comment>/\*.*?\*/|//[^\n]*)
    | (?P<string>"(?:[^"\\\n]|\\.)*")
    | (?P<pp>\#[A-Za-z_]+)
    | (?P<directive>@[A-Za-z_][A-Za-z0-9_]*)
    | (?P<number>\b\d+(?:\.\d+)?[fFuUlL]*\b)
    | (?P<ident>[A-Za-z_][A-Za-z0-9_]*)
    """,
    re.VERBOSE | re.DOTALL,
)

BLOCK_RE = re.compile(r"(<pre><code>)(.*?)(</code></pre>)", re.DOTALL)
SPAN_RE = re.compile(r'</?span(?: class="(?:k|t|fn|c|s|pp|at|n)")?>')


def classify(name, rest):
    """Return a token class for an identifier, or None to leave it plain."""
    if name in C_KEYWORDS:
        return "k"
    if re.match(r"\s*\(", rest):
        return "fn"
    # Leading underscore means an ivar or struct member, not a type.
    if name[0].isupper():
        return "t"
    return None


def highlight(code):
    out = []
    pos = 0
    for m in TOKEN_RE.finditer(code):
        out.append(html.escape(code[pos:m.start()], quote=False))
        kind = m.lastgroup
        text = m.group()
        if kind == "ident":
            cls = classify(text, code[m.end():m.end() + 4])
        else:
            cls = {"comment": "c", "string": "s", "pp": "pp",
                   "directive": "at", "number": "n"}[kind]
        esc = html.escape(text, quote=False)
        out.append(f'<span class="{cls}">{esc}</span>' if cls else esc)
        pos = m.end()
    out.append(html.escape(code[pos:], quote=False))
    return "".join(out)


def process(path, force=False):
    src = open(path, encoding="utf-8").read()
    touched = skipped = 0

    def repl(m):
        nonlocal touched, skipped
        open_tag, body, close_tag = m.groups()
        if "<span" in body:
            if not force:
                skipped += 1
                return m.group()
            body = SPAN_RE.sub("", body)
        touched += 1
        return open_tag + highlight(html.unescape(body)) + close_tag

    out = BLOCK_RE.sub(repl, src)
    if out != src:
        open(path, "w", encoding="utf-8").write(out)
    print(f"{path}: {touched} block(s) highlighted, {skipped} already done")


if __name__ == "__main__":
    args = sys.argv[1:]
    force = "--force" in args
    targets = [a for a in args if not a.startswith("-")] or ["index.html"]
    for t in targets:
        process(t, force=force)
