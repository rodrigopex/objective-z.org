# Where the code on the site comes from

`thermostat.m` is the Objective-C source shown on objective-z.org. Everything in
`generated/` is the transpiler's own output for that file — not written or edited
by hand. The site quotes these files verbatim; the only changes are whitespace
(tabs shown as four spaces, and one long function signature wrapped to fit the
code pane).

## Regenerating

From an objective-z checkout:

```sh
clang -Xclang -ast-dump=json -fsyntax-only \
      -fobjc-runtime=macosx -fobjc-arc -fblocks \
      -Iinclude/oz_sdk --target=arm64-apple-darwin \
      thermostat.m > thermostat.ast.json

PYTHONPATH=tools python3 -m oz_transpile \
      --input thermostat.ast.json \
      --sources thermostat.m \
      --outdir generated
```

Generated with objective-z v0.5.99.

## What each snippet on the site maps to

| Site pair | Source | Generated |
| --- | --- | --- |
| Hero — a property | `Thermometer` `@property`/`@synthesize` | `struct Thermometer`, `Thermometer_offset`, `Thermometer_setOffset_`, `Thermometer_read` |
| Message send → direct call | `-[Thermostat shouldHeat]` | `Thermostat_shouldHeat` |
| Protocol → const table | `@protocol Sensor` + two conformers | `OZ_PROTOCOL_RESOLVE_read` in `oz_dispatch.c` |
| ARC → inserted release | `Thermostat`'s strong `_probe` ivar, no `-dealloc` | `Thermostat_dealloc` |
| Slab alloc | `[[Thermometer alloc] init]` | `OZ_SLAB_DEFINE` + `Thermometer_alloc` in the header |
