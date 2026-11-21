# IOHIDFamily out-of-bounds fix sites — descriptor provenance and the virtual-HID entitlement gate

Date: 2026-11-21
Builds: iOS 27.0.1 `24A446` (target) and iOS 27.2 `24B119` (reference), arm64e kernelcache.
Device/build host: unreachable this run. No device probe was run and no panic-capable path was touched.

This continues the two earlier HID checkpoints: the localisation of four accessor routines
that gained bounds checks in the newer build, and the correction showing that two of the four
are live code reached from the extension's element-hierarchy builder. This pass answers the
open reachability question — *can any app-openable client start element-container
construction?* — and records the exact shape of the newer build's guard.

## 1. What the newer build actually checks

For the second live accessor, `0xfffffe000a0c1894` (27.0.1) versus `0xfffffe000a11094c`
(27.2): the target build walks a descriptor-derived array, takes an index stored inside each
element, sign-extends it and loads from `base + index*0x14 + 8` with **no compare against the
count field**. The newer build inserts, inside the same loop, a load of the count
(`[obj+0x40]`, hoisted out of the loop), a `index < count` branch that substitutes zero for
out-of-range elements, and a non-null check on the array base `[obj+0x38]`:

```
ldrsw x15, [elem, #8]      ; index
cmp   w15, w11            ; w11 = [obj+0x40]
b.ge  <zero>              ; out of range -> result word 0
ldr   x16, [obj, #0x38]    ; base
cbz   x16, <zero>
smull x15, w15, #0x14
add   x15, x15, #8
ldr   w15, [base + x15]
```

The first live accessor (`0xfffffe000a0bc6d0`) uses the same `[obj+0x38]` / `[obj+0x40]`
pair. The descriptor object carries the magic `0x68696420`; its region bases and count fields
are filled by two parser passes over the report-descriptor bytes, so the index and the base
are parser-produced rather than caller-supplied scalars.

## 2. Where the descriptor comes from

Both live accessors are reached only through the element-hierarchy builder:
container initialisation (which logs a failure to open the report descriptor) calls
`createElementHierarchy`, which calls the two accessors. That initialiser has no direct
caller; it occupies two method-table slots. The two remaining accessors still have no direct
caller and no pointer-slot reference under every control-validated scan used.

## 3. The only app-facing producer of a report descriptor is entitlement-gated

The platform publishes exactly one user client for the virtual-HID service:
`IOClass=IOHIDResource` maps to `IOUserClientClass=IOHIDResourceDeviceUserClient`. Its class
is now pinned rather than inferred: the instance constructor stores instance-vtable address
point `0xfffffe000831f290` (Itanium header at `0x831f280`), and two metaclass constructors
store the metaclass vtable `0x831f8a0`.

Slot 171 of that instance vtable holds a predicate routine that consults two task
entitlements — `com.apple.hid.manager.user-access-device` and
`com.apple.developer.hid.virtual.device` — and, when neither is held, logs
`"%s:0x%llx %s is not entitled"` and returns false. When either is held it populates
per-client state and returns true. It has no direct caller (it is reached indirectly), so the
caller that consumes this predicate is not yet named.

Historical device measurement with the project's unsigned carrier: opening `IOHIDResource`
at client types 0–4 returned `kIOReturnBadArgument` uniformly on both test devices. A later
method-call sweep opened three other HID services at type 2 but never `IOHIDResource`.

## 4. Bounds and consequence

Established: the exact guard shape; that the descriptor object is parser-built and reached
only via the hierarchy builder; the identity and vtable of the virtual-HID user client; that
its predicate consults a restricted virtual-HID entitlement and reports "not entitled" without
one; and that every measured open of that service was refused.

Not established: whether a malformed report descriptor can drive an index past the count
(the writers of the count and of the per-element index were not isolated); which indirect
caller consumes the slot-171 predicate and whether a missing entitlement denies device
creation or only configures a degraded mode; and any successful open of the service from a
sandboxed app.

This stays a **device-attach-path finding** with no app-carried trigger. No out-of-bounds
access, type confusion, lifetime error, kernel read/write primitive or jailbreak is claimed;
readiness for this path is unchanged.

## 5. Next steps

1. Isolate the writers of the count and of the per-element index in the two parser passes, to
   decide whether a descriptor item can exceed the count — independent of reachability.
2. Name the indirect caller of slot 171 to learn what the entitlement gates.
3. With a device host available, retry the virtual-HID service across a wider client-type
   range with a carrier that requests `com.apple.developer.hid.virtual.device`, and record the
   exact open result; do not attempt element-container creation without a safe oracle.
