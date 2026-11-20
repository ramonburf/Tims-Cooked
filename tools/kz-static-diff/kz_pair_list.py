#!/usr/bin/env python3
"""Per-function cross-build comparison of one fileset member's replace blocks.

`kz_newfunc_align.py` reports whole-block edits; `kz_pair_shape_check.py` reduces
them to drift vs real. This tool goes one level further: inside each replace block it
pairs A/B functions **by index** (valid only when the block's function counts match)
and classifies every pair as

  * normalised-fingerprint equal  -> unchanged
  * instruction-shape equal        -> address/data-segment drift
  * shape-differing               -> REAL code edit

and prints both sides of every real pair.

Usage:
    python kz_newfunc_align.py <member> > align.txt
    python kz_pair_list.py <member> align.txt

Numpy-free; uses capstone from tools/pylibs and kc_member/kc_norm_diff/kc_fstarts.
"""
import difflib
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "opencode-temp"))
sys.path.insert(0, str(HERE.parent / "pylibs"))

import capstone  # noqa: E402
from capstone import CS_ARCH_ARM64, CS_MODE_LITTLE_ENDIAN  # noqa: E402
from capstone.arm64 import ARM64_OP_MEM, ARM64_OP_REG  # noqa: E402
from kc_member import load_member  # noqa: E402
import kc_norm_diff  # noqa: E402
from kc_fstarts import func_refs  # noqa: E402

BUILDS = ("24A446", "24B119")
MD = capstone.Cs(CS_ARCH_ARM64, CS_MODE_LITTLE_ENDIAN)
MD.detail = True
MD.skipdata = True

PAT = re.compile(
    r"replace A=(\d+)\s+B=(\d+)\s+szA=(\d+)\s+szB=(\d+)\s+"
    r"A@0x([0-9a-f]+)\.\.0x([0-9a-f]+)\s+B@0x([0-9a-f]+)\.\.0x([0-9a-f]+)")


def starts_in(build, member, lo, hi):
    b = load_member(build, member)
    return b, [s for s in b["starts"] if lo <= s < hi]


def func_size(b, va):
    s = b["starts"]
    for k, v in enumerate(s):
        if v == va:
            return (s[k + 1] - va) if k + 1 < len(s) else None
    return None


def off_of(b, va):
    for nm, (vm, vsz, fo, fsz) in b["segs"].items():
        if vm <= va < vm + vsz:
            return fo + (va - vm)
    raise KeyError(hex(va))


def shape_ins(b, va, sz):
    if not sz:
        return ()
    out = []
    for ins in MD.disasm(b["data"][off_of(b, va):off_of(b, va) + sz], va):
        try:
            ops = ins.operands
        except capstone.CsError:
            ops = []
        regs = tuple(ins.reg_name(o.reg) for o in ops if o.type == ARM64_OP_REG)
        mem = ""
        for o in ops:
            if o.type == ARM64_OP_MEM:
                mem = "[sp]" if o.mem.base == 0 else "[%s]" % ins.reg_name(o.mem.base)
        out.append((ins.mnemonic, regs, mem))
    return tuple(out)


def refs(b, va, sz):
    return sorted(func_refs(b, va, va + sz))[:6] if sz else []


def main(argv):
    if len(argv) < 2:
        raise SystemExit(__doc__)
    member = argv[1]
    path = argv[2] if len(argv) > 2 else "-"
    text = sys.stdin.read() if path == "-" else Path(path).read_text(errors="replace")
    drift = real = 0
    for ln in text.splitlines():
        m = PAT.match(ln)
        if not m:
            continue
        nA, nB, szA, szB = (int(m.group(i)) for i in (1, 2, 3, 4))
        a0, a1, b0, b1 = (int(m.group(i), 16) for i in (5, 6, 7, 8))
        ba, sa = starts_in(BUILDS[0], member, a0, a0 + szA + 4)
        bb, sb = starts_in(BUILDS[1], member, b0, b0 + szB + 4)
        if nA != nB or len(sa) != len(sb):
            real += 1
            print("COUNT-MISMATCH A=%d B=%d startsA=%d startsB=%d A@%#x sz %#x -> B@%#x sz %#x"
                  % (nA, nB, len(sa), len(sb), a0, szA, b0, szB))
            for va in sa:
                print("    A %#x" % va)
            for vb in sb:
                print("    B %#x" % vb)
            continue
        block_real = []
        for va, vb in zip(sa, sb):
            fza, fzb = func_size(ba, va), func_size(bb, vb)
            fa = kc_norm_diff.norm_func(ba, va, fza) if fza else []
            fb = kc_norm_diff.norm_func(bb, vb, fzb) if fzb else []
            if fa == fb:
                continue
            if (shape_ins(ba, va, fza) if fza else ()) == \
               (shape_ins(bb, vb, fzb) if fzb else ()):
                drift += 1
                continue
            real += 1
            block_real.append((va, vb, fza, fzb))
        if block_real:
            print("REAL A@%#x..%#x -> B@%#x..%#x (%d/%d funcs differ)"
                  % (a0, a1, b0, b1, len(block_real), nA))
            for va, vb, fza, fzb in block_real:
                fa = kc_norm_diff.norm_func(ba, va, fza)
                fb = kc_norm_diff.norm_func(bb, vb, fzb)
                sm = difflib.SequenceMatcher(None, fa, fb, autojunk=False)
                print("  pair A@%#x sz %#x -> B@%#x sz %#x  refsA=%s refsB=%s"
                      % (va, fza, vb, fzb, refs(ba, va, fza), refs(bb, vb, fzb)))
                for tag, i1, i2, j1, j2 in sm.get_opcodes():
                    if tag == "equal":
                        continue
                    print("    %-7s A=%-3d B=%-3d | %s || %s" % (
                        tag, i2 - i1, j2 - j1,
                        " ; ".join(fa[i1:i2])[:200],
                        " ; ".join(fb[j1:j2])[:200]))
    print("%s: blocks drift=%d real=%d" % (member, drift, real))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
