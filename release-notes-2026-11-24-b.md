# iOS 27 research checkpoint — IOSurface binary parser parent-seeding limit (all explicit modes)

Exact-build static review of `iPhone14,2` / iOS 27.0 build `24A5390f` expands the earlier selector-0 direct-factory negative. The binary parser initializes its current-parent slot and parent-stack state to zero. Its only indexed parent-stack write stores either zero or the current parent; parent classification requires an existing non-null stack entry. Callback returns do not seed the parent-stack write. The apparent counterexample was an object-table insertion, not a parent-stack entry.

The whole-cache census found that all seven IOSurface calls to the relevant import stub set `x2=0`. Seven other importer calls have stack-derived `x2` and unresolved `w4`; callback execution is not established for them. Decoded chained fixups are on-disk evidence, not proof of live pointer installation or runtime calls. The nested `OSDictionary → IOSurfacePlaneInfo → OSArray` graph cannot be supplied through this parser's explicit parent-stack mechanism. Ordinary-app reachability and the separate text-parser route remain unresolved.

No device method or selector was called. No vulnerability, memory corruption, kernel read/write primitive, exploit, or jailbreak is established.

The attached `TimsCooked-v0.6.ipa` is reused unchanged from the preceding checkpoint (SHA-256 `dd7a4680155fd738d5b279bf0da3e8debf385a0cf44d8636a0c35a3e1039ce50`); it is not a new carrier build. The original archive's sanitation was previously rechecked: neutral bundle identifier, no embedded provisioning profile, ad-hoc signature, no entitlements, and no source-backup files. It requires re-signing and provisioning before installation.
