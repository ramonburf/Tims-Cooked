# IOHIDFamily region-A element producer found — index provenance closed

Static analysis, iOS 27.0.1 (24A446) against iOS 27.2 (24B119). No device probe was run;
no app-carried trigger, kernel read/write primitive, exploit or jailbreak is claimed.

## What was open

An earlier note localised the HID extension's newer bounds check to four accessor routines
and then found the routine that writes the count field the check tests. It left one
question open: **who writes the elements of descriptor region A**, whose `+8` field is the
index the check compares against that count? Without the producer, it was impossible to say
whether a malformed report descriptor can drive the index past the count, or whether the
comparison is an invariant of construction.

## Result

The producer is the HID **Collection** handler (main item tag `0xa`), reached from the
extension's main-item dispatcher. It appends a region-A element at
`base + count*0x28`, increments the region-A count, and fills the new element as follows:

- `element[+8]`  ← a parser cursor held in the per-parse context (`ctx+0x50`)
- `element[+0xc]` ← `count_D - ctx+0x50`, the complementary remainder
- then `ctx+0x50` ← the current region-D entry count

Tracing that cursor closes the question:

- it is zeroed once per parse, when the parse context is initialised;
- the item reader that decodes each report-descriptor item never writes it;
- its only non-zero writer is the Collection handler itself, storing the **current**
  region-D count;
- the region-D count is append-only on the parse path — the layout pass zeroes it and the
  value-appending handlers only increment it. No decrement site was found.

Therefore the index stored in a region-A element is always **less than or equal to the final
region-D count**. It equals the final count exactly when a Collection item is processed after
the last value-appending (local) item and no further values follow.

The 24B119 counterpart of the Collection handler is instruction-identical to the 24A446 one,
so the parser still stores the unclamped cursor; the newly added accessor guard is the only
change. Sibling main-item handlers were checked and do not write the cursor.

## What the fix therefore closes

Only the `index == count` case — an off-by-one. In 27.0.1 the accessor loads from
`D_base + index*0x14 + 8`; with `index == count` that address sits just past the region-D
array. The six descriptor regions are carved contiguously out of a single allocation
(`A | B | C | D | E | F | trailer`), so the read normally lands inside the same allocation
(in the following region or the trailing area) and leaves the allocation only when every
later region is empty.

Classification: a **bounded, mostly intra-allocation out-of-bounds read**, fixed upstream by
the `index < count` guard. The earlier "attacker picks an arbitrary index" reading is
refuted; there is no unbounded index, no write, no type confusion, and no primitive. The
finding stays scoped to the device-attach report-descriptor path: the only user client that
reaches the element-hierarchy builder belongs to the virtual-HID service and carries an
entitlement predicate, and no sandboxed-app ingress has been established. Readiness for this
path is unchanged, and no device work was attempted.

## Reproduction / evidence (local, not published)

Target build: `firmware/24A446/kernelcache.release.macho`, member
`com.apple.iokit.IOHIDFamily`. The Collection handler was identified by censusing every store
to the descriptor count slots across the member, then tracing the cursor field's writers; the
24B119 counterpart was located by an exact instruction-sequence match. Local evidence
(disassembly, both builds' handler bodies, the count-store census) is retained outside this
repository.
