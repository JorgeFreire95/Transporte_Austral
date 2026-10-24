#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
chile_fuel.py - Reemplaza las marcas europeas de las estaciones de servicio por
marcas chilenas (Copec / Pronto) editando los atlas de textura del juego base.

Extrae /prefab2/gas_station/*.dds del juego, cambia logos, carteles de combustible
y publicidad, y escribe el resultado en prefab2/gas_station/ del mod (mismo path:
el mod sobreescribe la textura original, el .tobj original se sigue usando).
Familias soportadas: gryfoil, primel, pegi (variantes de 2048x2048 sin 'light').
"""

import re
import struct
import subprocess
import sys
from pathlib import Path

import texture2ddecoder as t
from PIL import Image, ImageDraw, ImageFont

BASE = Path(__file__).resolve().parent.parent
EXTRACTOR = BASE / "tools" / "extractor" / "extractor.exe"
SRC = BASE / "scratch" / "gas" / "prefab2" / "gas_station"
OUT = BASE / "prefab2" / "gas_station"
GAME_DIRS = [
    Path(r"D:\SteamLibrary\steamapps\common\Euro Truck Simulator 2"),
    Path(r"C:\Program Files (x86)\Steam\steamapps\common\Euro Truck Simulator 2"),
    Path(r"E:\SteamLibrary\steamapps\common\Euro Truck Simulator 2"),
]
FONT = r"C:\Windows\Fonts\arialbd.ttf"
FONT_I = r"C:\Windows\Fonts\arialbi.ttf"
K = 2048 / 1932.0
BLUE = (0, 66, 160, 255)
RED = (214, 30, 40, 255)
FAMILY = re.compile(r"^gas_station_(gryfoil|primel|pegi)_(?!.*(light|modern|lod)).*\.dds$")


def extract():
    if SRC.exists() and any(SRC.glob("*.dds")):
        return
    game = next((g for g in GAME_DIRS if g.exists()), None)
    if not game:
        sys.exit("No se encontro la carpeta de ETS2")
    subprocess.run([str(EXTRACTOR), str(game / "base_share.scs"), str(game / "base.scs"),
                    "-f=/prefab2/gas_station/*", "-d=" + str(BASE / "scratch" / "gas")],
                   capture_output=True, check=True)


def decode(path):
    d = path.read_bytes()
    h, w = struct.unpack_from("<II", d, 12)
    if d[84:88] != b"DX10" or struct.unpack_from("<I", d, 128)[0] not in (77, 78):
        return None, d
    return Image.frombytes("RGBA", (w, h), t.decode_bc3(d[148:], w, h), "raw", "BGRA"), d


def B(v):
    return tuple(int(round(x * K)) for x in v)


def sample(im, b):
    return im.getpixel((b[0] + 4, b[1] + 4))


def fill(im, b, color=None):
    b = B(b)
    ImageDraw.Draw(im).rectangle(b, fill=color or sample(im, b))


def text(im, b, s, color, size, vertical=False, bold_italic=False, bgcolor=None):
    b = B(b)
    f = ImageFont.truetype(FONT_I if bold_italic else FONT, int(size * K))
    x0, y0, x1, y1 = b
    w, h = (y1 - y0, x1 - x0) if vertical else (x1 - x0, y1 - y0)
    layer = Image.new("RGBA", (w, h), bgcolor or im.getpixel((x0 + 4, y0 + 4)))
    ld = ImageDraw.Draw(layer)
    bb = ld.textbbox((0, 0), s, font=f)
    ld.text(((w - (bb[2] - bb[0])) / 2 - bb[0], (h - (bb[3] - bb[1])) / 2 - bb[1]), s, font=f, fill=color)
    if vertical:
        layer = layer.rotate(90, expand=True)
    im.paste(layer, (x0, y0))


def fuel_labels(im):
    # Etiquetas de boquilla (formas) y de surtidor, mismas posiciones en todas las marcas
    green, white, black = (12, 180, 90, 255), (236, 240, 236, 255), (34, 34, 40, 255)
    pump = [((1525, 228, 1606, 490), "95", white, green), ((1628, 228, 1710, 490), "97", green, white),
            ((1732, 228, 1810, 490), "93", green, white), ((1832, 228, 1918, 490), "Diésel", black, white)]
    for b, s, bgc, fg in pump:
        ImageDraw.Draw(im).rectangle(B(b), fill=bgc)
        text(im, b, s, fg, 48, vertical=True, bgcolor=bgc)


def ads(im):
    for b in [(1068, 970, 1484, 1604), (1501, 970, 1916, 1604)]:
        bb = B(b)
        ImageDraw.Draw(im).rectangle(bb, fill=(0, 56, 140, 255))
        text(im, (b[0], b[1] + 60, b[2], b[1] + 200), "PRONTO", (255, 214, 0, 255), 90, bold_italic=True,
             bgcolor=(0, 56, 140, 255))
        text(im, (b[0], b[1] + 260, b[2], b[1] + 360), "Café y sándwich", (255, 255, 255, 255), 42,
             bgcolor=(0, 56, 140, 255))
        text(im, (b[0], b[1] + 420, b[2], b[1] + 520), "Abierto 24 horas", (255, 214, 0, 255), 46,
             bgcolor=(0, 56, 140, 255))
    shop = (830, 1068, 1040, 1504)
    text(im, shop, "PRONTO", (0, 56, 140, 255), 80, vertical=True, bold_italic=True)


def logo_panel(im, b, color=BLUE, size=100, label="COPEC"):
    fill(im, b)
    text(im, b, label, color, size)


def brand_gryfoil(im):
    yellow = im.getpixel(B((200, 760)))
    ImageDraw.Draw(im).rectangle(B((0, 706, 484, 1190)), fill=yellow)
    text(im, (0, 706, 484, 1190), "COPEC", BLUE, 100, bgcolor=yellow)
    text(im, (0, 1376, 483, 1524), "COPEC", (30, 30, 40, 255), 70)
    ImageDraw.Draw(im).rectangle(B((262, 1606, 418, 1760)), fill=im.getpixel(B((300, 1590))))
    ImageDraw.Draw(im).rectangle(B((499, 762, 570, 1604)), fill=yellow)
    ImageDraw.Draw(im).rectangle(B((570, 1000, 646, 1604)), fill=yellow)
    text(im, (499, 1000, 646, 1560), "COPEC", BLUE, 62, vertical=True, bgcolor=yellow)
    ImageDraw.Draw(im).rectangle(B((540, 1405, 648, 1535)), fill=yellow)


def brand_primel(im):
    yellow = (214, 192, 32, 255)
    ImageDraw.Draw(im).rectangle(B((0, 1330, 484, 1930)), fill=yellow)
    text(im, (0, 1330, 484, 1930), "COPEC", BLUE, 110, bgcolor=yellow, bold_italic=True)
    ImageDraw.Draw(im).rectangle(B((0, 1330, 484, 1340)), fill=yellow)


def brand_pegi(im):
    light = im.getpixel(B((10, 720)))
    dark = im.getpixel(B((10, 10)))
    ImageDraw.Draw(im).rectangle(B((0, 0, 482, 480)), fill=dark)
    text(im, (0, 0, 482, 480), "COPEC", (255, 214, 0, 255), 90, bgcolor=dark)
    ImageDraw.Draw(im).rectangle(B((0, 708, 484, 1354)), fill=light)
    text(im, (0, 708, 484, 1354), "COPEC", BLUE, 100, bgcolor=light)
    ImageDraw.Draw(im).rectangle(B((0, 1376, 484, 1526)), fill=light)
    text(im, (0, 1376, 484, 1526), "COPEC", BLUE, 90, bgcolor=light)
    ImageDraw.Draw(im).rectangle(B((499, 762, 722, 1606)), fill=light)
    text(im, (499, 762, 722, 1606), "COPEC", BLUE, 72, vertical=True, bgcolor=light)
    ImageDraw.Draw(im).rectangle(B((0, 1610, 484, 1930)), fill=light)
    text(im, (0, 1610, 484, 1930), "COPEC", BLUE, 100, bgcolor=light)


def save_dds(im, header, path):
    levels = []
    cur = im.convert("RGBA")
    mips = struct.unpack_from("<I", header, 28)[0]
    tmp = path.with_suffix(".tmp.dds")
    for _ in range(mips):
        cur.save(tmp, format="DDS", pixel_format="DXT5")
        levels.append(tmp.read_bytes()[128:])
        if cur.width > 1:
            cur = cur.resize((max(1, cur.width // 2), max(1, cur.height // 2)), Image.LANCZOS)
    tmp.unlink()
    path.write_bytes(header[:148] + b"".join(levels))


def main():
    extract()
    OUT.mkdir(parents=True, exist_ok=True)
    n = 0
    for f in sorted(SRC.glob("gas_station_*.dds")):
        m = FAMILY.match(f.name)
        if not m:
            continue
        im, raw = decode(f)
        if im is None or im.size != (2048, 2048):
            continue
        ref = im.getpixel(B((556, 30)))
        if not (ref[0] > 180 and ref[1] < 60):  # extintor rojo: confirma el mismo layout
            continue
        {"gryfoil": brand_gryfoil, "primel": brand_primel, "pegi": brand_pegi}[m.group(1)](im)
        fuel_labels(im)
        ads(im)
        save_dds(im, raw, OUT / f.name)
        im.convert("RGB").save(BASE / "scratch" / ("out_" + f.stem + ".png"))
        n += 1
    print(f" -> {n} texturas de estaciones de servicio rebrandeadas (Copec / Pronto)")


if __name__ == "__main__":
    main()
