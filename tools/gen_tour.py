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

# (step, objc range, caption, [(label, buffer, a, b), ...])
STEPS = [
 (1, (10, 16), "A Zephyr channel, declared in an Objective-C file. The macro is a C "
     "preprocessor construct that builds linker-section structures — and it comes "
     "out the other side byte for byte.",
  [("thermostat_ozm.c", OZM, 26, 32)]),

 (2, (18, 20), "A protocol first becomes a function-pointer type. Nothing is allocated "
     "and nothing is looked up yet.",
  [("oz_dispatch.h", DSH, 86, 86)]),

 (3, (22, 35), "The class becomes a struct whose first member is its superclass, so an "
     "upcast is a pointer cast. The method becomes a function taking <code>self</code> "
     "explicitly.",
  [("thermostat_ozh.h", OZH, 13, 17), ("thermostat_ozm.c", OZM, 40, 43)]),

 (4, (37, 50), "Now that two classes conform, the protocol gets a <code>const</code> "
     "table indexed by class id. It lives in <code>.rodata</code>, so it costs FLASH "
     "and no RAM at all.",
  [("oz_dispatch.c", DSC, 131, 134), ("thermostat_ozm.c", OZM, 57, 60)]),

 (5, (52, 70), "<code>atomic</code> wraps both accessors in a real Zephyr "
     "<code>k_spinlock</code> guard. <code>getter=isHeating</code> names the generated "
     "function; the setter keeps its conventional name.",
  [("thermostat_ozh.h", OZH, 91, 98), ("thermostat_ozm.c", OZM, 77, 96)]),

 (6, (72, 88), "The array literal becomes a stack buffer of retained objects. The "
     "expiry block is lifted out as a file-scope function and handed to the timer by "
     "name — which is why only non-capturing blocks are allowed. <code>__bridge</code> "
     "is just a cast.",
  [("thermostat_ozm.c", OZM, 71, 75), ("thermostat_ozm.c", OZM, 112, 119)]),

 (7, (90, 104), "Fast enumeration becomes an explicit iterator loop. Because "
     "<code>sensor</code> is <code>id</code>, the read goes through the protocol table "
     "— one indexed load, no message lookup. This is the polymorphic path.",
  [("thermostat_ozm.c", OZM, 126, 141), ("oz_dispatch.h", DSH, 175, 175)]),

 (8, (105, 112), "Nothing in this method mentions memory — and yet a release "
     "appears. ARC works out that <code>spare</code> dies at the closing brace and "
     "writes the call for you, before the return, at compile time. No collector, no "
     "runtime bookkeeping, and the exact instruction is right there to audit.",
  [("thermostat_ozm.c", OZM, 145, 151)]),

 (9, (113, 119), "Here the receiver type is known, so the send collapses to a direct "
     "call. And the <code>dealloc</code> you never wrote releases every strong ivar.",
  [("thermostat_ozm.c", OZM, 155, 158), ("thermostat_ozm.c", OZM, 160, 166)]),

 (10, (120, 130), "A plain C callback can talk to objects. Only the message send is "
     "rewritten; the listener macro and the function signature are untouched.",
  [("thermostat_ozm.c", OZM, 170, 178)]),
]

# Lines that exist only because the transpiler inserted them. Called out in the
# generated column with a label. Keyed by step; the text must match exactly.
EMPHASIS = {
 8: ("    OZObject_release((struct OZObject *)spare);", "added by the transpiler"),
}


def esc(s):
    return html.escape(s, quote=False)


def emphasise(step, text):
    """Wrap an inserted line in the callout span, escaping around it."""
    if step not in EMPHASIS:
        return esc(text)
    line, label = EMPHASIS[step]
    assert line in text, f"step {step}: emphasis line not found"
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
covered = []
left = []
for step, (a, b), _cap, _c in STEPS:
    covered.append((a, b))
for i, (step, (a, b), _cap, _c) in enumerate(STEPS):
    lo = 1 if i == 0 else covered[i - 1][1] + 1
    hi = b if i == len(STEPS) - 1 else covered[i + 1][0] - 1
    chunk = lines(SRC, lo, hi)
    left.append(f'<span class="g" data-step="{step}">{esc(chunk)}</span>')

# --- right column: generated C in tour order ---
right, notes = [], []
for step, _o, cap, blocks in STEPS:
    files = []
    body = []
    for label, buf, a, b in blocks:
        if label not in files:
            files.append(label)
        body.append(reflow(lines(buf, a, b)))
    right.append(
        f'<span class="g" data-step="{step}" data-file="{esc(" · ".join(files))}">'
        + emphasise(step, "\n\n".join(body)) + "</span>")
    notes.append(f'<p class="tour-note" data-step="{step}">'
                 f'<b>{step}.</b> {cap}</p>')

missing = [k for k, n in used.items() if n == 0]
assert not missing, "reflow patterns never matched:\n" + "\n".join(m[:70] for m in missing)

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
