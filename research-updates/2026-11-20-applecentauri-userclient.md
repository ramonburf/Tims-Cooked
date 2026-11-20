# A changed user-client handler family in a kernel extension (static finding, iOS 27.0.1 vs 27.2)

Date: 2026-11-20
Builds compared: iOS 27.0.1 (kernelcache build 24A446, target) and iOS 27.2 (build 24B119, reference).

## What was done

The project keeps a census of which kernel extensions differ between the target build and
the next public release. Most entries in that census are ranked by an index-paired change
count, which is only meaningful for extensions whose function count is identical in both
builds. Filtering to those extensions leaves 48 candidates; one of them, a driver that
publishes an enumerable service and a user client, had never been examined.

The comparison used two independent passes so that address drift could not be mistaken for
code change: an alignment pass that flags rewritten regions, then a per-function check that
re-compares each flagged region's instruction *shape* (mnemonic, register operands, memory
base, with immediates masked). Shape-identical blocks are data-segment drift; only
shape-differing blocks are real edits.

## Result

The extension has the same function count in both builds, and the shape check reduces the
alignment pass's flagged blocks almost entirely to drift. Exactly one contiguous region
survives as a real edit: nineteen functions forming the extension's external-method
dispatcher and its handler bodies. Within that region, seventeen of the nineteen functions
differ at the instruction level.

In every one of those handlers, the newer build inserts the same three instructions ahead
of checks that already existed in the target build:

```
ldr  xN, [request_context, #8]
and  xN, xN, #0xfffffffffffffeff
str  xN, [request_context, #8]
```

That is: clear bit 8 of a per-request word before the selector and size gates run. The
same mask appears at the same position in all seventeen handlers. The newer build also
hoists the rejection-status constant into the handler prologue.

The user client itself is ordinary: it publishes a table of eight external methods through
the standard kernel dispatcher, and its open path requires a private entitlement string.
No device sweep has established whether an unsigned app can satisfy that entitlement or
open the service at all.

## What this is and is not

- **Observed:** a consistent code change confined to one handler family of one extension,
  in a user client gated by a private entitlement.
- **Not established:** what bit 8 of that request word means, who sets it in the target
  build, and whether any reachable input can leave it set in a way the newer build's clear
  prevents. No out-of-bounds access, type confusion, use-after-free or lifetime error was
  observed. The apparent size checks compare against two different constants, and which one
  bounds the caller-supplied structure length is not yet resolved.
- **No vulnerability, kernel read/write primitive, kernel code execution or jailbreak is
  claimed.** This is reconnaissance on a changed surface, not a candidate bug.

## Next steps

Resolve the dispatch-row field layout against a known thunk on this extension, determine
which constant bounds the caller's structure length, then trace the producer and consumers
of that request-word bit in the target build. Device work remains blocked because no
authorised host currently enumerates a device; nothing was executed on hardware.
