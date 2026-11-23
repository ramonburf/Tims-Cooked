# IOSurface `IOSurfacePlaneInfo` class gate — static

**Date:** 2026-11-23
**Target:** iPhone14,2, iOS 27.0 build `24A5390f`
**Kernelcache SHA-256:** `6719422222a3b68120f663b2113272b5bcf48d648afe892bbce23b8460ba47dd`
**Scope:** Exact-build kernelcache disassembly and on-disk chained-fixup analysis only. No device method, selector, build, or install was run for this update.

## Result

A previous pass found that `c27200` calls the object returned for `IOSurfacePlaneInfo` through vtable slot `+0x90`, uses the returned count `n` in allocation requests of `24*n` and `32*n`, and rejects `n > 3` only after those requests. The call site itself has no direct type test. The lookup helper does, however, filter the property value by class:

- `c2c2a4` gets the property through object slot `+0x138`, loads the requested metaclass pointer, then tail-branches through `c54a3c`.
- The authenticated on-disk fixup at `0xfffffff00804b648` resolves to `0xfffffff00a877130`. That helper calls slot `+0x38`, compares the returned class pointer with the requested metaclass, follows the superclass link at `+0x10`, and returns the original object only when the class or a superclass matches.
- The requested metaclass pointer resolves through `0xfffffff00804b950` → `0xfffffff007c44438` → `0xfffffff00ad81c50`. Exact-build constructor `0xfffffff00a87c058` initializes that global with class name `OSArray`, superclass global `0xfffffff00ad81f10`, and size `0x28`.
- The exact-build `OSNumber` constructor at `0xfffffff00a8acc54` instead names `OSNumber` and supplies the `OSObject` metaclass as its superclass. A plain `OSNumber` therefore cannot pass the `IOSurfacePlaneInfo` lookup's `OSArray`-or-subclass gate and reach the `+0x90` call through this path.

This resolves the earlier question about a wrong-type plain `OSNumber` being invoked at `+0x90`. It does **not** identify the exact `+0x90` method implementation or the concrete subclass returned by the property helper.

## Remaining limits

The `n > 3` check still occurs after the two allocation requests; no earlier count bound was established in this trace. The selector-0 text parser has an unchecked 64-bit numeric accumulator, but its record `+0x48` value has not been connected to the `IOSurfacePlaneInfo` property, an accepted array element consumed by `c27200`, or the count/allocation operands. No concrete text-token-to-allocation chain is demonstrated.

The class and function identities above are derived from exact-build code, constructor arguments, and on-disk fixups; they do not prove that a particular vtable is installed on a live object or that an ordinary app can open and invoke this path. No out-of-bounds access, type confusion, memory corruption, kernel read/write primitive, exploit, or jailbreak is established.
