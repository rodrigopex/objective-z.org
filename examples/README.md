# Where the code on the site comes from

`thermostat.m` is the Objective-C source shown on objective-z.org. Everything in
`generated/` is the transpiler's own output for that file — not written or edited
by hand. The site quotes these files; the only changes are whitespace (tabs shown
as four spaces, and a few long lines wrapped to fit the code panes).

Generated with objective-z v0.5.99.

## Regenerating

The example uses Zephyr headers (`zephyr/kernel.h`, `zephyr/zbus/zbus.h`), so the
AST dump needs a configured Zephyr build's generated headers — the same ones the
real build feeds Clang. From an objective-z checkout, with `$AUTOCONF` pointing at
a build's `zephyr/include/generated/zephyr/autoconf.h` and `$ZFLAGS` holding the
`-I`/`-D` set from that build's `compile_commands.json`:

```sh
clang -Xclang -ast-dump=json -fsyntax-only \
      -fobjc-runtime=macosx -fobjc-arc -fblocks \
      --target=arm64-apple-darwin $ZFLAGS -Iinclude/oz_sdk \
      -DCONFIG_ARM=1 -DCONFIG_ATOMIC_OPERATIONS_BUILTIN=1 \
      -include $AUTOCONF \
      thermostat.m > thermostat.ast.json

PYTHONPATH=tools python3 -m oz_transpile \
      --input thermostat.ast.json \
      --sources thermostat.m \
      --outdir generated
```

Clang reports a handful of errors from the Zephyr headers themselves plus a
`mach-o section specifier` complaint on `ZBUS_CHAN_DEFINE` — host Clang is
standing in for the ARM target, and the project's own `.clangd` suppresses the
same ELF-vs-Mach-O attribute noise. None of them touch the Objective-C
declarations, and none reach the generated output.

## What each snippet on the site maps to

| Site pair | Source | Generated |
| --- | --- | --- |
| Hero — properties | `@property (atomic) int setpoint` and `getter=isHeating` | `Thermostat_setpoint` / `Thermostat_setSetpoint_` wrapped in `OZ_SPINLOCK`, and `Thermostat_isHeating` |
| Block → static function | the `OZTimer` expiry block | `_oz_block_L0_C0`, passed by name to `OZTimer_initWithUserData_expiry_stop_` |
| Zephyr macros pass through | `ZBUS_CHAN_DEFINE`, `on_setpoint`, `ZBUS_LISTENER_DEFINE` | the same macros verbatim; only `[unit setSetpoint:…]` becomes `Thermostat_setSetpoint_(unit, …)` |
| Message send → direct call | `-[Thermostat shouldHeat]` | `Thermostat_shouldHeat` |
| Protocol → const table | `@protocol Sensor` + two conformers | `OZ_PROTOCOL_RESOLVE_read` in `oz_dispatch.c` |
| ARC → inserted release | two strong ivars, no `-dealloc` | `Thermostat_dealloc` |
| Slab alloc | `[[Thermostat alloc] init…]` | `OZ_SLAB_DEFINE` + `Thermostat_alloc` in the header |

## A note on blocks and C callbacks

A block cannot be used as a `ZBUS_LISTENER_DEFINE` callback. The macro builds a
file-scope struct whose `.callback` member is a function pointer, and a block
literal is a block object — Clang rejects it outright:

```
error: initializing 'void (*)(const struct zbus_channel *)' with an expression
       of incompatible type 'void (^)(const struct zbus_channel *)'
```

That is an Objective-C type rule, not a transpiler limitation. Blocks work where
an API takes a block (`OZTimer`, `OZDefer`); C APIs taking function pointers need
a function, which is why the listener above is a `static void` function that
sends a message to the object.
