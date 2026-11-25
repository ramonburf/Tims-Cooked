# iOS 27 research checkpoint — 2026-11-25-c

An expanded exact-build static census examined references and stores associated with allocator entry-table page `0xfffffff00ad38000` on `iPhone14,2` / iOS 27.0 build `24A5390f`. It covered 21,072 exact function starts and 2,285,568 decoded instructions. The broader page-derived scan found only the two already-known generic-creator `+0x34` fresh-entry writes; no additional page-rooted size writer was recovered. A global offset census produced many unrelated register-based candidates, and receiver provenance remains unresolved for those paths.

The selector-5 `buffer+7` access remains a logical overread only. Class-0 runtime size, allocation capacity, and mapping are unknown; indirect/generated paths and runtime mutation are not excluded. Static analysis only: no device test, selector/method call, build, or install occurred. No vulnerability, memory corruption, kernel read/write primitive, exploit, or jailbreak is established. No IPA is included.

See `research-updates/2026-11-25-allocator-entry-writer-census.md` for scope and candidate triage.
