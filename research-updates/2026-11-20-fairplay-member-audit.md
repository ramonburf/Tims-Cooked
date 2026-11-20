# Second-largest unexamined changed kernel extension retires as recompilation noise (bounded negative)

Date: 2026-11-20
Builds: iOS 27.0.1 kernelcache (build 24A446, target) and iOS 27.2 kernelcache (build 24B119, reference)
Scope: `com.apple.driver.FairPlayIOKit`
Device activity: none. No authorised host enumerated a device, so nothing here is a runtime result.

## Background

The cross-build census ranks changed kernel extensions by an index-paired count of
functions whose instruction fingerprint differs. That count is only a ranking hint: when a
member's data segment moves between builds, address literals inside untouched code change
too, and when a member contains obfuscated code with per-build baked constants, recompiling
it changes instructions without changing logic. This checkpoint examined the largest
remaining un-audited member in the equal-function-count subset, whose nominal count was
**69** changed functions — the second-highest nominal figure after the already-audited SCSI
architecture-model extension.

## Result

Both builds contain **479** functions in this member. The alignment pass flags 46 replace
regions; a per-function shape re-check reduces them to **39 regions of
address/data-segment drift and 7 real blocks**, covering 73 of the 479 functions. So roughly
three quarters of the nominal count is recompilation noise rather than changed logic.

## What the seven real blocks are

Every real block lies in one contiguous high region of the extension. That region is not
ordinary driver code: its function bodies load large baked 64-bit constants, combine them
with XOR / multiply / multiply-add, index into tables of code pointers, and end in a
computed authenticated jump. It is an obfuscated interpreter or crypto-virtual-machine blob.

Comparing a representative pair from the smallest real block shows the same structure and
the same control flow on both sides, differing only in the baked material: different key
and multiplier constants, different table bases and entry offsets, and a different
jump-authentication diversity value. Nothing about bounds, lengths, or object lifetimes
changes shape. This reads as a **recompiled obfuscated blob carrying a new per-build key** —
a crypto/feature refresh, not a security fix.

A whole-image scan for direct calls to the first changed function finds none; the blob is
entered through its own computed-jump dispatch, so static caller counting cannot enumerate
its internal edges either way.

## Reachability

The extension's published personalities contain exactly one service — a FairPlay service
matched through the resource plane — and **no user-client class**. A user-client class does
exist in the binary, but creating it requires passing an open-time gate that looks up three
private FairPlay entitlement strings and fails when none is present, and a dump of that
class's method table shows every extension-local target below the changed region, so no
method-table slot points at a changed function. All of the user-client method messages in
the image resolve into the unchanged portion of the extension.

## Assessment — bounded negative

No out-of-bounds access, type confusion, lifetime error, kernel read/write primitive or
jailbreak is established. The largest remaining un-audited equal-count member carries no
app-reachable change, so this axis is closed rather than promoted. It should not be
reopened without a newly published user-client class, a new factory route, or a concrete
changed bound or length check in this extension.

## Tooling note

This extends the project's existing rule. An index-paired count must be re-checked per
function before it means anything; here that turned 69 nominal changes into 7 real blocks,
and reading one real block then showed those are an obfuscated blob recompiled under a new
key. Two stages of filtering were needed, and neither alone was sufficient.
