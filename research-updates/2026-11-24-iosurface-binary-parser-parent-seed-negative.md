# IOSurface selector-0 binary parser parent-seeding check — static negative

**Date:** 2026-11-24
**Target:** iPhone14,2, iOS 27.0 build `24A5390f`
**Kernelcache SHA-256:** `6719422222a3b68120f663b2113272b5bcf48d648afe892bbce23b8460ba47dd`
**Scope:** Exact-build static disassembly of the `0xd4` custom binary parser, its selector-0 factory, and the caller's returned-object class gate. No device method, selector, build, or install was run.

## Result

The selector-0 factory at `a8ba8a8` calls the binary parser with `x2=x3=w4=0`, selecting the direct collection-dispatch mode. Parser setup initializes `[sp]`, parent-stack depth/storage/capacity, and the OSDictionary/OSArray/OSSet parent slots to zero. For collection token types, the low-24-bit field is a requested collection capacity, not an expected child count.

The only indexed parent-stack store in the parser writes `x20` at `a8bc248`. The preceding `a8bc1c0–1c8` sets `x20` to zero when token bit 31 is set, or copies the current `[sp]` value when it is clear. Since `[sp]` begins zero, every pushed stack entry is explicitly zero unless parent setup has already found a non-null entry. The parent-class setup at `a8bc0a8–1bc` can set `[sp]` and a class-specific parent slot only after finding and classifying a non-null stack candidate. With only zero entries, the backward scan exits at depth 1; it does not read uninitialized stack slot 0. The depth-zero path also exits without setting a parent.

Therefore, in this factory's direct mode, the parser cannot seed an OSDictionary, OSArray, or OSSet parent from the first root container, and has no parent to which it can attach the nested `IOSurfacePlaneInfo` array/dictionary graph consumed by `c27200`. The caller's OSDictionary-or-subclass filter does not supply that missing graph. No concrete token stream is justified.

## Limits

This is a bounded static negative for the selector-0 factory arguments and direct mode. It does not assess alternate parser callers with different context/mode arguments, the text parser, or runtime installation/reachability. It is not a parser-wide memory-safety proof. No out-of-bounds access, corruption, kernel read/write primitive, exploit, or jailbreak is established.
