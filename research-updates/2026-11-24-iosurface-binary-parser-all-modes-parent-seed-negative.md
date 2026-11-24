# IOSurface selector-0 binary parser all-mode parent-seeding check — static negative

**Date:** 2026-11-24
**Target:** iPhone14,2, iOS 27.0 build `24A5390f`
**Kernelcache SHA-256:** `6719422222a3b68120f663b2113272b5bcf48d648afe892bbce23b8460ba47dd`
**Scope:** Exact-build static caller/reference census and full disassembly review of the selector-0 `0xd4` binary parser, factory, forwarding wrapper, and callback-mode parent-stack paths. No device method or selector was called.

## Result

This follow-up expands the earlier direct-factory-mode negative. The factory at `0xfffffff00a8ba8a8` passes `x2=x3=w4=0` to the parser at `0xfffffff00a8bb630`. An alternate forwarding wrapper preserves caller arguments. In the caller census, seven non-IOSurface importer calls have stack-derived `x2` and unresolved `w4` flags; nonzero `x2` alone does not establish callback execution. The callback path can be assessed statically even though no alternate callback invocation is proven.

The parser saves `x2` as the indirect callback function and `x3` as callback context. The exact instruction sequence at `0xfffffff00a8bbd88` and `0xfffffff00a8bbe3c` loads the callback target into `x8` and context into `x0`, then calls through `blraa x8`. The parser initializes the current-parent slot `[sp]`, parent-stack depth, and stack base to zero. Its only indexed parent-stack store, at `0xfffffff00a8bc248`, writes `x20`, selected as either zero or the already-existing current parent. Parent classification and non-null class-parent stores occur only after scanning an existing non-null parent-stack entry. The callback return is not the value written to that parent-stack slot.

A store at `0xfffffff00a8bbc6c` was initially mistaken for a parent-stack write. Its base is the separate object-table pointer at `[sp+0x70]`, and its index is the object count; it does not seed the parent stack. A fresh full-function store scan found no other indexed parent-stack write.

A whole-cache caller census covered 255 executable file-backed segments (43,149,776 bytes across 252 fileset members). It found 2 direct branches to the parser, 3 to the forwarding wrapper, 8 to the factory, 19 on-disk format-8 fixup cells resolving to the factory, and 43 calls to the 19 importing loader stubs. All seven IOSurface calls to the relevant import stub set `x2=0`; among the full 43 importer calls, 36 explicitly set `x2=0` and seven non-IOSurface calls use stack-derived `x2` with `w4` provenance unresolved. Nonzero `x2` alone does not prove callback dispatch. The fixup results are on-disk target decodings; they do not prove live PAC-signed pointers, runtime installation, or runtime calls. The non-IOSurface forwarding-wrapper callers have not been linked to IOSurface row 0 or the `IOSurfacePlaneInfo` property path.

**Bounded conclusion:** In the exact binary parser's explicit parent-stack and callback paths, serialized input cannot seed the first non-null collection parent. The nested `OSDictionary → IOSurfacePlaneInfo → OSArray` graph required by the reviewed `c27200` path therefore cannot be assembled through this parser's parent-stack mechanism. This supersedes the earlier note's narrower direct-mode scope. It is not a whole-parser memory-safety proof and does not cover arbitrary opaque callback side effects or the separate text-parser route.

## Limits

This is static analysis of one exact kernelcache. It does not establish ordinary-app IOSurface reachability, runtime installation of the decoded fixup targets, or behavior of unreviewed callback implementations. The distinct text-parser route remains unresolved. No vulnerability, memory corruption, kernel read/write primitive, exploit, or jailbreak is established.