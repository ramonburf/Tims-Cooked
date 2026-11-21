# Time-sync kernel extensions — delta audit (bounded negative)

Date: 2026-11-21. Target build 24A446 (iOS 27.0.1); comparison build 24B119 (27.2).
Static analysis only. No device probe was run and no panic-capable path was touched.

## Scope

Two kernel extensions were audited that publish user clients an ordinary app could in
principle open, and that no earlier equal-count sweep can cover because their function
counts differ between builds (so raw index pairing misaligns and every later pair is
meaningless):

| extension | functions, target / newer | publishes |
|---|---|---|
| gPTP plugin (`com.apple.plugin.IOgPTPPlugin`) | 1641 / 1619 | `IOTimeSyncDaemonUserClient`, `IOTimeSyncgPTPManagerUserClient` |
| TimeSync family (`com.apple.iokit.IOTimeSyncFamily`) | 1488 / 1474 | `IOTimeSyncClockManagerUserClient` and the daemon / filtered / edge-capture / edge-generate / network-port / gPTP client classes |

Method: cross-build shape alignment of whole function lists, then a per-function shape
re-check, then a per-block instruction-mnemonic census, then targeted instruction-level
diffs of the surviving regions.

## Result

Shape alignment flagged 195 regions in the gPTP plugin and 173 in the TimeSync family.
The per-function re-check reduced those to **12 real edits in each**; the rest are
register renaming, stack-slot moves, load merging, or address/data-segment drift.

The edit-shaped items found:

* **gPTP plugin — logging/virtual-call path.** A large routine that walks method slots
  gains a variable-format log call (a halfword counter increment, a signed-byte field,
  a 16-bit mask, and fixed format/type words) together with a pointer-authentication
  integrity check (`xpacd`/`compare`/trap) on the object whose method slot it then
  calls. The same integrity idiom already appears elsewhere in that same routine in the
  target build, so this is a codegen/log-path change, not a new bounds predicate.
* **gPTP plugin — null-guarded virtual call.** A separate region gains a null check on a
  state field followed by an authenticated indirect call, where the target build called
  unconditionally. Fix-shaped, but the owning class, the field's provenance and any
  reachability are unresolved.
* **TimeSync family — assertions.** A routine gains several state checks (a tested bit,
  a null check, a small-constant compare, a bitfield extraction from a state byte) that
  feed the platform's own assertion formatter (`Assert: %s (value 0x%lx %lu), %s file:
  %s, line: %d`). This is assertion/hardening churn, not a memory-safety bound.

No new comparison against a count or size field exists anywhere in either extension, and
no out-of-bounds access, type confusion, lifetime error or corruption effect is
established.

## Reachability

The reachable surface is gated by private entitlements in both builds:

* The gPTP plugin sets the IOKit user-client entitlements property to
  `com.apple.private.timesync.clocksync`.
* The TimeSync family carries the `com.apple.private.timesync.*` family —
  `.clocksync`, `.edge-capture`, `.edge-generate`, `.direct-userclient`,
  `.clock-testing`, `.tsn-capture`, `.ppmoffset`, `.reversesync`, `.getsyncinfo` — and a
  "missing entitlement" refusal message for nine user-client classes.

This is static evidence that the predicate exists, not a measured `IOServiceOpen`
refusal. It does mean these user clients are not ordinary-app-openable surfaces on the
evidence available.

## Verdict

Bounded reconnaissance / negative. No out-of-bounds access, type confusion, lifetime
error, kernel read/write primitive, exploit or jailbreak is established. No device
probe was run. This surface stays closed unless new service or entitlement evidence
removes the gate; a generic time-sync sweep should not be repeated without a changed
input or oracle.
