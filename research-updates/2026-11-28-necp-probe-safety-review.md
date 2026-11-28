# NECP probe safety review — 2026-11-28

## Scope

Static review of the NECP probe source against the exact iPhone18,1 / iOS 27.0.1 build `24A446` kernelcache, plus a host-only syscall-mocked run. No device was contacted, and no install, launch, or real NECP syscall was performed.

## Verified observations

- Exact-build dispatch shows that the probe's selected action routes to a different handler from the candidate it was intended to assess. Upstream enum labels are not treated as proof of exact-build semantics.
- A separate candidate handler's optional-buffer branch requires an exact fixed-size buffer and copies that fixed amount in and out. Its core helper runs before that branch; helper dataflow and ordinary-app reachability remain unresolved.
- The host mock was built with syscall calls redirected to a stub. Symbol inspection confirmed the mock entry point and absence of a real syscall reference in that binary; execution exercised userspace control flow only.

## Assessment and limits

This review does not establish a vulnerability, memory corruption, kernel read/write primitive, exploit, or jailbreak. The mock is not evidence about kernel behavior. The selector mismatch and unresolved helper/reachability analysis mean that changing the action or buffer and running the probe on a device is not justified. A device test remains gated on complete exact-build dataflow, credible ordinary-app ingress to the exact path, an independent oracle, and a reachable authorized host.

## Next work

Continue bounded static analysis of the helper and parser/reachability path. Keep any future mock run host-only and verify that the binary contains no live syscall reference. Reconsider device testing only if every gate above is independently satisfied; stop on unexpected crash or service failure and preserve evidence.
