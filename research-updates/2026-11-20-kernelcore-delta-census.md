# Kernel-core 27.0.1 → 27.2 delta census, and one fix-shaped candidate

Date: 2026-11-20
Builds: iOS 27.0.1 kernelcache (24A446, target) and iOS 27.2 kernelcache (24B119, reference)
Scope: `com.apple.kernel` only
Device activity: none. No device was enumerated by an authorised host, so nothing here is a runtime result.

## What was done

The whole kernel-core member was taken through the project's cross-build pipeline:
function alignment, per-block shape re-checking, masked-instruction delta clustering,
per-function index pairing inside equal-count blocks, and a second clustering pass keyed
on instruction mnemonics alone (to expose idioms that register-aware comparison hides).

Headline counts: 3,964 replace blocks; 308 blocks classified as real code edits after
3,030 were shown to be address/data-layout drift; 7,467 distinct masked-text deltas;
268 real per-function pairs; 1,678 mnemonic-level deltas.

## What the census shows

1. **Most flagged differences are recompilation artefacts.** After removing them, the
   largest remaining groups are single-instruction register renames and prologue/epilogue
   stack-slot moves. They are not edits.
2. **One systemic change is already known.** The clusters that look like inserted
   compare-and-branch sequences are alignment artefacts of the reserved message-flag bit-8
   clear (`load word; and #~0x100; store`) that the newer build inserts in kernel-core
   `Dispatch(const IORPC)` overrides. That family was characterised and closed earlier.
3. **One numeric change is layout, not a fix.** A per-CPU statistics gatherer computes its
   element offset with a multiply by `0x468` in the target build and by `0x480` in the newer
   build (about 34 sites). It reads per-CPU counters through the per-CPU accessor and fills
   a per-CPU array, so this is a structure-size change, not validation logic.

## New candidate (unconfirmed, static only)

Inside an equal-count block of seven functions, the target and newer builds pair cleanly.
In one pair the newer build grows from `0xcc` to `0xfc` bytes. Both versions decode an
authenticated descriptor, extract a count from it, derive a base pointer, and walk a linked
list whose elements are `0x18` bytes with a count field at `+0xc`.

The newer build inserts, on each iteration, a bound assertion before dereferencing:
`count * 0x18 + 0x18` is compared against a limit derived from the descriptor, and failure
reaches a trap. The target build performs the same walk with no such check. A sibling
function in the same block gains only null-check and tag-test-order tweaks.

This is **fix-shaped**: it is the kind of check that would be added after an out-of-bounds
or overflow report. It is **not established** as a vulnerability:

- the owning subsystem is unidentified (no diagnostic string is referenced anywhere in the
  function family);
- whether the per-element count and the descriptor-derived limit are attacker-controlled is
  unknown;
- no sandboxed-app ingress to the family has been traced.

No out-of-bounds access, controlled corruption, kernel read/write primitive or jailbreak is
claimed. The candidate is recorded so the owner can be named next; no probe was designed or
run for it.

## Next step

Name the function family (pointer-slot / vtable census, then trace its callers upward) and
only then judge attacker control and app reachability. Device work remains gated on an
authorised host enumerating a phone; no generic stress test was run.
