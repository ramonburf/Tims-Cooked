# Follow-up: that changed handler family is a DriverKit-style `Dispatch` override

Date: 2026-11-20
Builds compared: iOS 27.0.1 (kernelcache build 24A446, target) and iOS 27.2 (build 24B119, reference).
Companion note: [`2026-11-20-applecentauri-userclient.md`](2026-11-20-applecentauri-userclient.md).

## What this pass did

The earlier note found one contiguous region of real instruction-level edits in a driver
that publishes an enumerable service plus a user client: nineteen functions forming a
dispatcher and its handler bodies, seventeen of them changed. Each changed handler inserts
three instructions that clear bit 8 of a per-request word. That note left three things open:
the dispatch-row field layout, which size constant bounds the caller's input, and who
produces and consumes that request-word bit.

This pass resolves all three from code, and identifies what the changed virtual method is.

## Result

**The changed family is the driver's slot-12 virtual override, not the external-method
table.** The driver class's published class table puts the changed dispatcher at virtual
slot 12, with the same shared base-class bodies in slots 2 through 11 as its user-client
class. The user-client class keeps the kernel default for slot 12, which returns
"unsupported". A class's slot-12 body in this hierarchy was already identified in an
earlier, closed investigation as `IOUserClient::Dispatch(const IORPC rpc)`: it takes the
0x20-byte `IORPC` record by value (`message`, `reply`, `sendSize`, `replySize`,
`kernelContent`), and the generic base implementation copies those 32 bytes, takes the
provider object, and tail-calls slot 12 on it. The driver's override dispatches on the
message identifier inside the kernel-supplied content pointer and routes to its own method
bodies. So the seventeen edited handlers are this driver's own `Dispatch` methods.

**The two size constants are minimum `sendSize`/`replySize` thresholds.** In the newer
build the handler loads both size fields together and rejects when either is below its
constant. They are therefore per-method minimums on the RPC's declared send and reply
sizes, not scalar counts, and neither is a caller-controlled structure-length bound. The
open question from the earlier note is answered: there is no missing length check here.

**The inserted clear is the reserved message-flag bit.** The newer handler loads the
flags word from the kernel content pointer, clears bit 8, and stores it back before any
method-specific checks; the target build has no such store. Bit 8 is outside the public
RPC message-flag enumeration, so it is a private/reserved flag. This is the same mask, the
same position and the same idiom already recorded for the two other slot-12 `Dispatch`
overrides examined in the earlier closed cluster, where the change was classified as
hardening-shaped.

**The method-table field roles are now read from code, not inferred.** The kernel's
external-method dispatcher computes each row's address as base plus selector times the row
size, then compares the row's four scalar/structure count fields against the corresponding
argument-record fields before calling the row's entry point. The stride and field roles
quoted in the earlier note are confirmed by that code; rows whose counts read zero simply
impose no constraint.

## What this is and is not

- **Observed:** the changed instructions clear one reserved RPC message-flag bit ahead of
  pre-existing gates, in one driver's own `Dispatch` override, exactly like the closed
  cluster's overrides.
- **Not established:** any app-facing ingress. Slot-12 `Dispatch` sits behind the DriverKit
  RPC machinery, which an earlier bounded-negative pass found reachable only through a
  DriverKit-administrator-gated creation path; the driver's user client additionally
  requires a private entitlement on its open path. Whether the target build ever sets this
  flag bit, and what it gates, remain unknown.
- **No vulnerability, memory-safety effect, kernel read/write primitive, kernel code
  execution or jailbreak is claimed.** This is reconnaissance on a changed surface, and it
  agrees with the earlier closed verdict rather than reopening it.

No device probe was run: no authorised Mac currently enumerates a device, and the PC-side
USB device list is empty.
