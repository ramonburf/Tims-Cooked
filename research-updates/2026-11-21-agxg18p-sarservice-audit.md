# AGXG18P and AppleSARService delta audit — bounded negatives

Date: 2026-11-21. Static analysis of the iOS 27.0.1 (build 24A446) and iOS 27.2
(build 24B119) kernel caches. No device or build host was reachable, so no probe
was run and nothing here is a runtime result.

## Scope

Two more changed kernel extensions were audited with the project's two-stage
cross-build pipeline (shape alignment, then a per-function shape re-check, then a
per-region instruction-mnemonic census). Both belong to the class of extensions
that plain index pairing cannot cover because their function counts differ
between builds, and both publish a user-client class:

- the GPU accelerator extension (`AGXDeviceUserClient` **3421** functions in the
  target build, **3442** in the newer one; 45 nominal index-paired changes)
- the radio power-management extension (`AppleSARServiceUserClient`, 1866 / 1876
  functions; 68 nominal changes)

The accelerator extension is the higher-value of the two: its user client is the
one user-client surface this project has measured as openable from a signed
sandboxed app on both test devices.

## Result

Alignment flagged 448 regions in the accelerator extension and 297 in the power
extension; the per-function shape re-check reduced those to **41 real edits** and
**29 real edits** respectively. Nearly all of both sets are register renaming,
stack-slot moves or refactors.

Three accelerator edits are fix-shaped and worth recording, though none is
promoted:

- Two unwind/retry routines gained a **second pending flag byte** in the state
  object, tested ahead of the flag the target build already tested, and their
  callback slot moved by one vtable entry. The shift is consistent with one new
  virtual method inserted into that class's method table.
- One branch of a lookup routine was rewritten to add an authenticated virtual
  call whose result is rejected when it exceeds a small threshold derived from
  an object field; the target build's corresponding branch performs no such call.

The accelerator extension's previously recorded channel-index out-of-bounds
helper is **not** inside any changed region, so it is unchanged upstream and
remains exactly where the earlier note left it.

## Reachability

No app-carried route is established for either extension. For the accelerator
extension, an earlier device measurement with this project's unsigned carrier
found that every command path accepting a channel index sits behind an exclusive
owner check and/or a private performance entitlement, and that the only
unprivileged selector command is a read-only status query. Neither the owner
check nor the unprivileged query's dispatch site lies inside a changed region;
the command-processing helper that does lie inside a changed region shows only
register/stack churn, with no new bound or flag predicate. The power extension
publishes a user client, but no open or entitlement result exists for its service,
so its reachability is simply unknown.

**Verdict: bounded reconnaissance / negative.** No out-of-bounds access, type
confusion, lifetime error, kernel read/write primitive, exploit or jailbreak is
established. Both surfaces are left closed absent a published user-client route
plus a measured open result.

Evidence and the full per-region census are held locally; this repository carries
no reproducer for these static observations.
