# iOS 27 allocator callback-slot audit — 2026-11-25

A follow-up exact-build static audit traced the class-0 consumer's null-callback branch and reviewed 50 candidate stores against the callback qword's full width. The apparent `+0x42` overlap is a four-byte default-fill store at `+0x3c`, ending at `+0x40`; no callback-qword overlap was found in that bounded set. Among 513,607 decoded fixups, none targets the generic creator or `a273b18`; two target the known size helpers for entries 1 and 2.

These are bounded on-disk/static results. Live callback state, class-0 size, allocation extent, and mapping remain unresolved. The selector-5 `buffer+7` access is still a logical overread only; no vulnerability or jailbreak is established. No device test, build, or install occurred. Documentation-only release; no IPA is included.

See `research-updates/2026-11-25-allocator-callback-slot-audit.md`.
