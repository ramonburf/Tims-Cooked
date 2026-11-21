# APFS member delta audit — three added input validations in 27.2; no app ingress established

Date: 2026-11-21 · Builds: iOS 27.0.1 (24A446, target) vs iOS 27.2 (24B119)
Device work: **none** — no authorised Mac enumerated a device and no iPhone was
attached to the Windows workstation. All results are static binary reading.

## Why this extension

`com.apple.filesystems.apfs` is the highest-value changed kernel extension that
the two index-paired sweeps could not cover: it has **2396 functions in the
target build and 2399 in the newer build**, so raw index pairing misaligns and
every later function would be compared against the wrong counterpart. It is
also one of the few remaining un-audited extensions whose code an ordinary app
reaches through VFS file operations rather than through a gated user client.

## Method

Alignment pass (`kz_newfunc_align.py`) → shape re-check
(`kz_pair_shape_check.py`) → per-block mnemonic-delta census (new scratch tool)
→ instruction-level diffs (`kz_fn_sem_diff.py`). Of 443 flagged regions,
**401 reduce to address/data-segment drift and 41 remain real edits**. Most of
those 41 are register renaming, stack-slot moves or refactors. Three contain
concrete input-validation predicates that are absent from the target build's
corresponding bodies.

## The three additions

### 1. A 16-bit record field gained bounds and type checks

In a record/descriptor parsing routine, the target build computes the remaining
buffer length, checks only that it is at least four bytes, then loads a 16-bit
field at offset +2 of a record pointer and uses it without further validation.
The newer build, at the same point, additionally requires:

- the 16-bit value to fit within the remaining buffer (`value <= length - 4`);
- the value to be at most `0x2f` (47);
- bit 0 of the record's first halfword to be clear;

and otherwise takes a return/skip path instead of using the value. The shape is
an added validation, not a refactor. The routine carries an internal
state/lock-context string and is called from **seven sites** inside the same
extension; a whole-image pointer-slot scan finds no stored reference to it.

### 2. Null and lower-bound checks around a halfword store

A small operation routine in the newer build loads a state field, branches away
when it is null, stores a 16-bit header value through a pointer derived from
that state, and then compares the header value against a minimum before use;
it also adds a null check on one argument. The target build performs the store
unconditionally and never applies those comparisons. This routine has no direct
caller and no stored reference under the scans used, so its dispatch mechanism
is unresolved.

### 3. New upper clamp before a division sequence

A conversion routine in the newer build clamps its input against a small
constant (`0xc17`) with a branch-away before a divide-by-multiply sequence,
where the target build divides without that clamp. The neighbouring internal
string suggests a verify-style helper. Three direct callers exist inside the
extension; no stored reference was found.

## What is not established

- **Field provenance.** Whether the validated values come from trusted on-disk
  volume metadata or from a caller-influenced buffer was not traced; the
  producers of the record pointer and the length argument are unresolved.
- **Owning path.** No syscall, `vnode` operation or mount path reaching any of
  the three routines was identified.
- **Effect.** No out-of-bounds access, type confusion, lifetime error, crash or
  corruption was observed or reproduced.

Because an APFS volume's metadata is kernel-trusted and an app cannot substitute
arbitrary volume structures, the default reading is **reconnaissance, not a
trigger**.

## Verdict

Three concrete validation predicates exist in 27.2 and not in the corresponding
27.0.1 bodies. That confirms Apple tightened these parsers, but reachability,
input provenance and security impact are all unresolved, and nothing here is a
vulnerability, a kernel read/write primitive, an exploit or a jailbreak. No
device probe was run.

## Next step

Trace the producers of the record pointer and length argument in the first
routine and walk its seven callers upward toward a VFS entry point; repeat for
the other two. Only if a caller chain reaches a syscall an ordinary app can
invoke on a mounted volume should a bounded control be considered.
