# Largest unexamined changed kernel extension retires as address drift

Date: 2026-11-20
Builds: iOS 27.0.1 kernelcache (build 24A446, target) and iOS 27.2 kernelcache (build 24B119, reference)
Scope: `com.apple.iokit.IOSCSIArchitectureModelFamily`
Device activity: none. No authorised host enumerated a device, so nothing here is a runtime result.

## Background

The cross-build census of changed kernel extensions ranks members by an index-paired
count of functions whose instruction fingerprint differs. That count is only valid as a
ranking hint: when a member's data segment moves between builds, every address literal
inside untouched code changes too. This checkpoint examined the largest un-audited
member in the equal-function-count subset, whose nominal count was **248** changed
functions — which would have made it the most-changed extension after the kernel core.

## Result

Both builds contain **734** functions in this member. The alignment pass flags 56 replace
regions plus one deletion; a per-function shape re-check reduces them to **54 regions of
address/data-segment drift and 2 real edits**. The nominal 248 is therefore almost
entirely recompilation noise, not changed logic.

## What the two real edits are

Both are in the internal SCSI task object's lifecycle, in the same compiled cluster as
that class's type descriptor:

* In a teardown-shaped routine, the newer build replaces a conditional field clear
  (gated on an identity comparison against a global pointer) with an unconditional clear,
  and inserts a notification call ahead of it that runs only when a state byte's bit 0 is
  set and the related object pointer is non-null. The notification goes through an
  imported kernel stub whose target could not be named — neither kernel image carries a
  symbol table.
* A small helper that stored the object's back-pointer and state fields was removed; its
  body now appears inlined in the constructor that used to call it, and the inlined copy
  performs the same notification call first.

These are refactor/hardening-shaped changes to an unpublished internal storage-stack
object, not an observable memory-safety defect.

## Reachability

The extension's published personalities are exactly two — a subsystem-globals service
matched through the resource plane and a peripheral-device nub matched through the SCSI
protocol-services plane. It publishes **no user-client class**, and the changed teardown
routine has no direct caller in either build, so it is entered indirectly. Nothing here
is an app-facing interface.

## Assessment — bounded negative

No out-of-bounds access, type confusion, lifetime error, kernel read/write primitive or
jailbreak is established. The largest un-audited equal-count member carries no
app-reachable change, so this axis is closed rather than promoted.

## Tooling note

This reinforces the project's existing rule: never rank or report a member from an
index-paired change count alone. Re-check each flagged region per function with a
shape-only comparison first — here that turned 248 nominal changes into 2 real ones.
