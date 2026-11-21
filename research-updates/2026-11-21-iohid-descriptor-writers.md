# IOHIDFamily descriptor writers — provenance of the bounded count field

Static analysis, 2026-11-21. Target build 24A446 (iOS 27.0.1); reference build 24B119
(iOS 27.2). No device probe was run; no device or build host was reachable.

This note continues the HID fix-site work. An earlier pass localised four accessor routines
in the HID kernel extension that gained an index bound in the newer build, and established
that the index is read from a descriptor-derived element and used to address an array whose
count lives at offset `+0x40` of the descriptor object. The open question was whether that
count — and the index compared against it — can be driven apart by a malformed report
descriptor. This pass traces who writes them.

## Descriptor layout

The layout pass computes six concatenated regions and stores base/count pairs in the
descriptor object:

| region | base | count | entry stride |
|---|---|---|---|
| A | `+0x8` | `+0x10` | `0x28` |
| B | `+0x18` | `+0x20` | `0x68` |
| C | `+0x28` | `+0x30` | `0x10` |
| D | `+0x38` | `+0x40` | `0x14` |
| E | `+0x48` | `+0x50` | `0x10` |
| F | `+0x58` | `+0x60` | `0x10` |

The two live accessors walk region A elements and use a value stored in each element as an
index into region D (`base + index*0x14 + 8`). The newer build's guard compares that index
against the region-D count `[obj+0x40]` before the load.

## Who writes the count field

The count `[obj+0x40]` is written non-zero only by three append sequences inside one
item-tag handler (the routine the descriptor parser dispatches each parsed item to). Each
sequence has the same shape: load the region-D base, load the count, compute
`entry = base + count*0x14`, store the entry fields, then increment the count and store it
back. The count therefore equals exactly the number of region-D entries that path created.
Elsewhere in the extension the field is only zeroed, by the layout pass and by the parser's
re-initialisation step. Sibling tag handlers append to other regions and never store this
field; their similarly-numbered stores address an entry field of a different region, not the
descriptor count.

The value the newer build's guard protects — region-D entry `+8` — is written by those same
append sequences from the parsed item's scalar value, so both the count and the addressed
entry fields are produced together, per item.

## Region-A producer: not found

The index compared against the count lives in a region-A element. Two scans looked for its
producer:

* a whole-extension scan for an append signature (one base register carrying both the
  `+0x8` base load and the `+0x10` count load/store, plus a `0x28` stride immediate) returns
  no function;
* a census of every function that carries the descriptor type tag `" hid"` lists all
  accesses to offsets `0x8 / 0x10 / 0x38 / 0x40`; none of them stores to the descriptor's own
  count fields. The similarly-shaped serialiser routines do write `+0x40`, but to caller
  output records rather than to the descriptor.

So region A and its count are filled by code outside the routines that carry the descriptor
type tag, and that producer was not identified in this pass.

## Bounds

Established: the bound field's provenance (append-only, incremented in lockstep with region-D
creation), and that the guarded load reads a field written by the same append sequences.

Not established: the region-A element producer, and therefore whether any input can make a
region-A index reach or exceed the number of region-D entries. The "attacker-controlled
index" reading is neither reproduced nor refuted.

Consequence: the earlier finding stays unpromoted and remains scoped to the device-attach
path. No out-of-bounds access, type confusion, lifetime error, kernel read/write primitive,
exploit or jailbreak is established, and no device probe was run.
