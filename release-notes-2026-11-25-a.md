# iOS 27 research checkpoint — allocator-init callback cell (static, bounded)

Exact-build static review of `iPhone14,2` / iOS 27.0 build `24A5390f` found three direct reads of an optional `__DATA_CONST` callback cell across 82 exact function intervals and no direct store in the bounded ADRP-derived scan. All three readers null-check before their authenticated indirect call. The cell is zero on disk and has no decoded chained-fixup entry; that does not prove its live value or exclude indirect/alias writes and loader-time mutation.

The exact init registry decoded to 3,353 records and 106 unique callback starts, with no decoded non-starts. This narrows one early-init indirect path but does not prove allocator runtime state. The class-0 size/backing extent and the parser's logical `buffer+7` load's physical bounds remain unresolved.

No device test, method/selector call, build, or install was performed in this follow-up. No vulnerability, memory corruption, kernel read/write primitive, exploit, or jailbreak is established.

No IPA is attached: this checkpoint is static-only; no new app binary was built or inspected.
