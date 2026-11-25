# Progress tracker

Last updated: 2026-11-25.

A bounded 2026-11-25 device batch on iPhone18,1/build `24A446` completed a userland self-memory control, one ANE service open without a selector call, and decmpfs filesystem-ingress attempts with no data-bearing readback; decoder entry remains unproven. No component percentage changes: no kernel read/write primitive or jailbreak was established. See `research-updates/2026-11-25-device-probe-batch.md`.

Percentages mean "how far along that component is toward being a working part of the chain",
not "probability it will work". 100 % means done and verified on hardware.

## Chain stages

| # | Stage | Component | Status | % |
|---|-------|-----------|--------|---|
| 1 | Target acquisition | Exact kernelcache for current `iPhone14,2` target build 24A5390f plus 24A446 / 24B119 comparison builds | Complete | **100%** |
| 2 | Reachability map | Sandbox-app reachability of AGX / IOHID / IOSurface / WebKit daemons / network socket families | Complete (AGX sweep, iokit enumeration, crash corpus, `--rawsock` both devices) | **96%** |
| 3 | Vulnerability ID | Whole-kernelcache diff 27.0.1 → 27.2 (91 kexts, 542 changed kernel functions) mapped to CVEs | Complete | **90%** |
| 4 | Kernel r/w primitive | Socket UAF lead (CVE-2026-112514 mapping unverified) | **Unvalidated.** Historical peer-delivery/UDP events are ambiguous: `entered` increments before `sendmsg`, then the target fd closes before reclaimer allocation, so ordinary fd reuse can explain them. No UAF or kernel R/W established. | **5%** |
| 4b | Kernel r/w primitive | IOSurface notify UAF family (CVE-2026-112517 / -112516 / -112477) | Identified; PAC / type-confusion constraints unresolved | **25%** |
| 4c | Kernel r/w primitive | IOHIDFamily OOB r/w (CVE-2026-112507) | Patch confirmed in the diff; no sandbox-openable HID class found | **20%** |
| 4d | Kernel r/w primitive | Other diff-derived kernel UAF candidates | Triage list produced; unconfirmed | **15%** |
| 4e | Kernel r/w primitive | `uipc_mbuf2.c` mbuf-chain length arithmetic (`m_sum16` / `m_adj_sum16`, four 32→64-bit sites confirmed changed in 27.2) | Functions identified and fully caller-mapped; several callers pass underflow-capable header-field differences. Raw sockets are denied to apps on both devices, so the path is **remote-only (`AV:N`), not app-reachable**. Keep as a bounty candidate | **30%** |
| 4f | Kernel r/w primitive | `PF_ROUTE` raw route socket from the app sandbox | **Characterised (2026-11-14): reads work, writes are `EPERM`.** `RTM_GET` returns real `rt_msghdr` records with sockaddr arrays; `RTM_ADD`/`RTM_DELETE` both fail with `EPERM`; malformed `sa_len` is rejected with `EINVAL`. iOS 27's `struct rt_msghdr` is **0x5c**, not the published 0x54. The changed `bsd/net/route.c` helper is encode-side only (called from two notification encoders fed by ifnet/ifa state), so its 27.0.1 `VERIFY` cannot be driven by message contents. Information channel, **not** a kR/W path | **35%** |
| 4g | Kernel r/w primitive | VM deferred-reclamation MIG surface (`mach_vm_deferred_reclamation_buffer_{allocate,flush,resize,query}`) | **Measured (2026-11-14): kernel implements it, app cannot call it.** `osfmk/vm/vm_reclaim.c` is compiled in (five functions at `0xfffffe000acd9aa8`-`0x...cebc`, 43 log-string refs) and the MIG routine names/order match `mach_vm.defs`. But `dlsym` on the device resolves **none** of the four routines (nor `mach_vm_reallocate`); `_mach_vm_deallocate` resolves as a control, so the negative is real. No vm_reclaim function changed between 24A446 and 24B119. Gate tunable `vm_reclaim_max_threshold` defaults to 0 and its name string is absent from the image. **Closed for app-carried work** unless a future SDK exports a stub | **15%** |
| 4h | Kernel r/w primitive | **UPL/page-validation change in `vm_pageout.c` / `iopl_valid_data()`** — five functions changed 27.0.1→27.2 between `0xfffffe000acd1e18` and `0x...8e50`, above the type wall and on the file-I/O path | **Partially resolved (2026-11-14).** The headline claim that 27.2 *adds* a DART/SID/APF validation call is **refuted**: 27.0.1 already calls it (`bl 0xacd3ca8 -> 0xad3ff9c`, sz `0x1a88`) behind the same `[obj+0xa6]` tag gate, and both builds touch an identical set of 18 `vm_object` offsets. The real delta is removal of one `internal`-bit gate around a ledger-accounting call plus a deleted page-grab statistics block — refactor-shaped, and `iopl_valid_data` remains panic-only (**DoS ceiling**). Its caller is identified: `0xb347a08` in `IOMemoryDescriptor.cpp` (direct `BL` at `0xb347c20`), itself dispatched via a runtime pointer. No device run justified | **25%** |
| 5 | Build / deploy pipeline | macOS + Xcode → signed `.app` → `devicectl` install → launch on device | Working end-to-end | **100%** |
| 6 | EL1 code exec past PAC/CTRR/SPTM (TXM trustcache) | Required after kernel r/w before any persistent code runs | Not started | **5%** |
| 7 | Credential patch + rootless bootstrap (package manager) | Final stage | Not started | **5%** |

**Overall: not re-scored.** The earlier ~31% included unsupported socket-race progress and is superseded by the fd-reuse correction. Target acquisition, reachability mapping, and the build pipeline are substantially complete, but no kernel read/write primitive is verified and downstream stages remain untouched.
Per-path percentages are in `JAILBREAK-PATHS.md`.
The current target-build IOSurface static note links the service hook to `IOSurfaceRootUserClient`; app-level open, initialization-gate policy, and method reachability remain unresolved. See `research-updates/2026-11-22-iosurface-client-construction.md`.

## Confirmed 27.0.1 → 27.2 fix sites

- `com.apple.iokit.IOSurface` — exactly two changed functions: a dying-flag check
  (`ldrb` / `tbz`) at `+0xf1` and the teardown `strb`. Matches the notify-UAF family.
- `com.apple.iokit.IOHIDFamily` — four accessors gain `cmp` + `b.ge` + a count load
  (CVE-2026-112507).
- `com.apple.kernel` — 542 changed functions; a cluster of new state-byte checks
  (`ldrb` + `tbz`/`tbnz`) are candidate UAF fixes for kernel CVEs not yet mapped.
- The CVE-2026-112514-to-socket-function mapping remains **unverified**. The target 24A446
  `sbunlock` candidate already contains `so_usecount`/defunct-state checks; this does not
  establish a 27.2-only fix or CVE linkage. See `research-updates/2026-11-20-socket-fd-reuse-erratum.md`.

## Build and deploy pipeline

1. Build the carrier on macOS with Xcode:
   `xcodebuild -destination generic/platform=iOS -allowProvisioningUpdates`.
2. Install onto the attached device:
   `xcrun devicectl device install app --device <udid> <path-to-.app>`.
3. Launch with a mode argument and capture the console, e.g.
   `xcrun devicectl device process launch --device <udid> --console --terminate-existing \
    <bundle-id> --sockprec`.
4. Logs appear both on the console and in the app's own container.

Signing uses a standard development provisioning profile. Its details (bundle identifier,
team, expiry) are environment-specific and are deliberately omitted from this repository —
substitute your own.

## Immediate next step

The socket lead is unvalidated because its historical peer-delivery oracle does not exclude
ordinary fd reuse; do not spend device cycles on the old trigger until an fd-pinned control
exists. The mbuf checksum lead is closed as app-reachable work (raw sockets are denied); and `PF_ROUTE` is now characterised as a
**read-only** interface (`RTM_GET` works, `RTM_ADD`/`RTM_DELETE` return `EPERM`) — an
information channel, not a primitive. Priorities:

1. **UPL/page-validation change (4h) is partially resolved** — the claimed "27.2 adds
   DART/SID validation" is refuted; both builds have it, with identical `[obj+0xa6]`
   gating and an identical 18-field `vm_object` access set. What actually changed is
   one removed `internal`-bit gate in `iopl_valid_data` plus a deleted page-grab
   statistics block, and `iopl_valid_data`'s caller is now named
   (`0xb347a08`, `IOMemoryDescriptor.cpp`). It stays panic-only (**DoS**), so no device
   run is warranted. See `analysis/krw-leads/upl-dart-not-a-272-addition-2026-11-14.md`.
   Next if reopened: name the two 27.2-only helpers `0xad2586c` / `0xad37930`.
2. **Identify the CVE-2026-112576 guard helper** `0xfffffe000acbabd8` and the setter of
   `[obj+0x75]` bit 1 before any further CoW device work.
3. **Use `tools/opencode-temp/kc_fstarts.py` + `kc_norm_diff.py` + `kc_align_region.py for
   all future 27.0.1↔27.2 comparisons**; the method is exact and removes relocation noise.
4. **The VM deferred-reclamation surface (4g) is closed for app-carried work** — iOS
   exposes no client stub for `mach_vm_deferred_reclamation_buffer_*`, measured on both
   devices. Re-open only if a future SDK `.tbd` exports one of them.
5. **Re-examine leads above the type-isolation wall** rather than grooming the socket slot
   further: APFS error-propagation panics need non-ordinary failure conditions, and
   IOSurface external-object routes remain PAC-constrained.

Evidence: `analysis/kernelcache-funcstarts-exact-diff-2026-11-14.md`,
`analysis/socket-uaf-crosstype-2026-11-14.md`, `analysis/socket-uaf-stale-write-2026-11-13.md`,
`analysis/krw-leads/network-surface-reachability-2026-11-14.md`,
`analysis/krw-leads/pfroute-characterisation-2026-11-14.md`, and `HANDOFF.md`.
