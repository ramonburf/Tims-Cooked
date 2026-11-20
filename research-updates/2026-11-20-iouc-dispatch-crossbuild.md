# The user-client dispatch path is named, and it is unchanged upstream

Date: 2026-11-20
Builds: iOS 27.0.1 (24A446, target) vs iOS 27.2 (24B119, reference)
Device work: **none.** No authorised Mac currently enumerates a device, so this
pass is static binary reading only.

## Why this pass happened

The previous checkpoint on the generic user-client entitlement gate left one
item open: the large dispatcher that references the internal method-shim name
strings had no discovered caller and no pointer slots, so "indirect entry" was
not yet a named mechanism, and the registering routine table had not been found.
This pass resolves that by identifying the function rather than by finding a
table.

## Result

**The dispatcher is the kernel's generic user-client external-method
dispatcher.** Its body validates an entry from a user client's method-dispatch
description against the call's argument record — comparing the declared scalar
input count, structure input size and scalar output count with the values the
caller supplied — and then calls one of several marshalling shims selected by
the method's flavour. That is exactly the role already recorded in this
repository for the image-codec extension's method table, so the earlier
observation that the codec's dispatch entries are consumed by a shared kernel
core is now confirmed as the ordinary user-client mechanism rather than a
one-off.

**The shim-name consumer sits directly beneath it.** The four
`shim_io_connect_method_*` literals are referenced from inside a single
function that switches on method type, and that function is called from the
dispatcher. This was previously read as an unresolved pair at the "top of the
RPC shim dispatch"; it is now placed as one level below the external-method
dispatcher.

**No stored pointer of any scanned encoding reaches the dispatcher.** A whole
multi-extension raw search for arm64e authenticated pointer slots returns
nothing for it in any data segment, including the boot data segment, and a
full-width address search and a relative-offset search also return nothing; a
positive control in the same run reproduces a known slot. The reference is
therefore either a chained-fixup entry the decoder misses or a table built at
runtime. That is recorded as a tooling gap, not as evidence that the routine is
dead: the routine plainly validates live argument records and calls live shims.

## Bounded negative: none of this changed in 27.2

Every function in the family was paired with its counterpart in the reference
build and compared as a masked instruction stream (mnemonics and operands with
immediates normalised). The external-method dispatcher, the entitlement gate,
the request/reply handler that calls the gate, its five sibling handlers, the
two class-membership helpers, and the object-lookup helper are all present at
the same size with identical instruction streams.

The practical consequence is narrow but useful: the most app-reachable surface
in the kernel image — how a sandboxed app's method call is validated and
marshalled into a kernel extension, and where the entitlement gate is applied —
carries **no 27.0.1-to-27.2 fix**. There is nothing here to adopt as a
candidate, and the earlier reading that these routines have "no ingress" should
now be stated more precisely: no *other* caller exists in these scans, but the
path is reachable by construction through ordinary user-client method dispatch.

## What this does and does not change

* It closes the previous checkpoint's open item and retires the plan to hunt
  for a boot-built registration array.
* It does **not** reopen any candidate path, and it does not weaken any earlier
  bounded negative: the entitlement gate still enforces, and nothing in this
  family reads or writes attacker-controlled memory.
* No vulnerability, kernel read/write primitive, kernel code execution, or
  jailbreak is claimed. Device work remains blocked because no authorised build
  host currently enumerates a device.

## Next step if resumed

Leave this cluster closed. The next static step should come from a different
lead; device work waits on a host enumerating the phones.
