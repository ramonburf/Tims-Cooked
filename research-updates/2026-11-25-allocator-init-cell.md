# Early-init allocator callback-cell census — static, bounded

- **Date:** 2026-11-25
- **Target:** iPhone14,2, iOS 27.0 build `24A5390f`
- **Kernelcache SHA-256:** `6719422222a3b68120f663b2113272b5bcf48d648afe892bbce23b8460ba47dd`
- **Scope:** Exact-build init-registry validation and a bounded direct-reference scan for one optional callback cell. No device test, selector, or method call was run in this follow-up.

## Result

The exact `__BOOTDATA.__init_entry_set` table contains 3,353 24-byte records. Decoding the authenticated callback pointer at record `+8` against the exact `__TEXT` base yields 106 unique function starts and no decoded non-starts. The order-1 callback at record 27 is `0xfffffff00aa304d4` (flags `0xffffffff`).

The optional callback cell at `0xfffffff007b98290` is in `__DATA_CONST`; its on-disk qword is zero and the validated format-8 fixup walk found no chain entry. A raw aligned ADRP scan found 118 instructions targeting its page, mapping to 82 exact function intervals. Limited exact-function ADRP/ADD/MOV tracking found three direct accesses to the cell, all loads and no direct stores:

- `0xfffffff00a1d4008` in `0xfffffff00a1d3fc0`;
- `0xfffffff00a1d4d18` in `0xfffffff00a1d4c88`;
- `0xfffffff00aa304f0` in callback `0xfffffff00aa304d4`.

Each reader checks `cbz x8` before its authenticated indirect call: respectively `a1d4014`, `a1d4d2c`, and `aa304fc`. Thus, if the cell remains zero at runtime, these dispatches are skipped. The first two reader functions are not init-table entries; their direct callers were found at `a1de848` and `a1e7e44`.

**Bounded conclusion:** No direct store to this cell was found in the ADRP-derived references tracked across those exact function intervals. This narrows the optional order-1 callback path; it does not establish the live cell value or exclude writes through aliases, indirect mutation, alternate address encodings, or loader-time activity.

## Relation to the allocator/parser candidate

The separate allocator initialization path remains conditional on runtime count/entry state and successful execution; this cell census does not establish the live class-0 element size or backing extent. The quoted-attribute parser candidate still has a logical `buffer+7` load for a 7-byte input, but physical allocation bounds, mapping, and any out-of-bounds effect remain unverified.

No vulnerability, kernel read/write primitive, exploit, or jailbreak is established. No Mac/device connection, build, install, selector, or method call occurred in this pass. Next: check alternative literal/absolute references and indirect aliases, then continue the class-0 count/size writer audit.
