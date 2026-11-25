# Allocator callback-slot writer audit — iPhone14,2 / 24A5390f

- **Date:** 2026-11-25
- **Target:** iPhone14,2, iOS 27.0 build `24A5390f`
- **Kernelcache SHA-256:** `6719422222a3b68120f663b2113272b5bcf48d648afe892bbce23b8460ba47dd`
- **Scope:** Exact-build static analysis only. No device test, selector/method call, build, or install occurred.

## Findings

The class-0 consumer `a205b20` passes allocator entry 0 to `a277c94`, which reads the entry's `+0x34` size and the optional callback qword at `+0x40`. If that callback is null, the path reaches `a278360` with the original entry in `x0`. On that path `a278360` reads `+0x34`, `+0x36`, and `+0x8`, but its entry-rooted stores are at `+0x90`, `+0xa8`, `+0x6c`, and `+0x74`, not `+0x34`. This branch is conditional on the live callback value; the pinned file has zero `+0x40` qwords for entries 0–40, which does not establish post-init state.

A width-aware review of 50 page-rooted candidate stores found one apparent `+0x42` overlap at `a279774`. Disassembly shows the store is `str w14,[x13,#0x3c]`, with `x13` holding the current entry base in the sentinel default-fill loop. Its four-byte write ends at `+0x40` and does not overlap the callback qword `[+0x40,+0x48)`. The two known indirect size-setting helpers, `a279ae8` and `a279c70`, write only `+0x3c` and `+0x34`; in the analyzed `(7,0)` records they conditionally target entries 2 and 1.

Across 513,607 decoded fixup records, no source cell targets the generic creator `a2791a4` or helper `a273b18`. Exactly two target the known size helpers: `0xfffffff007ba3338 -> a279c70` and `0xfffffff007ba3378 -> a279ae8`, both in `__DATA_CONST`. This is a file-image fixup census, not proof that code-derived, runtime-generated, or otherwise indirect dispatch is absent.

## Assessment and limits

This review did not find a callback-qword write within the bounded store candidates or the two known helper bodies, and it did not establish a class-0 runtime size. The selector-5 `buffer+7` access remains a logical overread only; allocation capacity, backing mapping, and physical bounds are unresolved. No vulnerability, memory corruption, kernel read/write primitive, exploit, or jailbreak is established.
