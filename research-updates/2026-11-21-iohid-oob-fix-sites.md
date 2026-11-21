# IOHIDFamily out-of-bounds fix sites localised; entry mechanism not found

Date: 2026-11-21
Builds: iOS 27.0.1 kernelcache (build 24A446, target) and iOS 27.2 kernelcache (build 24B119, reference)
Member: `com.apple.iokit.IOHIDFamily`
Device activity: none. No authorised host enumerated a device, so nothing here is a runtime result.

## Background

An out-of-bounds read/write in this extension was already recorded from the
27.0.1-to-27.2 diff and mapped to CVE-2026-112507. The open question was reachability:
no sandbox-openable HID user client had been identified, so the path sat at a low
readiness level. This pass set out to pin the fix down exactly in the target build and
to find how the four changed routines are entered.

## Result: the fix is exactly four accessor routines

Cross-build function alignment flagged 296 candidate regions; a per-function shape
re-check reduced them to 12 real blocks. Exactly two of those carry the security-relevant
edit, and each contains two functions:

* Two routines that read an element from an array held in the object and copy it into
  the caller's record.
* Two routines that perform the same guarded copy plus an output-record write.

In the target build all four load an index, derive an offset into the array, and
dereference it **without comparing the index against the count field**. The newer build
inserts the same short sequence ahead of everything in each routine:

```
load  the count
compare the index against it
branch away on greater-or-equal
reload the array base
```

The second pair additionally gains a null check on the array base, which the target
build does not have.

A census over every function in both builds confirms this guard shape is new in the
newer build: zero occurrences of the load-count/compare/branch pattern in the target,
and only these routines plus pre-existing unrelated uses of the same field offset in the
newer one. So the set above is complete for this member.

## Reachability: not established, and weaker than before

Three independent scans were run, each with a positive control that reproduces a known
pointer slot:

* A word-level branch scan across the whole kernel image finds **no** direct call or
  tail-branch to any of the four routines.
* Whole-image pointer-reference scans for the encodings used by arm64e method tables,
  jump tables, chained fixups and literal pools find **no** reference to any of them.
* A slot-relative-delta scan also finds nothing.

For contrast, unchanged sibling routines in the same extension that share an identical
type tag constant *do* have small wrapper callers, found by the same scanner. The four
changed routines have none. They may be entered through a runtime-built dispatch that
these static scans do not cover, or they may be effectively unreachable; either way this
pass does not establish app reachability.

One inference is also recorded rather than proven: the index is loaded from a nested
sub-object, and no ingress path that sets it was traced, so "attacker-controlled index"
remains a description of the third-party diff note, not a result reproduced here.

A counting caveat: the two builds do not contain the same number of functions in this
member, so raw index pairing misaligns after the added function. All pairing above comes
from instruction-shape alignment, not from index arithmetic.

## Consequence

No out-of-bounds access, type confusion, lifetime error, kernel read/write primitive or
jailbreak is established, and readiness for this path is unchanged. The next step is to
find the entry mechanism — a runtime-built dispatch rather than a static table — before
any device time is spent here, and to reconcile against the earlier measured result that
every openable HID service refused every selector tried. Do not repeat a broad HID
selector sweep without a named owning class and a matching client type.
