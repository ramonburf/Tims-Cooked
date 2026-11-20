# Tims Cooked

Tims Cooked is an exploratory iOS security-research harness and analysis repository for iOS 27.0 and 27.0.1 on arm64e. The research goal is a semi-untethered jailbreak; this repository does **not** contain one.

## Current status

No kernel read/write primitive, kernel code execution, PAC/SPTM bypass, or working jailbreak has been demonstrated. The repository tracks candidate socket, VM, IOSurface, and other kernel paths. Treat each result according to its evidence: a reachable interface or race observation is not, by itself, a memory-corruption primitive or exploit.

Start with the relevant notes under [`analysis/`](analysis/) and distinguish confirmed observations from hypotheses before running a probe.

## Latest research update — 2026-11-20

Static analysis has connected a Mach-VM-read-like request path to a VM copy/fault candidate on iOS 27.0.1 (build 24A446), but the exact API identity, ordinary-app reachability, and runtime guard conditions remain unverified. No confirmed vulnerability, controlled kernel corruption, kernel read/write primitive, or semi-untethered jailbreak has been demonstrated; no new CoW device trigger was run for this checkpoint.

See the [dated research note](research-updates/2026-11-20.md) and the [GitHub checkpoint release](https://github.com/ramonburf/Tims-Cooked/releases/tag/research-2026-11-20). That release includes the unchanged, sanitized v0.6 IPA (SHA-256 `dd7a4680155fd738d5b279bf0da3e8debf385a0cf44d8636a0c35a3e1039ce50`); no new app build is claimed.

## Safety

- Test only on devices you own or are authorized to assess.
- The research workflow is intended to preserve device data. Do not restore, update, downgrade, or write firmware as part of these probes.
- A kernel or system-service probe can still crash or reboot a device. Stop after a crash, respring, or unexpected reboot, then preserve the logs before continuing.
- Review a probe and its resource limits before running it. Do not treat a successful launch or a userland crash as proof of kernel impact.
- Keep signing credentials, device identifiers, host details, and private operational notes out of commits.

## Release 0.6

The `v0.6` release asset is `TimsCooked-v0.6.ipa` (build 6, bundle identifier `com.example.timscooked`). It is an ad-hoc-signed research build with no embedded provisioning profile. Re-sign and provision it with your own development identity before installation. It is a harness for research, not a jailbreak or a general-purpose security tool.

## Build and run

Building requires macOS and Xcode. Installing on a device also requires a locally configured signing identity and a device enabled for development.

From the `carrier/` directory, build for a connected device:

```sh
cd carrier
DEV=<device-identifier> ./build_race.sh
```

The script writes the app to `.build13/Build/Products/Debug-iphoneos/AGXProbe.app`. Install and launch it with the bundle identifier configured in your local Xcode signing settings:

```sh
xcrun devicectl device install app --device "$DEV" \
  .build13/Build/Products/Debug-iphoneos/AGXProbe.app
xcrun devicectl device process launch --device "$DEV" --console \
  --terminate-existing <your-bundle-identifier> --sockprec
```

The build helper accepts `KEYCHAIN_PW` from the environment when Xcode needs the login keychain unlocked. Do not put the password in the script or in shell history. Signing settings belong in your local Xcode configuration, not in this repository.

### Harness modes

| Argument | Purpose |
|---|---|
| `--sockuaf` | Run the socket-lifetime race variants |
| `--sockprec` | Run the gated socket probe with its peer-delivery oracle |
| `--sockool`, `--sockxz`, `--sockgc` | Run experimental reclaim and spray variants |
| `--web`, `--webscan` | Run WebKit probes |
| `--probe` | Run the IOSurface probe sweep |

These modes are experimental and may crash the app or device. Their names describe what a probe attempts, not a confirmed vulnerability or exploit.

## Tests

The standalone Swift regression checks do not require a device or signing. Run them on macOS:

```sh
cd carrier/tests
swiftc -O fixcheck.swift -o "$TMPDIR/fixcheck" && "$TMPDIR/fixcheck"
swiftc -O logcheck.swift -o "$TMPDIR/logcheck" && "$TMPDIR/logcheck"
```

See [`carrier/tests/README.md`](carrier/tests/README.md) for test coverage and limits.

## Repository layout

- `carrier/` — SwiftUI research harness and headless regression checks.
- `analysis/` — firmware, kernel, reachability, and experiment notes.
- `tools/` — supporting parsers and analysis utilities.

Research notes can be build-specific and provisional. Reproduce a result on the stated OS build before drawing conclusions from it.
