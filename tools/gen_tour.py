import html, pathlib, re, sys

BASE = pathlib.Path(sys.argv[1])
SRC = (BASE / "thermostat.m").read_text().split("\n")
OZM = (BASE / "final/thermostat_ozm.c").read_text().split("\n")
OZH = (BASE / "final/thermostat_ozh.h").read_text().split("\n")
DSC = (BASE / "final/Foundation/oz_dispatch.c").read_text().split("\n")
DSH = (BASE / "final/Foundation/oz_dispatch.h").read_text().split("\n")

def lines(buf, a, b):
    """1-indexed inclusive slice, tabs to four spaces."""
    return "\n".join(l.replace("\t", "    ") for l in buf[a - 1:b])

# Whitespace-only reflows so nothing overflows a code pane. Each key must
# appear exactly once in the assembled listing, or we abort.
REFLOW = {
"    struct Thermometer * probe = (struct Thermometer *)OZObject_init((struct OZObject *)Thermometer_alloc());":
"""    struct Thermometer * probe = (struct Thermometer *)
        OZObject_init((struct OZObject *)Thermometer_alloc());""",

"    unit = Thermostat_initWithProbe_pollEvery_(Thermostat_alloc(), probe, 1000);":
"""    unit = Thermostat_initWithProbe_pollEvery_(
        Thermostat_alloc(), probe, 1000);""",

'    OZLog("worst=%d heating=%d", Thermostat_worstReading(unit), Thermostat_isHeating(unit));':
"""    OZLog("worst=%d heating=%d",
          Thermostat_worstReading(unit), Thermostat_isHeating(unit));""",

"    struct Thermometer * spare = (struct Thermometer *)OZObject_init((struct OZObject *)Thermometer_alloc());":
"""    struct Thermometer * spare = (struct Thermometer *)
        OZObject_init((struct OZObject *)Thermometer_alloc());""",

"    struct Thermostat * me = (struct Thermostat *)k_timer_user_data_get(t);":
"    struct Thermostat * me =\n        (struct Thermostat *)k_timer_user_data_get(t);",

"    struct OZObject *_oz_arr_0_buf[] = {(struct OZObject *)OZObject_retain((struct OZObject *)(struct OZObject *)probe), (struct OZObject *)OZObject_retain((struct OZObject *)(struct OZObject *)(struct Hygrometer *)OZObject_init((struct OZObject *)Hygrometer_alloc()))};":
"""    struct OZObject *_oz_arr_0_buf[] = {
        (struct OZObject *)OZObject_retain(
            (struct OZObject *)(struct OZObject *)probe),
        (struct OZObject *)OZObject_retain(
            (struct OZObject *)(struct OZObject *)
            (struct Hygrometer *)OZObject_init(
                (struct OZObject *)Hygrometer_alloc()))};""",

"    struct OZArray *_oz_recv1 = OZArray_initWithItems(_oz_arr_0_buf, 2);":
"    struct OZArray *_oz_recv1 =\n        OZArray_initWithItems(_oz_arr_0_buf, 2);",

"    struct OZTimer *_oz_recv2 = OZTimer_initWithUserData_expiry_stop_(OZTimer_alloc(), (struct OZObject *)self, _oz_block_L0_C0, (((void *)0)));":
"""    struct OZTimer *_oz_recv2 =
        OZTimer_initWithUserData_expiry_stop_(
            OZTimer_alloc(), (struct OZObject *)self,
            _oz_block_L0_C0, (((void *)0)));""",

"    OZTimer_startAfter_period_(self->_poll, periodMs, periodMs);":
"    OZTimer_startAfter_period_(self->_poll,\n                               periodMs, periodMs);",

"        struct OZObject *_oz_iter0 = (struct OZObject *)OZ_PROTOCOL_SEND_iter((struct OZObject *)self->_bank);":
"""        struct OZObject *_oz_iter0 = (struct OZObject *)
            OZ_PROTOCOL_SEND_iter((struct OZObject *)self->_bank);""",

"        for (const  id sensor = (const  id)OZ_PROTOCOL_SEND_next(_oz_recv1); sensor != ((void *)0); sensor = (const  id)OZ_PROTOCOL_SEND_next(_oz_recv1)) {":
"""        for (const  id sensor =
                 (const  id)OZ_PROTOCOL_SEND_next(_oz_recv1);
             sensor != ((void *)0);
             sensor = (const  id)OZ_PROTOCOL_SEND_next(_oz_recv1)) {""",

"#define OZ_PROTOCOL_SEND_read(obj) OZ_PROTOCOL_RESOLVE_read[((struct OZObject *)(obj))->_meta.class_id]((struct OZObject *)(obj))":
"""#define OZ_PROTOCOL_SEND_read(obj)                       \\
    OZ_PROTOCOL_RESOLVE_read[                            \\
        ((struct OZObject *)(obj))->_meta.class_id](     \\
            (struct OZObject *)(obj))""",

"ZBUS_CHAN_DEFINE(chan_setpoint, struct msg_setpoint, NULL, NULL,":
"ZBUS_CHAN_DEFINE(chan_setpoint, struct msg_setpoint,\n                 NULL, NULL,",
"                 ZBUS_OBSERVERS(lis_setpoint), ZBUS_MSG_INIT(0));":
"                 ZBUS_OBSERVERS(lis_setpoint),\n                 ZBUS_MSG_INIT(0));",
}

# (step, objc range, caption, [(label, buffer, a, b[, callout label]), ...])
STEPS = [
 (1, (10, 12), "A protocol becomes a function-pointer type. Nothing is allocated and "
     "nothing is registered at startup — the abstraction costs you a typedef.",
  [("oz_dispatch.h", DSH, 86, 86)]),

 (2, (14, 27), "The class becomes a struct whose first member is its superclass, so an "
     "upcast is a pointer cast. The method becomes a function taking <code>self</code> "
     "explicitly, and a send to a known type costs <strong>12 cycles</strong> — exactly "
     "what the C call costs.",
  [("thermostat_ozh.h", OZH, 13, 16), ("thermostat_ozm.c", OZM, 33, 36)]),

 (3, (29, 42), "With two classes conforming, the protocol needs a table. It is "
     "<code>const</code>, so it lands in <code>.rodata</code> — FLASH, not RAM. "
     "Polymorphism for <strong>zero bytes of RAM</strong>.",
  [("oz_dispatch.c", DSC, 131, 134), ("thermostat_ozm.c", OZM, 50, 53)]),

 (4, (44, 63), "<code>atomic</code> wraps both accessors in a real Zephyr "
     "<code>k_spinlock</code> guard — <strong>10 cycles</strong> to read, two fewer than "
     "the C++ equivalent, because it is the kernel's own primitive and not a library "
     "mutex. <code>getter=isHeating</code> names the function; the setter keeps its "
     "conventional name.",
  [("thermostat_ozh.h", OZH, 92, 99), ("thermostat_ozm.c", OZM, 70, 89)]),

 (5, (65, 80), "An array literal becomes a stack buffer of retained objects. The block "
     "is lifted out as a file-scope function and handed to the timer by name — which is "
     "why only non-capturing blocks are allowed, and why invoking one costs the same "
     "<strong>12 cycles</strong> as a C++ lambda. <code>__bridge</code> is just a cast.",
  [("thermostat_ozm.c", OZM, 64, 68), ("thermostat_ozm.c", OZM, 105, 112)]),

 (6, (82, 95), "Fast enumeration becomes an explicit iterator loop. Because "
     "<code>sensor</code> is <code>id</code>, the read goes through the protocol table: "
     "one indexed load, <strong>21 cycles</strong>, with no message lookup and no "
     "dispatch cache to miss.",
  [("thermostat_ozm.c", OZM, 119, 136), ("oz_dispatch.h", DSH, 175, 175)]),

 (7, (97, 103), "Nothing in this method mentions memory — and yet a release appears. "
     "ARC works out that <code>spare</code> dies at the closing brace and writes the "
     "call, before the return, at compile time. No collector, no runtime bookkeeping, "
     "and <strong>zero heap</strong>: the pool above is a fixed slab in "
     "<code>.bss</code>, sized from the AST, with no allocator header per object.",
  [("thermostat_ozm.c", OZM, 14, 14), ("thermostat_ozm.c", OZM, 138, 144)]),

 (8, (105, 110), "A known receiver collapses to a direct call. Below it is a whole "
     "function that appears in no source file: the class declares no "
     "<code>-dealloc</code>, so ARC wrote one, releasing each strong ivar in turn before "
     "handing off to the superclass.",
  [("thermostat_ozm.c", OZM, 148, 151),
   ("thermostat_ozm.c", OZM, 153, 159, "added by the transpiler")]),

 (9, (112, 130), "This is the part no other language gets for free. "
     "<code>ZBUS_CHAN_DEFINE</code> and <code>ZBUS_LISTENER_DEFINE</code> are C "
     "preprocessor macros that build linker-section structures; here they sit in a "
     "<code>.m</code> file and come out untouched. <strong>Zero bindings</strong> to "
     "write, and none to fix when Zephyr changes. A plain C callback talks to the "
     "object — only the message send is rewritten.",
  [("thermostat_ozm.c", OZM, 163, 178)]),

 (10, (132, 141), "And it runs. Every message is an ordinary call, ARC releases the "
      "local probe on the way out, and the whole file goes through the same GCC as the "
      "rest of your firmware — no second compiler, and <strong>28% smaller</strong> "
      "than the equivalent built as C++.",
  [("thermostat_ozm.c", OZM, 179, 187)]),
]

# Lines that exist only because the transpiler inserted them. Called out in the
# generated column with a label. Keyed by step; the text must match exactly.
EMPHASIS = {
 7: ("    OZObject_release((struct OZObject *)spare);", "added by the transpiler"),
 10: ("    OZObject_release((struct OZObject *)probe);", "added by the transpiler"),
}


def esc(s):
    return html.escape(s, quote=False)


def callout(text, label):
    """Wrap a whole block in the callout, tagging its first line."""
    first, sep, rest = text.partition("\n")
    return ('<span class="add">' + esc(first)
            + f'<b class="add-tag">{esc(label)}</b>'
            + esc(sep + rest) + "</span>")


# Counts how many blocks each EMPHASIS entry actually matched, checked at the end
# so a stale line fails loudly rather than silently rendering unmarked.
emphasis_hits = {step: 0 for step in EMPHASIS}


def emphasise(step, text):
    """Wrap an inserted line in the callout, if this block contains it.

    A step may have several blocks and the line lives in only one of them, so a
    miss here is normal; the tally is verified after every step is built.
    """
    if step not in EMPHASIS:
        return esc(text)
    line, label = EMPHASIS[step]
    if line not in text:
        return esc(text)
    emphasis_hits[step] += 1
    head, _, tail = text.partition(line)
    return (esc(head)
            + '<span class="add">' + esc(line)
            + f'<b class="add-tag">{esc(label)}</b></span>'
            + esc(tail))

used = {k: 0 for k in REFLOW}

def reflow(text):
    for old, new in REFLOW.items():
        if old in text:
            used[old] += text.count(old)
            text = text.replace(old, new)
    return text

# --- left column: the whole file, grouped ---
# Each step names the lines it is about; the blank/comment lines between two
# steps go to the later one. Ranges must tile the file exactly -- no gaps, no
# overlaps, or the listing silently duplicates or drops a line.
covered = [rng for _s, rng, _cap, _c in STEPS]
left = []
for i, (step, (a, b), _cap, _c) in enumerate(STEPS):
    lo = 1 if i == 0 else covered[i - 1][1] + 1
    hi = len(SRC) if i == len(STEPS) - 1 else covered[i][1]
    assert lo <= hi, f"step {step}: empty range {lo}..{hi}"
    chunk = lines(SRC, lo, hi)
    left.append(f'<span class="g" data-step="{step}">{esc(chunk)}</span>')
    if i:
        prev_hi = covered[i - 1][1]
        assert lo == prev_hi + 1, f"step {step}: range does not follow the previous"

rendered = sum(len(html.unescape(re.sub(r"<[^>]+>", "", g)).split("\n")) for g in left)
assert rendered == len(SRC), (
    f"left column renders {rendered} lines but the file has {len(SRC)}")

# --- right column: generated C in tour order ---
right, notes = [], []
for step, _o, cap, blocks in STEPS:
    files = []
    body = []
    for block in blocks:
        # 4-tuple: plain block. 5-tuple: the whole block is transpiler-inserted,
        # so it gets the callout with the given label.
        label, buf, a, b = block[:4]
        note = block[4] if len(block) > 4 else None
        if label not in files:
            files.append(label)
        text = reflow(lines(buf, a, b))
        body.append(callout(text, note) if note else emphasise(step, text))
    right.append(
        f'<span class="g" data-step="{step}" data-file="{esc(" · ".join(files))}">'
        + "\n\n".join(body) + "</span>")
    notes.append(f'<p class="tour-note" data-step="{step}">'
                 f'<b>{step}.</b> {cap}</p>')

missing = [k for k, n in used.items() if n == 0]
assert not missing, "reflow patterns never matched:\n" + "\n".join(m[:70] for m in missing)

bad = {s: n for s, n in emphasis_hits.items() if n != 1}
assert not bad, f"emphasis lines matched the wrong number of blocks: {bad}"

# width check
for name, col in (("left", left), ("right", right)):
    worst = max((len(l) for blk in col for l in html.unescape(re.sub(r"<[^>]+>", "", blk)).split("\n")), default=0)
    print(f"{name}: longest line {worst} chars")

out = pathlib.Path(sys.argv[2])
out.write_text(
    "<!-- LEFT -->\n" + "\n".join(left) +
    "\n<!-- NOTES -->\n" + "\n".join(notes) +
    "\n<!-- RIGHT -->\n" + "\n".join(right) + "\n")
print("wrote", out, f"({len(STEPS)} steps)")
