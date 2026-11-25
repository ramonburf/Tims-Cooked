# iOS 27 allocator fallback caller census — 2026-11-25

An exact-kernel direct-branch scan found two `B`/`BL` sites to `a278360`: the conditional null-callback route from `a277c94`, and a call from `a27c5e8`. The latter selects an allocator entry from incoming `w0`; both of its direct callers pass index `0x21` (entry 33), not entry 0. No decoded fixup targets `a27c5e8`.

This closes only the reviewed direct-call and decoded-fixup scope. Indirect/runtime dispatch, class-0 runtime state, and physical allocation bounds remain unresolved. No device test, build, or install occurred. Documentation-only release; no IPA is included.

See `research-updates/2026-11-25-allocator-a278360-callers.md`.
