# iOS 27 allocator caller census — 2026-11-25

A full exact-fileset direct `B`/`BL` scan covered 252 images, 255 executable segments, 176,646 function intervals, and 10,787,442 instructions. It found exactly two sites to `a278360` and two to `a27c5e8`, all within `com.apple.kernel`; no other fileset image directly branches to either target. Both direct callers of `a27c5e8` pass index `0x21` (entry 33), not entry 0. The pinned decoded-fixup map has no target to `a27c5e8`. A separate kernel scan found no `ADR` reference to its VA and no `ADRP` reference to its containing page; these are bounded reference-form negatives only.

Indirect calls, arithmetic/data-derived targets, runtime-generated dispatch, live class-0 state, and physical allocation bounds remain unresolved. No device test, build, install, or selector/method call occurred. Documentation-only prerelease; no IPA or binary assets.

See `research-updates/2026-11-25-allocator-a278360-callers.md`.
