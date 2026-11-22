# IOSurface notification dispatch follow-up — static

**Date:** 2026-11-22
**Target:** iPhone14,2, iOS 27.0 build `24A5390f`
**Comparison:** iPhone14,2, build `24B119`
**Scope:** Exact-kernelcache static analysis only. No selector call, device test, install, or build was performed for this update.

## Result

The IOSurface external-method wrapper is now linked to its generic dispatcher and mode-dependent method tables in both exact-product caches. The dispatcher uses the incoming selector as a bounded table index. One client-mode branch maps notification registration and per-key removal to their handlers; the alternate branch maps those entries to stubs. The mode byte is populated by an entitlement-related initializer check.

In the newer comparison build, client teardown sets a marker while holding the list lock, and notification registration checks that marker under the same lock. This is consistent with preventing registration from inserting a node after teardown unlink. The per-key removal handler does not set the teardown marker, so this comparison does not establish that every re-registration sequence is blocked.

## Limits

This is a static dispatch and patch-site mapping, not a reproduced race or memory-safety finding. Ordinary-app service open, the live client-mode value, and callback/client-free ordering remain unverified. Authenticated table pointers were mapped using their low-32 file-offset values into executable ranges; chained-fixup metadata was not independently decoded.

No use-after-free, kernel-memory corruption, kernel read/write primitive, exploit, or jailbreak is established. No device method was invoked.

## Cache identities

- Target: `24A5390f`, SHA-256 `6719422222a3b68120f663b2113272b5bcf48d648afe892bbce23b8460ba47dd`.
- Comparison: `24B119`, SHA-256 `eca347bf3b221b3e048a5ef7a7988cf2db46b4be895483d90e11281729865561`.
