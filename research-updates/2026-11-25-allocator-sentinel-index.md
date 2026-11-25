# Allocator sentinel-index correction — iPhone14,2 / 24A5390f

- **Build:** iOS 27.0, `24A5390f`
- **Kernelcache SHA-256:** `6719422222a3b68120f663b2113272b5bcf48d648afe892bbce23b8460ba47dd`
- **Scope:** Exact-build static analysis only; no device, selector, or method was exercised.

## Corrected creator interpretation

The boot-prelude call at `0xfffffff00aa3c878` passes `x1=0x100` and sentinel `x3=0xffff` to creator `0xfffffff00a2791a4`. The creator first checks the 16-bit count at `0xfffffff00ad38266`. When the count is at most `0x27`, it initializes default descriptors through index 39 and stores count `0x28`; the sentinel then selects index 40. With a count already at least `0x28`, it selects that current index. On these normal valid-count paths, the requested rounded size `0x100` can apply to a dynamic entry at index 40 or above—not parser-selected entry 0 (`0xfffffff00ad38280`). The earlier inference that a zero initial count made this sentinel call initialize entry 0 was incorrect.

## Bounded caller census

A constant-propagation pass over 96 direct creator `BL`/tail-`B` sites across 71 functions found 83 sentinel `x3=0xffff` sites, 11 explicit nonzero constants (`1, 2, 15–21, 26, 27`), and two dynamically derived values; no constant-zero `x3` was found.

One dynamic source reads `w3` from callback-context offset `+0x20`. All 62 order-7/flags-3 context pointers were decoded from their exact format-8 fixup slots and mapped to `__DATA`; their values are 40 instances of `0xffff` and 22 nonzero values in the range 3–39, with no zero. The other source adds `0xa` to its incoming low 16 bits; the five traced authenticated-stub callers pass 0–4 and therefore reach indices 10–14. These findings are limited to the scanned direct sites, contexts, and callers; generated/indirect paths and runtime state are not excluded.

## Effect on the parser candidate

The selector-5 text-parser candidate still performs a logical `buffer+7` load for a 7-byte input, and class lookup selects entry 0. This `0x100` sentinel registration does not establish entry-0 `+0x34`, so it cannot be used to show that the load fits within an element. Entry-0's live size, backing extent, mapping, and any physical out-of-bounds effect remain unresolved. No vulnerability, memory corruption, kernel read/write primitive, exploit, or jailbreak is established.
