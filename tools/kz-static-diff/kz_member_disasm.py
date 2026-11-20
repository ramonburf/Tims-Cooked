#!/usr/bin/env python3
"""Disassemble one fileset member function with printable-string references annotated.

`kz_fn_strings.py` only works for the kernel-core member; this variant loads any
fileset member by substring and annotates each instruction whose operands build a
printable string address (ADRP+ADD / literal-pool loads are followed by capstone's
own operand text, so also try direct integer operands).

Usage:
    python kz_member_disasm.py <build> <member-substring> <va_hex> [size_hex]

Examples:
    python kz_member_disasm.py 24A446 AppleCentauriManager 0xfffffe0008a13968
    python kz_member_disasm.py 24B119 AppleJPEGDriver 0xfffffe000900c1cc

Numpy-free; capstone from tools/pylibs.
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "opencode-temp"))
sys.path.insert(0, str(HERE.parent / "pylibs"))

import capstone  # noqa: E402
from capstone import CS_ARCH_ARM64, CS_MODE_LITTLE_ENDIAN  # noqa: E402
from kc_member import load_member  # noqa: E402
from kc_fstarts import func_of, cstr_at, v2o  # noqa: E402

MD = capstone.Cs(CS_ARCH_ARM64, CS_MODE_LITTLE_ENDIAN)
MD.detail = True
MD.skipdata = True


def main(argv):
    if len(argv) < 4:
        raise SystemExit(__doc__)
    bld, member = argv[1], argv[2]
    va = int(argv[3], 16)
    sz = int(argv[4], 16) if len(argv) > 4 else None
    b = load_member(bld, member)
    st = func_of(b, va)
    if st:
        size = (st[1] - st[0]) if st[1] else 0
        print("func start %#x (contains %#x), size %#x" % (st[0], va, size))
        if sz is None:
            sz = size or 0x200
    off = v2o(b, va)
    blob = b["data"][off:off + (sz or 0)]
    for ins in MD.disasm(blob, va):
        ann = ""
        for tok in ins.op_str.split(","):
            tok = tok.strip().lstrip("#")
            try:
                v = int(tok, 0)
            except ValueError:
                continue
            if v >= 0xfffffe0007000000:
                s = cstr_at(b, v)
                if s and all(32 <= ord(c) < 127 or c in "\n\t" for c in s):
                    ann += '   ; "%s" @%#x' % (s[:100], v)
        print("%#x  %-8s %-40s%s" % (ins.address, ins.mnemonic, ins.op_str, ann))


if __name__ == "__main__":
    main(sys.argv)
