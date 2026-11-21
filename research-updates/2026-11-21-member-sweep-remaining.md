# Remaining equal-count extensions audited — bounded negatives, plus three fix-shaped additions without established ingress

Date: 2026-11-21
Builds: iOS 27.0.1 kernelcache (build 24A446, target) and iOS 27.2 kernelcache (build 24B119, reference)
Scope: every member of the cross-build census whose function count is identical in both builds and which had not yet been examined — roughly thirty members, including all the remaining large ones
Device activity: none. No authorised host enumerated a device, so nothing here is a runtime result.

## Background

The census ranks changed extensions by an index-paired count of functions whose
instruction fingerprint differs. That count is only a ranking hint: address literals
inside untouched code change when a data segment moves, and register allocation alone
can make unrelated functions look rewritten. Every member here was re-checked per
function with immediates masked before any region was called real.

One tooling correction came out of this pass. The personality-extraction helper prints
a fixed field list and does **not** print `IOUserClientClass`, so an empty search of its
output says nothing about whether a member publishes a user client. All personalities
were therefore re-extracted from the kernelcache's prelinked information with that key
read explicitly, in both builds, before any reachability statement was made.

## The systematic idiom in this batch

Three members insert the same three-instruction sequence at the top of a validation
prologue, ahead of pre-existing checks:

```
load  a per-request word
and   it with ~0x100     (clear bit 8)
store it back
```

It appears thirteen times in one dispatch-sized routine in the packet-capture driver,
and across a family of roughly eight functions in the PCI extension and thirteen in
the firmware-kit extension. This is the same reserved message-flag bit-8 hardening
already recorded for the kernel's slot-12 `Dispatch` overrides elsewhere in this
project. Clearing a reserved bit is defence-in-depth: it neither grants nor removes an
attacker capability unless that bit was load-bearing, and no such provenance was
established. Recorded as reconnaissance, not a vulnerability.

## Fix-shaped additions (ownership and app ingress unresolved)

* **Secure-element control extension.** One routine gains two behaviour changes in the
  newer build: it accepts an additional return status from a preceding call, and it
  newly rejects a request when a stack byte equals a specific small constant. The
  extension does publish a user-client class, but the entitlement gate on that client
  and the meaning of the compared byte are both unresolved, and the enclosing routine
  could not be tied to a user-client method. Reconnaissance only.
* **Disk-image device extension.** A routine gains an explicit pointer-authentication
  verification (authenticate, strip, compare, trap) plus a flag store in a list walk.
  The extension publishes a device-creator user client. Whether the target build's
  corresponding path lacked the authentication check — which would make this a real
  fix — is unresolved, because the target implements the same loop differently.
* **Wireless-charger management extension.** A log path naming an inductive
  out-of-box-pairing state was inserted. Log-only, no decision logic observed.

## Everything else

The remaining members reduce to rebase drift, register renames, stack-frame changes or
refactors with no bounds, length or lifetime predicate seen to change. Two examples
worth recording so they are not redone: a report-hub constructor in the metrics
extension gained an object store plus a boolean return (a refactor, not a guard), and
a power-management routine masks an already-clamped length with `0xff`, which has no
effect because the length is clamped well below 256 first.

## Assessment

No out-of-bounds access, type confusion, lifetime error, kernel read/write primitive or
jailbreak is established, and no percentages were re-scored. These members should not
be reopened without a newly published user-client route, a concrete changed bound or
length check tied to an app-callable entry point, or runtime evidence from a device.
Device work remains blocked because no authorised host currently enumerates a device.
