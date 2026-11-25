# Descriptor-relative allocator-helper use-def — iPhone14,2 / 24A5390f

- **Date:** 2026-11-25
- **Target:** iPhone14,2, iOS 27.0, build `24A5390f`
- **Kernelcache SHA-256:** `6719422222a3b68120f663b2113272b5bcf48d648afe892bbce23b8460ba47dd`
- **Scope:** Exact-build static analysis only. No device/Mac connection, build, install, selector, or method call occurred.

## Finding

A previous address-only scan found no direct branch to the two size-setting helpers and did not resolve their `x1` receiver. That negative was too broad: the generic creator `0xfffffff00a2791a4` dispatches through a caller-supplied descriptor. It saves incoming `x4` at `0xfffffff00a279234`, reloads it into `x0` at `0xfffffff00a279588`, then on its fresh-entry path loads the function pointer from `[x4+0x10]` at `0xfffffff00a2795c4`, sets `x1=x23` at `0xfffffff00a2795c8`, and executes `blraa x9,x8` at `0xfffffff00a2795cc`.

In initializer `0xfffffff00aa3842c`:

| Creator call | `x3` | `x4` descriptor | Descriptor-relative fixup cell | Decoded on-disk target | `x1` receiver |
|---|---:|---:|---:|---:|---:|
| `0xfffffff00aa384ec` | 1 | `0xfffffff007ba3328` | `0xfffffff007ba3338` | `0xfffffff00a279c70` | `0xfffffff00ad38340` |
| `0xfffffff00aa38514` | 2 | `0xfffffff007ba3368` | `0xfffffff007ba3378` | `0xfffffff00a279ae8` | `0xfffffff00ad38400` |

The creator forms `x23` as `0xfffffff00ad38280 + x3*0xc0`, then passes that entry pointer in `x1`. The two helper bodies both set bit `0x100` at `[x1+0x3c]` and store 16-bit `1` at `[x1+0x34]`.

## Branch and runtime limits

The corresponding `x2` flags are `0xe000000044000020` and `0xe000000045000020`. With `x21=x2`, bit 61 routes control from `0xfffffff00a2795b0` to `0xfffffff00a279668`; bit 60 is clear, avoiding that alternate error branch, and bit 54 is clear, so the `tbz` at `0xfffffff00a279688` returns to the callback block at `0xfffffff00a2795bc`. Thus these constants permit the helper dispatch on the fresh-entry path.

This path is conditional: if `[x23]` is already nonzero, the creator returns through its existing-entry branch; allocation/creation must also succeed. Static disassembly and decoded fixups do not establish that the callback ran at runtime or that these on-disk targets are live PAC-signed pointers.

The later sentinel creator call `0xfffffff00aa38544` passes `x3=0xffff` and `x4=0`, so it skips the callback at the null check. Under the previously established sentinel semantics it selects index 40 or above, not parser-selected entry 0. The bounded 96-site direct creator census still found no constant-zero index; two dynamic sources and generated/indirect paths remain limitations.

## Context-backed dynamic callback census

Callback `0xfffffff00aa381b8` loads `w3` from context `+0x20`, `x4` from `+0x28`, then calls the generic creator at `0xfffffff00aa381dc`. Across all 62 exact order-7/flags-3 records, the decoded on-disk `x3` values are 40 sentinel `0xffff` entries and 22 explicit indices 3–39; none is zero. The `x4` field is zero in 59 records, so the creator's null check skips its helper callback for those records.

The only nonzero descriptors belong to orders 2559–2561 and indices 37–39: descriptor `0xfffffff007bf1040` selects helper `0xfffffff00a772024`, `0xfffffff007bf11c8` selects `0xfffffff00a77200c`, and `0xfffffff007bf1210` selects `0xfffffff00a771ff4`. These helpers store `0xfffffff007bf0ff8` into global pointer-table slots `0xfffffff007bf1188`, `0xfffffff007bf1190`, and `0xfffffff007bf1198`, respectively; they do not use `x1` or write the allocator entry's `+0x34` field. This bounds the context-backed path on disk but does not establish live data or runtime execution.

## Effect on the parser candidate

These two helper paths identify entries 1 and 2 in this initializer; they do not establish a writer for entry 0 at `0xfffffff00ad38280`. The selector-5 parser's `buffer+7` access for a 7-byte input remains a logical overread only. Class-0 size, backing extent, mapping, and physical bounds remain unknown. No vulnerability, corruption, kernel read/write primitive, exploit, or jailbreak is established.
