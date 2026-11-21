# Six more changed kernel extensions audited — bounded negatives, plus one 27.2 size clamp with unresolved ownership

Date: 2026-11-21
Builds: iOS 27.0.1 kernelcache (build 24A446, target) and iOS 27.2 kernelcache (build 24B119, reference)
Scope: six members of the equal-function-count subset that had not yet been examined
Device activity: none. No authorised host enumerated a device, so nothing here is a runtime result.

## Background

The cross-build census ranks changed kernel extensions by an index-paired count of
functions whose instruction fingerprint differs. That count is only a ranking hint: when a
member's data segment moves between builds, address literals inside untouched code change
too, and compiler register allocation alone can make unrelated functions look rewritten.
Every member below was therefore re-checked with a per-function shape comparison that
masks immediates and displacements before any region is called a real edit.

## Results

| extension | funcs (target/newer) | flagged regions | drift / real |
|---|---|---|---|
| IOMobileGraphicsFamily-DCP | 800 / 800 | 96 | 85 / 11 |
| AppleInputDeviceSupport | 878 / 878 | 88 | 84 / 4 |
| DiskImages.UDIFDiskImage | 191 / 191 | 34 | 26 / 8 |
| IOBiometricFamily | 509 / 509 | 79 | 64 / 15 |
| AppleAVD | 2328 / 2328 | 317 | 314 / 3 |
| AppleTypeCPhy | 253 / 253 | 25 | 22 / 3 |

As with earlier members, the large nominal counts reduce to address/data-segment drift
plus a handful of genuine edits. No member in this batch carries an ordinary-app-reachable
memory-safety change.

## The one clean fix-shaped change

In the display-co-processor extension, one virtual-method trampoline gained a guard in the
newer build that the target lacks entirely. Both builds load the object's method table,
authenticate it, load a fixed slot and tail-call it; the newer build first compares the
call's size argument against a small constant and returns a bad-argument status for larger
values instead of dispatching. This is a deliberate input-size clamp, not compiler drift.

Its ownership is **not established**, and that limits the finding:

* The routine is a method-table entry in a contiguous authenticated-pointer table, so the
  change is on a real dispatch path.
* A whole-image pointer-slot search did not decode this member's relocated entry (a
  positive control reproduced a known slot), so the entry was confirmed at the byte level
  rather than by the scanner.
* The extension publishes **no** IOKit personalities at all, and its own class-name strings
  name the application-processor framebuffer driver, whose method table is a different
  table from the one holding the changed entry. The owner class of the changed table was
  not identified.

Reconnaissance only: no user-client class, factory route or app ingress is established,
and no vulnerability, out-of-bounds access or primitive is claimed.

## Other real edits recorded as reconnaissance

* **AppleInputDeviceSupport** — four routines rework a length/offset computation. The
  target computes an end-minus-start difference and adds a carry value on underflow; the
  newer build compares both fields against a stored limit first and, when both exceed it,
  takes a new branch calling a helper with a different operation code and both fields.
  Two sibling routines gain the same compare-and-conditionally-reject idiom. Reads as a
  bounds/overflow-hardening rework. The extension publishes no personalities.
* **AppleAVD** — the decode-command builder gains a call to a helper followed by a
  conditional rejection, ahead of work the target performs unconditionally. The other two
  regions are branch-offset and register-allocation artifacts.
* **DiskImages.UDIFDiskImage** — two identical range-check wrappers replace a test that
  required both operands' high halves to be zero with one that accepts a slightly smaller
  maximum on the first operand while keeping the second's high half at zero, a small
  tightening near the 32-bit boundary; another routine gains an unconditional trap. Larger
  refactors sit in the same member. It publishes disk-image decoding services and no
  user-client class.
* **IOBiometricFamily** — the fifteen differing pairs are register renames, branch-offset
  changes and removal of a repeated global-select idiom. A separate static audit of the
  same extension reached the same conclusion from the source side. No bounds, length or
  lifetime predicate was seen to change.
* **AppleTypeCPhy** — a structure field moved by eight bytes plus drift.

## Assessment

No out-of-bounds access, type confusion, lifetime error, kernel read/write primitive or
jailbreak is established. These members should not be reopened without a newly published
user-client class, a new factory route, or a concrete changed bound or length check tied
to an app-callable entry point. Device work remains blocked because no authorised host
currently enumerates a device.
