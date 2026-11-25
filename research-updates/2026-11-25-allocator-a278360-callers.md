# Direct callers of allocator fallback `a278360` — iPhone14,2 / 24A5390f

- **Date:** 2026-11-25
- **Target:** iPhone14,2, iOS 27.0 build `24A5390f`
- **Kernelcache SHA-256:** `6719422222a3b68120f663b2113272b5bcf48d648afe892bbce23b8460ba47dd`
- **Scope:** Exact `com.apple.kernel` executable code, static analysis only. No device test, selector/method call, build, or install occurred.

## Result

A scan of 21,072 exact kernel function starts and 2,285,568 instructions found two direct `B`/`BL` sites to `a278360`:

| Caller | Site | Branch | Path |
|---|---:|---|---|
| `a277c94` | `0xfffffff00a277e30` | `B` | Conditional null-callback route; `x0` remains the original allocator entry pointer. |
| `a27c5e8` | `0xfffffff00a27c7c8` | `BL` | `x0=x19`, where `x19=table_base + w9*0xc0` and `w9` comes from incoming `w0`. |

The same exact-kernel scan found two direct call sites to `a27c5e8`. Both set `w0=0x21` (entry index 33) immediately before calling it:

- Caller `0xfffffff00a775294`, call site `0xfffffff00a7754ac`.
- Caller `0xfffffff00a776a2c`, call site `0xfffffff00a776b54`.

The pinned 513,607-record decoded-fixup map has no source cell targeting `a27c5e8`. Thus the second direct `a278360` path uses entry 33 at its observed direct callers, not entry 0. Branch immediates were normalized to 64-bit addresses during the scan because Capstone represents high kernel VAs as signed integers.

## Limits

This closes only the stated kernel direct `B`/`BL` call sites and decoded data-fixup scope. It does not rule out indirect calls, runtime-generated pointers, or other dispatch paths. No live class-0 size, callback value, allocation extent, or mapping is established. The selector-5 `buffer+7` access remains a logical overread only. No vulnerability, memory corruption, kernel read/write primitive, exploit, or jailbreak is established.
