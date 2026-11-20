# Mach IPC port-name table accessors identified as the kernel-core fix-shaped cluster

Date: 2026-11-20
Builds: iOS 27.0.1 kernelcache (build 24A446, target) and iOS 27.2 kernelcache (build 24B119, reference)
Scope: `com.apple.kernel`
Device activity: none. No authorised host enumerated a device, so nothing here is a runtime result.

## Background

An earlier checkpoint ran a whole-member cross-build census of the kernel core and
surfaced one fix-shaped candidate: in a small function family that walks a linked list
of fixed-size entries reached through an authenticated descriptor, the newer build
inserts a per-entry bound assertion (`count * 0x18 + 0x18` against a limit) before
dereferencing, while the target build performs the same walk without it. The owning
subsystem was unidentified because no diagnostic string is referenced anywhere in the
family.

## Identification

The family is the Mach IPC **port-name table accessor** set from the public XNU source
(`osfmk/ipc/ipc_entry.c`): the routines that look up, reserve, claim, allocate, resize
and release entries in a task's IPC space. The match was made structurally, not from
symbols or strings:

* the space object stores an authenticated table pointer; the code authenticates it
  with a diversity key and then treats the pointer as self-describing (a base plus an
  element count);
* each table element is exactly `0x18` bytes, with the object pointer at offset 0,
  a bits/generation word at `+0x8`, and the free-list link at `+0xc` — which explains
  both the walk stride and the `+0xc` link field seen in the disassembly;
* one member takes a port name, derives the table index from the name's bits, rejects
  index zero, and compares the stored generation and capability-type fields against the
  name — the port-name lookup routine;
* another takes a count, applies a load-factor threshold against the hashed-entry
  count, walks the free list, and returns `KERN_NO_SPACE` on exhaustion — the routine
  that reserves several free entries at once.

The public source was used only as a semantic fingerprint. Every offset, constant and
branch used for the identification was checked in the target image, and the target's
own compiled arithmetic differs slightly from current macOS source (its table count is
decoded from a tagged pointer representation), which is recorded rather than smoothed
over.

## What the newer build changes

Across the family, the newer build inserts per-access **index bounds checks** before
dereferencing a pointer derived from a table index: the element size times the index,
plus one element, is compared against the decoded table limit, and a violation traps.
The port-name lookup additionally gains a null check on the computed entry pointer and
a restructured type/generation test. These are internal-invariant assertions.

## Assessment — bounded negative

This reframes and closes the earlier candidate:

* the port-name lookup's index is user-influenced, but **both builds already validate**
  the index against the table size before reading the entry; the newer build only adds
  a null check and reorders the existing type/generation comparison.
* the reservation and claim routines walk the free-list link, which is kernel-owned
  state; the callers that pass a variable count supply only small counts, and the other
  passes a single entry.
* no attacker-chosen value is shown to reach an unvalidated dereference. The added
  checks are defence-in-depth for an already-inconsistent table, not an app-triggerable
  memory-safety defect.

No out-of-bounds access, controlled corruption, kernel read/write primitive or jailbreak
is established. The earlier "fix-shaped candidate" is therefore recorded as a bounded
negative, not promoted to a vulnerability. No probe was run.
