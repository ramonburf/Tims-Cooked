# IOSurfaceRoot client-construction path — iOS 27.0 (24A5390f)

Date: 2026-11-22
Target: `iPhone14,2`, iOS 27.0, build `24A5390f`
Kernelcache SHA-256: `6719422222a3b68120f663b2113272b5bcf48d648afe892bbce23b8460ba47dd`

Scope: exact-build static disassembly. No IOSurface open-only app test or external-method selector was run on this build.

## Static result

The target `IOSurfaceRoot` instance vtable has a service-specific new-client hook at slot `+0x468`, resolving to `0xfffffff009c3ea98`. The routine clears its output pointer, accepts client type 0 and rejects nonzero types, resolves the `IOSurfaceRootUserClient` metaclass, and constructs a client. Constructor and metaclass references independently tie the class to the `IOSurfaceRootUserClient` name.

Client construction is conditional: initialization methods must succeed before the routine publishes the client through its output pointer. The entitlement-dependent initializer and two additional gates are visible in the call sequence, but the policy semantics of those gates have not been established. The external-method wrapper also has mode-dependent dispatch tables; static table presence alone does not show which methods an ordinary app can reach.

## Reachability and limits

This establishes a target-binary service-hook-to-client-class link. It does **not** establish that a sandboxed app's `IOServiceOpen` reaches the hook, that the construction gates permit an ordinary app, or that any particular method is app-reachable. The upstream userland/MIG open path and sandbox policy remain untraced. The isolated open-only app build was unsigned and not installed; no device runtime result exists for this path.

No vulnerability, memory-corruption effect, kernel read/write primitive, exploit, or jailbreak is established. No selector was invoked.

## Next checks

Trace the userland/MIG open path and the service-open policy on this build; resolve the two client-construction gates; then, only after a signed isolated build and a fresh data-preserving backup, run a single type-0 open/close test with zero method calls. Any method or race test remains gated on those results.

## Checkpoint artifact

The accompanying research release reuses the previously verified sanitized `TimsCooked-v0.6.ipa` unchanged (SHA-256 `dd7a4680155fd738d5b279bf0da3e8debf385a0cf44d8636a0c35a3e1039ce50`). It is not a new app build and is not a jailbreak.
