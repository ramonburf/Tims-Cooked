# Advisory-driven member audit — iOS 27.2 security notes cross-walked to the kernelcache

Date: 2026-11-21
Builds: iOS 27.0.1 kernelcache (build 24A446, target) and iOS 27.2 kernelcache (build 24B119, reference)
Scope: members that publish a user-client class and were skipped by every equal-function-count sweep
Device activity: none. No authorised host enumerated a device, so nothing here is a runtime result.

## Method

Instead of ranking un-audited members by their nominal change count, this pass used Apple's own
iOS 27.2 security notes as the target list. The notes were parsed into component, CVE, impact
and description, then each kernel/IOKit component was matched to the fileset member that
implements it. Two consequences are worth recording:

* A user-client census was extracted directly from the kernelcache's prelinked information,
  reading the `IOUserClientClass` key explicitly. Both builds publish **87** user-client
  personalities, with an identical set. Earlier helpers never print that key, so any reachability
  claim built on their output alone is unsupported.
* Several advisory components do not correspond to a standalone changed member in this cache
  (for example the framebuffer and HFS entries), which means the cross-walk itself filters the
  sweep.

Advisory-backed kernel-memory surfaces remain the Neural Engine extension (two
app-may-corrupt-kernel-memory out-of-bounds writes) and the video-encoder extension (eight
entries spanning out-of-bounds read/write and kernel memory corruption). Both already have an
audit and a measured or closed reachability result in this repository, so they were not re-run.

## Results

| member | funcs (target/newer) | flagged regions | drift / real | verdict |
|---|---|---|---|---|
| EXBrightKext | 585 / 599 | 81 | 59 / 22 | bounded negative |
| ASIOKit | 98 / 97 | 15 | 8 / 7 | bounded negative |
| AppleFSCompressionTypeZlib | 67 / 66 | 15 | 4 / 11 | reconnaissance, unranked |

### EXBrightKext — display-brightness user client

The only changed function on the user-client path is the client's own external-method
dispatcher. Three edits are fix-shaped but none is a bounds predicate on caller-controlled
data: one virtual call changes a fixed argument from `0x1000` to `0`; two results that the
target build dereferenced unconditionally gain a null check; and one release call present in
the target is gone. The per-selector handlers behind the brightness, indicator-state,
ALS-calibration and SIL-debug server methods are not inside any changed region. Everything
else is address rebase plus field shifts caused by one new field in the driver object.

### ASIOKit — obfuscated blob dominates the diff

One changed region grows by about 115 KB with thousands of XOR/multiply/multiply-add
operations, table indexing and computed authenticated jumps: the known per-build-key
obfuscated crypto/VM blob being rebuilt under fresh constants, not a fix cluster. The
remaining edits add pointer-authentication instrumentation. This member should not be ranked
by shape-delta size at all.

### AppleFSCompressionTypeZlib — rewritten inflate region

Eleven real regions. The largest adds a long run of range comparisons, many calls and
conditional branches, i.e. a reorganised decompression path rather than a single inserted
check. The Compression advisory describes a memory-initialisation issue, which this diff does
not obviously exhibit. Left open, not claimed.

## Cross-check, not a new finding

AppleAVD's two index-paired changes were re-measured and are the same edit already recorded in
the equal-count sweep (a decode-command builder gaining a helper call plus conditional
rejection). They add no new claim here.

## Safety statement

No out-of-bounds access, type confusion, lifetime error, kernel read/write primitive, exploit
or jailbreak is established. No device probe was run, and no app can currently be deployed
because no authorised Mac enumerates a device.
