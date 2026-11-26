Exact-build OOL map-helper result provenance — iPhone14,2 / 24A5390f

Image
- Product/build: iPhone14,2 / 24A5390f.
- Kernelcache SHA-256: 6719422222a3b68120f663b2113272b5bcf48d648afe892bbce23b8460ba47dd.
- Fileset member: com.apple.kernel.

Trace
1. `a9587c8` calls `a2c9fe4` at `0xfffffff00a9588dc`. It passes the map-like object in `x0`, a caller-local address slot `&sp+0x28` in `x1`, and request-derived values in other registers/stack slots. On zero status, it reloads `[sp+0x28]` and writes it to `[input+8]` at `a9588e4–a9588e8`.
2. `a2c9fe4` aligns/validates its incoming address and keeps an intermediate in `[fp-0x78]`. It calls `a2c8668` with that slot as `x1` at `a2ca294`. On the successful common return path, it computes `x8 = [fp-0x78] + x28` and stores `x8` through the original caller's address-slot pointer at `a2ca864–a2ca878`.
3. In `a2c8668`, the subpath with request flag bit 0 clear calls `a2c82a4` with the map-like object, current value from `[*out_slot]`, size, flags, and a local two-qword result slot at `sp+0x130` (`a2c8b04–a2c8b20`). On zero status it first computes `x9 = sbfx(x8,#0,#0x3f)` for internal range work (`a2c8b2c–a2c8b34`). On the successful common path, it later reloads the first result qword, applies `sbfx` to `x8`, and stores that transformed value through `x20` at `a2c927c–a2c9284`. The sibling bit-0-set path calls `a2c9368`; its branch selection and tagged-result flow on the generic OOL route are partly documented in `ool-standard-branch-selection-24A5390f-2026-11-26.txt`.
4. `a2c82a4` first compares its object argument with global `0xfffffff007c42678`. The non-equal path uses object fields and request flags, then can call `a2e0098` or `a2dfabc` with the local two-qword slot as `x6`. Each helper's success path stores a tagged value (bit 63 ORed into its first qword) plus a companion qword; `a2c8668`'s signed 63-bit extraction transforms that tagged representation before the caller's later `+ x28` adjustment.

What this establishes
- On this bounded subpath, the address-out value is helper-derived; it is not simply the initial caller value. The observed transforms are: tagged helper result → signed 63-bit extraction → `a2c9fe4`'s `x28` adjustment → caller-local output slot → `[input+8]`.
- The helpers' first qword is an encoded result, not direct proof of a usable kernel pointer. `sbfx` sign-extends bit 62, so the final address class depends on the selected map/range and runtime value; do not describe it as merely clearing a tag in every case.

Limits
- The bit-0-set sibling through `a2c9368` is partly analyzed in `ool-standard-branch-selection-24A5390f-2026-11-26.txt`; its final map/output semantics and `x28` value remain unresolved.
- No runtime call, status, returned address, object identity, or mapping extent was observed. The setup sites configure different map-like ranges, but runtime registration/invocation, retention, and later writes remain unresolved.
- This does not establish that `[map+0x28]` is a mapped kernel data pointer, that `buffer+length` remains mapped, or that any OOB occurs.

Disassembly artifacts used (session scratch): `a9587c8-24A5390f.txt`, `a2c9fe4-24A5390f-full.txt`, `a2c8668_full.txt`, `a2c82a4_full_disass.txt`, `a2e0098_range_helper_full.txt`, `a2dfabc_range_helper_full.txt`, and `a2c7e3c_factory_full.txt`. The scan inputs were pinned to the kernelcache SHA above; no device probes, selector calls, builds, or installs were run.