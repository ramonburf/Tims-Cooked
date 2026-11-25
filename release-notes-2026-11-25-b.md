# iOS 27 research checkpoint — 2026-11-25-b

This checkpoint corrects the allocator sentinel-path interpretation. The boot-prelude call requests size `0x100` with sentinel index `0xffff`; the creator's default-fill path normalizes counts through 39 to 40 and then uses dynamic index 40, not parser-selected entry 0. A bounded census of 96 direct creator sites found no constant-zero index; two dynamic sources were traced within their static contexts/callers, with no zero value found. Other indirect/generated paths and runtime state remain unverified.

The selector-5 `buffer+7` access remains a logical overread only. Entry-0 size/backing bounds and physical out-of-bounds effect are unresolved. Static analysis only; no device or method test, build, install, vulnerability, exploit, kernel read/write primitive, or jailbreak is established. No IPA is included.

See `research-updates/2026-11-25-allocator-sentinel-index.md` for the bounded details.
