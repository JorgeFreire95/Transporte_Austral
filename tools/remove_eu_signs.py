#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
remove_eu_signs.py - Elimina de map/chile los letreros de destino europeos.

Los items tipo 'sign' (36) con plantilla de texto (sign_templ.*) muestran
ciudades europeas (Munchen, Esslingen...). Se quitan del sector y se limpian las
referencias de sus nodos. Es idempotente.
"""
import glob
import os
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import sector_walker as w

MAP_DIR = os.path.join(ROOT, "map", "chile")


def has_text(d, it):
    q = it.flags_off + 0x05 + 0x20
    boards = struct.unpack_from("<b", d, q)[0]
    q += 1 + boards * 0x18
    return boards > 0 or struct.unpack_from("<i", d, q)[0] != 0


def main():
    total = 0
    for p in sorted(glob.glob(os.path.join(MAP_DIR, "sec*.base"))):
        d, items, o = w.walk(p)
        rm = [it for it in items if it.type == w.T_ROADSIDE and has_text(d, it)]
        if not rm:
            continue
        gone = {it.uid for it in rm}
        out = bytearray(d[:0x14])
        struct.pack_into("<I", out, 0x10, len(items) - len(rm))
        pos = 0x14
        for it in rm:
            out += d[pos:it.offset]
            pos = it.offset + it.size
        out += d[pos:o]
        tail = bytearray(d[o:])
        cnt = struct.unpack_from("<i", tail, 0)[0]
        for i in range(cnt):
            no = 4 + 0x38 * i
            for off in (0x24, 0x2C):
                if struct.unpack_from("<Q", tail, no + off)[0] in gone:
                    struct.pack_into("<Q", tail, no + off, 0)
        out += tail
        open(p, "wb").write(out)
        d2, items2, o2 = w.walk(p)
        c2 = struct.unpack_from("<i", d2, o2)[0]
        vis = struct.unpack_from("<i", d2, o2 + 4 + 0x38 * c2)[0]
        assert o2 + 4 + 0x38 * c2 + 4 + 8 * vis == len(d2), p
        total += len(rm)
    print(f"  -> letreros europeos eliminados: {total}")


if __name__ == "__main__":
    main()
