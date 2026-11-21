# APFS `jobj_validate_key_val` — identity established, delta corrected, no app ingress

Date: 2026-11-21 · Builds: iOS 27.0.1 (24A446, target) vs iOS 27.2 (24B119)
Device work: **none** — no authorised Mac enumerated a device and no iPhone was
attached to the Windows workstation. All results are static binary reading.

This note follows up the [APFS member audit](2026-11-21-apfs-member-audit.md),
which localised three input-validation predicates added in the newer build but
left their routine and field provenance unnamed. The strongest of the three is
now identified, and the earlier description of exactly what the newer build
added is corrected below.

## Identity

The routine is **`jobj_validate_key_val`** — a key/value record validator in the
extension's on-disk object layer (`jobj.c`). The name comes from the platform's
own embedded function-name strings used by its assertion machinery: the routine
references the string `"jobj_validate_key_val"`, and the newer build's
counterpart references the same name. Neighbouring function-name strings in the
same cluster (`make_jkey_from_jobj`, `jobj_to_key_val`, `key_size_for_jobj`,
`val_size_for_jobj`, `jobj_release`) place it among the jobj serialization and
sizing helpers.

It takes a key pointer, a key length, a value pointer and a value length,
dispatches on the top nibble of the key's first word (the APFS object-type
field), and for each type checks that the declared key and value sub-field
lengths fit inside the buffers before the record is used. Failures return a
small error code; success returns zero.

## Corrected delta

The earlier audit said the newer build "additionally requires the value to fit
within the remaining buffer". That relation is **already present in the target
build** — both builds compute `value_length - 4` and compare the 16-bit field at
value offset +2 against it through a shared branch. The changed branch is one
case of the type dispatch; relative to the target build, the newer build adds
exactly two predicates:

- an **upper cap of `0x2f` (47)** on that 16-bit field;
- a requirement that **bit 0 of the value's flags halfword be clear**.

This is the same reserved-flag hardening idiom already recorded elsewhere in
this project (the message-flag bit-8 clears in several driver families): the
newer build rejects records whose reserved flag is set and whose length-like
field exceeds a small constant.

## Callers

Every caller found is inside the same extension and belongs to a
**record-read / deserialization** path:

- the enclosing routine's own assertion strings name it as
  `key_val_to_jobj` / `large_key_val_to_jobj` — the conversion from a raw
  key/value pair to an in-memory object;
- callers of that conversion include routines named by their own assertion
  strings as `make_dirent_iterator` (directory iteration), `lookup_jobj_ext`
  (object lookup by key) and the spec-telemetry handlers;
- another caller block names `apfs_volume_fixup` together with several inlined
  `fixup_*` helpers, and a further one references a directory-iteration case
  routine;
- one comparator routine calls the validator with a null value pointer, so it
  never reaches the value checks at all.

In other words, the bytes handed to the validator are key/value records read out
of b-tree nodes. No API was found that lets a caller supply those buffers.

## What is not established

- **Object type of the changed case.** Its key shape (a 16-bit name length at
  key offset +8, with a minimum key length of ten bytes) is consistent with a
  name-bearing APFS key such as an extended-attribute key, but the numeric
  type was not resolved against a published enumeration.
- **App-controlled input.** Whether any caller can be made to validate
  attacker-chosen bytes through this branch is unproven; no syscall, `vnode`
  operation or ioctl supplying raw jobj records was found.
- **Downstream consumer.** What reads the capped length field after validation,
  and whether the cap closes a real memory-safety gap there, is unknown.

## Verdict

**Bounded reconnaissance / negative.** A real, deliberately tightened validation
predicate exists in 27.2 and the routine behind it is now named, but every
caller is a metadata-read path over on-disk volume structures, and no
sandboxed-app route to it was established. Nothing here is a vulnerability, a
kernel read/write primitive, an exploit or a jailbreak, and no device probe was
run. Readiness percentages are unchanged.

## Next step

Leave this surface closed unless a caller chain is found that hands
app-controlled bytes to `jobj_validate_key_val`. The remaining un-audited
equal-function-count members and the other two APFS predicates stay open; device
work remains gated on an authorised host enumerating a phone.
