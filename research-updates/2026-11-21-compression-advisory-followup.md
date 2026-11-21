# Compression advisory follow-up — the decmpfs zlib decompressor

Static comparison of iOS 27.0.1 (build 24A446) against iOS 27.2 (build 24B119).
No device probe was run; this note records reconnaissance only.

## Which component the advisory means

The iOS 27.2 security notes list, under **Compression**, CVE-2026-113910: *"An app may
be able to disclose kernel memory — a memory initialization issue was addressed with
improved memory handling."* The same page's additional-recognition section names
**AppleFSCompression**. In the kernelcache the corresponding fileset member is
`com.apple.AppleFSCompression.AppleFSCompressionTypeZlib`, and its own embedded strings
identify it as the chunked **decmpfs** decompressor: `register_decmpfs_decompressor`,
`com.apple.ResourceFork`, chunk-count and resource-map validation, `invalid zlib header`,
`decode failed for compression algorithm 0x%x`.

The platform publishes one personality for it — `IOProviderClass=IOResources`,
`IOResourceMatch=IOBSD` — and **no user-client class** in either build. There is therefore
no `IOServiceOpen` route; the entry point is the BSD/VFS layer transparently decompressing
a file whose decmpfs/resource-fork extended attributes describe chunked compressed data.
That matters for reachability: an app can set extended attributes on files inside its own
container, so attacker-authored compressed bytes are a plausible kernel input. This run did
not measure that path.

## What changed between the builds

Alignment flags 4 address/data-segment drift blocks and 11 real edits. The substantive one
is the decode path itself:

| 27.0.1 | 27.2 |
|---|---|
| driver `0xfffffe0008b90a1c` (`0x4a0` bytes) plus helper `0xfffffe0008b915c8` (`0x6f8`) | one function `0xfffffe0008bce5cc` (`0xba4` bytes) |

The two routines were rewritten and merged into a single function about 1.8 KB larger. A
naive reading of the alignment output calls this a *deleted* function; it is not deleted —
every diagnostic string survives in the newer build and its referencing function is the
merged one. That is worth recording as a tooling caveat: when one build splits a routine
and the other merges it, an ordered-fingerprint aligner reports the leftover body as a pure
deletion.

The remaining edits are small: an extra conditional branch and trap in one routine, three
extra compares in another, a handful of bound/log-form changes elsewhere, and a NEON
(`addv`/`cnt`) block whose surrounding code is unchanged in structure.

## Why no specific fix is claimed

Because the decoder was reimplemented wholesale rather than patched in place, an
instruction-shape diff cannot isolate the "memory initialization" change described by the
advisory: a rewrite and a targeted hardening patch look the same at this granularity. No
uninitialised-copy-out site was identified, no bounds or lifetime defect was confirmed, and
no app-carried trigger was validated.

## Verdict

Bounded reconnaissance / negative. No out-of-bounds access, type confusion, lifetime error,
kernel read/write primitive, exploit or jailbreak is established.

## Next step

Device-gated. On a host that enumerates the test phones: confirm that an ordinary app can
place a decmpfs-compressed file in its container and reach the decompressor on read, then
compare the decompression work-buffer length against the number of bytes copied out — the
exact quantity a memory-initialisation fix would change. A generic decompression stress
test would not answer that question.
