# Allocator entry-table size-writer census — iPhone14,2 / 24A5390f

- **Date:** 2026-11-25
- **Target:** iPhone14,2, iOS 27.0, build `24A5390f`
- **Kernelcache SHA-256:** `6719422222a3b68120f663b2113272b5bcf48d648afe892bbce23b8460ba47dd`
- **Scope:** Exact-build static analysis only. No device/Mac connection, build, install, selector, or method call occurred.

## Result

An expanded scan covered 21,072 exact kernel function starts and 2,285,568 decoded instructions for references to allocator entry-table page `0xfffffff00ad38000`. The branch-reset tracker recorded 132 accesses; a broader symbolic tracker that does not reset across control-flow edges or calls recorded 215 candidate accesses, including 50 stores. The broader set is an over-approximation, not a set of proven feasible paths.

Only two page-derived stores in that broader set use displacement `+0x34`: the known fresh-entry writes in generic creator `0xfffffff00a2791a4`, at `0xfffffff00a279434` and `0xfffffff00a2794a4`. No additional page-rooted entry-table size writer was recovered.

A whole-image displacement census found 691 stores with a memory-operand displacement of `+0x34`; 30 are halfword stores across 22 functions, including 21 non-stack stores across 14 functions. The matching offset does not establish that a store's receiver is allocator entry 0.

One word-store candidate, `0xfffffff00a32d284`, writes to `[x23+0x34]` at three sites. Its companion helper copies incoming `x1` into context `+0x10`, which the store function reloads as its receiver. The direct-call census found 19 callsites across 18 functions. Two callers also reference the allocator table page; at those callsites, the receiver is each caller's original `x0`, not a locally computed table-entry pointer. This does not prove or exclude a runtime alias to entry 0.

## Assessment

The bounded page-rooted scan found no new entry-table size writer, but register-based aliases, indirect/generated call paths, and runtime mutation remain unexcluded. Class-0 `+0x34`, allocation capacity, and backing mapping are still unknown. The selector-5 `buffer+7` access is therefore established only as a logical overread, not a physical out-of-bounds read. No vulnerability, memory corruption, kernel read/write primitive, exploit, or jailbreak is established. No IPA is included.
