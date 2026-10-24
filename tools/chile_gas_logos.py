#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
chile_gas_logos.py - Reemplaza los logos de marcas de combustible europeas
(GOB, Filgas, Gasmer, Eco, VRM Oil...) de /model2/sign/company_logos/ por Copec.
"""

import struct
from pathlib import Path

import texture2ddecoder as t
from PIL import Image, ImageDraw, ImageFont

import chile_fuel as cf

BASE = cf.BASE
SRC = BASE / "scratch" / "logos"
REL = "model2/sign/company_logos"
FILES = [
    "eco/eco_fr", "filgas/filgas_blke", "gasmer/gasmer_balt", "gasmer/gasmer_balt_ru",
    "goab/goab_ger", "vrmoil/vrmoil_balt", "vrmoil/vrmoil_balt_ru", "vrmoil/vrmoil_symbol",
    "novoneft/novoneft", "ns_oil/ns_oil_sc", "ns_oil_ru/ns_oil_ru",
]
EXTRA = ["gasmer", "goab", "filgas", "eco", "vrmoil", "novoneft", "ns_oil", "ns_oil_ru"]
YELLOW = (255, 214, 0, 255)


def extract():
    if all((SRC / REL / (f + ".dds")).exists() for f in FILES):
        return
    import subprocess
    game = next(g for g in cf.GAME_DIRS if g.exists())
    for d in EXTRA:
        subprocess.run([str(cf.EXTRACTOR), str(game / "base.scs"), "-d=" + str(SRC),
                        "-p=/" + REL + "/" + d], capture_output=True, check=True)


def plate(w, h):
    im = Image.new("RGBA", (w, h), YELLOW)
    d = ImageDraw.Draw(im)
    m = max(4, min(w, h) // 32)
    d.rounded_rectangle((m, m, w - m, h - m), radius=m * 3, outline=cf.BLUE, width=m)
    size = int(min(w / 3.4, h * 0.55))
    f = ImageFont.truetype(cf.FONT, size)
    bb = d.textbbox((0, 0), "COPEC", font=f)
    d.text(((w - (bb[2] - bb[0])) / 2 - bb[0], (h - (bb[3] - bb[1])) / 2 - bb[1]), "COPEC",
           font=f, fill=cf.BLUE)
    return im


def main():
    extract()
    n = 0
    for f in FILES:
        p = SRC / REL / (f + ".dds")
        if not p.exists():
            continue
        d = p.read_bytes()
        h, w = struct.unpack_from("<II", d, 12)
        if d[84:88] != b"DX10" or struct.unpack_from("<I", d, 128)[0] not in (77, 78):
            continue
        out = BASE / REL / (f + ".dds")
        out.parent.mkdir(parents=True, exist_ok=True)
        cf.save_dds(plate(w, h), d, out)
        n += 1
    print(f" -> {n} logos de marcas de combustible reemplazados por Copec")


if __name__ == "__main__":
    main()
