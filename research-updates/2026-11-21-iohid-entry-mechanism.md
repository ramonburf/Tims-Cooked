# IOHIDFamily fix sites — entry mechanism corrected: two of four accessors are live

Date: 2026-11-21
Builds: iOS 27.0.1 kernelcache (build 24A446, target) and iOS 27.2 kernelcache (build 24B119, reference)
Member: `com.apple.iokit.IOHIDFamily`
Device activity: none. No authorised host enumerated a device, so nothing here is a runtime result.

## What this corrects

The previous note on these fix sites reported that **none** of the four changed
accessor routines had a direct caller, and generalised that to "no discoverable
entry point". That verdict was computed for only two of the four routines; the
raw caller scans in the evidence directory covered just those two. Re-running
the word-level branch scan over all four gives a different picture:

| accessor position | direct call sites in the target build |
|---|---|
| first of the four | 0 |
| second | **1** |
| third | 0 |
| fourth | **1** |

The 27.2 reference build is consistent: its counterparts show the same pattern,
one caller each for the second and fourth routine. So the security-relevant
change is not confined to dead code — half of it sits on a live path.

## What the live callers are

String cross-references inside the callers resolve them to the extension's
element-hierarchy builder: the routines that log `[ElementContainer]
createElementHierarchy …` messages. The member also carries the class-name and
typed-allocation literals `IOHIDElementContainer` / `IOHIDDeviceElementContainer`.
The chain is:

* a container initialiser logs `[ElementContainer] Failed to open report
  descriptor`, obtains the parsed descriptor object, then calls the
  `createElementHierarchy` builder;
* the builder calls the second accessor with the descriptor object and an
  output record;
* the builder calls a helper that in turn calls the fourth accessor.

The container initialiser itself has no direct caller, but it occupies two
method-table slots in the extension's read-only data, in table-shaped regions
that continue into shared kernel base-class bodies. The first and third
accessors still have no direct caller and no plain, authenticated or
chained-fixup pointer slot under every scan used, each validated against a
positive control.

## Reachability: still not established for an app

This is the report-descriptor-to-element-tree construction path. It runs when a
HID service or driver is started with a report descriptor — device attach, or a
virtual-device create. Three user-client classes are vended for this extension
by the platform's published personalities; none of them is shown to reach the
element-hierarchy builder, and an earlier device sweep measured uniform
method-call refusal across every openable HID service.

What is proven here is a call chain inside the extension. What is not proven is
any sandboxed-app ingress, attacker control of the index, or a memory-safety
effect. Readiness for this path is unchanged, and no out-of-bounds access, type
confusion, lifetime error, kernel read/write primitive or jailbreak is claimed.

## Next step

Trace where the index and count fields come from in the descriptor parser, to
decide whether a malformed descriptor can drive the index out of range, and
determine whether any app-openable user client can start element-container
construction at all. Until then this remains a device-attach-path finding, not
an app-carried route, and no broad HID selector sweep should be repeated without
a named owning class and a matching client type.
