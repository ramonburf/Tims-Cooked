# iOS 27 device-probe batch — 2026-11-25

Documentation-only, bounded tests on iPhone18,1 / iOS 27.0.1 build `24A446`:

- The app's `--mementry` self-memory alias control visibly completed; userland only.
- `--ane` without trigger opened one of 16 enumerated candidates; no selector or trigger was sent.
- `--decmpfs` produced no data-bearing readback, `UF_COMPRESSED` remained unset, and filesystem-control attempts returned `EPERM`; whether decoder entry occurred remains unproven.

Later crash-log review found a SpringBoard icon-placeholder `os_fault` event and an NRD staged-tvOS DYLD abort; neither is attributed to the test. No SpringBoard process death or device reboot was established, and no further reports appeared in the later read-only check. No kernel read/write, exploit, or jailbreak is established. No new app binary is attached or claimed; see `research-updates/2026-11-25-device-probe-batch.md`.
