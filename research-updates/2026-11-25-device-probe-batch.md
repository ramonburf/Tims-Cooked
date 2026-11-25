# iOS 27 device-probe batch — 2026-11-25

## Scope

A bounded signed-app test batch ran on iPhone18,1 with iOS 27.0.1 build `24A446`. The tests were limited to the app's self-memory control, ANE service reachability without an external-method trigger, and sandbox-local decmpfs filesystem ingress attempts. No broad selector sweep, malformed GPU/AVE request, IOSurface method call, or socket/allocator race was run.

## Results

- **`--mementry`:** the app visibly completed its self-memory alias control and read back the expected marker. This is a userland control only; it is not a kernel primitive.
- **`--ane` without `--anetrigger`:** 16 candidate services were enumerated, one open succeeded, and no trigger or external-method selector was sent. This establishes reachability only.
- **`--decmpfs`:** the plain-file baseline read returned 4096 bytes. The attempted xattr/resource-fork writes did not produce data-bearing reads: each tested compressed-data read returned zero, `UF_COMPRESSED` remained unset, and the filesystem-control variants returned `EPERM`. No decompressed output was observed, and decoder entry remains unproven. This is a bounded negative for these attempted app-sandbox ingress routes, not proof that every decmpfs path is safe or that the decoder was reached.

The app-container manifests showed no pre-existing file removal; expected session-log and reach-log updates account for the observed changes.

## Device health and limits

Crash-report snapshots were unchanged at 307 before/after each fresh mode. A later read-only snapshot contained 309 reports: one `ExcUserFault_SpringBoard` event whose `os_fault` payload names `com.apple.iconservices` and a placeholder-image failure, and one `com.apple.NRD.UpdateBrainService` DYLD abort reporting a staged executable built for tvOS. The SpringBoard report has no `procExitAbsTime`; the same SpringBoard PID was present before and after, and the boot session was unchanged. This does not establish a SpringBoard termination/respring or device reboot, and any relation to the tests is unproven. A later read-only check found no further reports, the device connected and booted, and the probe app not running.

The iPhone 13 Pro secondary was unavailable on both checked hosts. No further device mode was cleared: remaining candidates are historical, lack reachable test ingress or an independent oracle, or involve broad/racy, panic-capable, or malformed-driver paths that require the designated secondary and the existing no-brick gates.

No vulnerability, memory corruption, kernel read/write, exploit, or jailbreak is established. No new app binary was built or released in this checkpoint.
