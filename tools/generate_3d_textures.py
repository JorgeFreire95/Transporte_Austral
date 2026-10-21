#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
==============================================================================
TRANSPORTE AUSTRAL - GENERADOR DE TEXTURAS 3D Y CARTELES EN EL MUNDO (ETS2)
==============================================================================
Genera las texturas DDS con compresión DXT5 y pirámide completa de mipmaps
para sustituir los carteles 3D y prefabs físicos del juego base:
1. /material/logo/*.dds y .tobj (Carteles de entrada y fachadas de empresas)
   - transinet.dds -> Blue Express
   - itcc.dds      -> ENAP Refinerías
   - sellplan.dds  -> Unimarc
   - eurogoodies.dds -> Lider (Walmart Chile)
   - tradeaux.dds  -> Starken
   - lkwlog.dds    -> Starken
   - posped.dds    -> Chilexpress
   - fcp.dds       -> Soprole
   - bcp.dds       -> Carozzi
   - euroacres.dds -> Agrosuper
   - sanbuilders.dds -> Sodimac
   - kaarfor.dds   -> Cencosud
   - trameri.dds   -> Colun
   - treeet.dds    -> Arauco
   - stokes.dds    -> CCU
   - nbfc.dds      -> Coca-Cola Embonor
   - wgcc.dds      -> SQM
2. /prefab/tradeaux_warehouse/*.dds y .tobj (Tótems de entrada)
   - transinet_logo.dds -> Blue Express Tótem
   - tradeaux_logo.dds  -> Starken Tótem
   - stokes_logo.dds    -> CCU Tótem
3. /prefab/gas_small/*.dds y .tobj (Tótems de estaciones de servicio)
   - price_stand_red.dds   -> Copec Pronto
   - price_stand_blue.dds  -> Shell Upa!
   - price_stand_green.dds -> Petrobras Spacio 1
4. /prefab/gas/*.dds y .tobj (Marquesinas y edificios de estaciones de servicio)
   - gas_station.dds        -> Copec Pronto (Rojo/Blanco)
   - gas_station_yellow.dds -> Shell Upa! (Amarillo/Rojo)
   - gas_station_green.dds  -> Petrobras Spacio 1 (Verde/Amarillo)
   - carwash*.dds           -> Lavado Copec / Shell / Petrobras
5. /model/sign/gas/*.dds y .tobj (Tótems de carretera y autopista)
   - gas_*.dds y gas_big_*.dds -> Copec, Shell, Petrobras, Aramco
"""

import os
import sys
import io
import shutil
import struct
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

BASE_DIR = Path(__file__).resolve().parent.parent
EXTRACT_DIR = BASE_DIR / "scratch" / "test_extract"
FONT_BOLD = r"C:\Windows\Fonts\arialbd.ttf"
FONT_REG = r"C:\Windows\Fonts\arial.ttf"


# ==============================================================================
# 1. COMPRESOR DDS DXT5 CON PIRÁMIDE COMPLETA DE MIPMAPS
# ==============================================================================
def encode_dxt5_mipmaps(im: Image.Image) -> bytes:
    """Codifica una imagen RGBA en un archivo DDS binario con DXT5 y mipmaps completos."""
    im = im.convert("RGBA")
    w, h = im.size

    # Generar todos los niveles de mipmaps hasta 1x1
    mips = [im]
    cur_w, cur_h = w, h
    while cur_w > 1 or cur_h > 1:
        cur_w = max(1, cur_w // 2)
        cur_h = max(1, cur_h // 2)
        mips.append(mips[-1].resize((cur_w, cur_h), Image.Resampling.LANCZOS))

    mip_data = bytearray()
    for m in mips:
        buf = io.BytesIO()
        pad_w = max(4, (m.width + 3) & ~3)
        pad_h = max(4, (m.height + 3) & ~3)
        if pad_w != m.width or pad_h != m.height:
            padded = Image.new("RGBA", (pad_w, pad_h), (0, 0, 0, 0))
            padded.paste(m, (0, 0))
            padded.save(buf, format="DDS", pixel_format="DXT5")
        else:
            m.save(buf, format="DDS", pixel_format="DXT5")
        raw = buf.getvalue()
        # Los bloques comprimidos DXT5 están después de los 128 bytes del header DDS
        mip_data.extend(raw[128:])

    # Cabecera estándar DDS con soporte de mipmaps y DXT5
    DDSD_CAPS = 0x1
    DDSD_HEIGHT = 0x2
    DDSD_WIDTH = 0x4
    DDSD_PIXELFORMAT = 0x1000
    DDSD_MIPMAPCOUNT = 0x20000
    DDSD_LINEARSIZE = 0x80000

    DDSCAPS_COMPLEX = 0x8
    DDSCAPS_TEXTURE = 0x1000
    DDSCAPS_MIPMAP = 0x400000

    DDPF_FOURCC = 0x4

    flags = DDSD_CAPS | DDSD_HEIGHT | DDSD_WIDTH | DDSD_PIXELFORMAT | DDSD_MIPMAPCOUNT | DDSD_LINEARSIZE
    caps1 = DDSCAPS_TEXTURE | DDSCAPS_COMPLEX | DDSCAPS_MIPMAP
    pitch_or_linear = max(1, ((w + 3) // 4)) * 16

    header = bytearray(128)
    header[0:4] = b"DDS "
    struct.pack_into("<I", header, 4, 124)                 # dwSize
    struct.pack_into("<I", header, 8, flags)               # dwFlags
    struct.pack_into("<I", header, 12, h)                  # dwHeight
    struct.pack_into("<I", header, 16, w)                  # dwWidth
    struct.pack_into("<I", header, 20, pitch_or_linear)    # dwPitchOrLinearSize
    struct.pack_into("<I", header, 24, 0)                  # dwDepth
    struct.pack_into("<I", header, 28, len(mips))          # dwMipMapCount

    # PixelFormat (offset 76)
    struct.pack_into("<I", header, 76, 32)                 # dwSize
    struct.pack_into("<I", header, 80, DDPF_FOURCC)        # dwFlags
    header[84:88] = b"DXT5"                                # dwFourCC

    # Caps (offset 108)
    struct.pack_into("<I", header, 108, caps1)

    return bytes(header) + bytes(mip_data)


def save_dds(im: Image.Image, out_path: Path):
    """Guarda una imagen en formato DDS DXT5 con mipmaps."""
    out_path.parent.mkdir(parents=True, exist_ok=True)
    dds_bytes = encode_dxt5_mipmaps(im)
    with open(out_path, "wb") as f:
        f.write(dds_bytes)


def copy_or_create_tobj(src_rel: str, dest_path: Path, clamp: bool = False):
    """Copia el archivo TOBJ original si existe o genera uno compatible con ETS2."""
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    src_path = EXTRACT_DIR / src_rel
    if src_path.exists():
        shutil.copy2(src_path, dest_path)
    else:
        # Generar TOBJ estándar
        tex_path = "/" + str(dest_path.with_suffix(".dds").relative_to(BASE_DIR)).replace("\\", "/")
        path_bytes = tex_path.encode("utf-8")
        addr = 0x01 if clamp else 0x02
        header = bytes([
            0x01, 0x0A, 0xB1, 0x70,
            0x00, 0x00, 0x00, 0x00,
            0x00, 0x00, 0x00, 0x00,
            0x00, 0x00, 0x00, 0x00,
            0x00, 0x00, 0x00, 0x00,
            0x01, 0x00, 0x00, 0x00,
            0x02, 0x00,
            0x03, 0x03, 0x03, 0x00,
            addr, addr,
            0x00, 0x00, 0x00, 0x00,
            0x00, 0x01, 0x00, 0x00
        ])
        with open(dest_path, "wb") as f:
            f.write(header)
            f.write(struct.pack("<Q", len(path_bytes)))
            f.write(path_bytes)


# ==============================================================================
# 2. CARTELES 3D DE EMPRESAS CHILENAS (/material/logo/)
# ==============================================================================
COMPANY_3D_BRANDS = {
    "transinet": {
        "title": "BLUE EXPRESS",
        "sub": "DISTRIBUCIÓN NACIONAL",
        "bg": (0, 150, 214),       # Azul oficial Blue Express
        "fg": (255, 255, 255),
        "accent": (255, 120, 0),    # Naranja courier
        "size": (256, 128)
    },
    "itcc": {
        "title": "ENAP",
        "sub": "REFINERÍAS DE CHILE",
        "bg": (0, 45, 95),         # Azul marino Enap
        "fg": (255, 255, 255),
        "accent": (211, 17, 30),    # Rojo energía
        "size": (256, 128)
    },
    "sellplan": {
        "title": "UNIMARC",
        "sub": "SUPERMERCADO CHILENO",
        "bg": (211, 17, 30),       # Rojo Unimarc
        "fg": (255, 255, 255),
        "accent": (255, 220, 220),
        "size": (512, 256)
    },
    "eurogoodies": {
        "title": "LIDER",
        "sub": "WALMART CHILE",
        "bg": (0, 70, 145),        # Azul Lider
        "fg": (255, 255, 255),
        "accent": (255, 194, 32),   # Amarillo chispa
        "size": (256, 128)
    },
    "tradeaux": {
        "title": "STARKEN",
        "sub": "CARGA Y ENCOMIENDAS",
        "bg": (255, 102, 0),       # Naranja Starken
        "fg": (255, 255, 255),
        "accent": (255, 235, 210),
        "size": (256, 128)
    },
    "lkwlog": {
        "title": "STARKEN",
        "sub": "LOGÍSTICA NACIONAL",
        "bg": (255, 102, 0),
        "fg": (255, 255, 255),
        "accent": (255, 235, 210),
        "size": (256, 128)
    },
    "posped": {
        "title": "CHILEXPRESS",
        "sub": "COURIER & LOGÍSTICA",
        "bg": (255, 204, 0),       # Amarillo Chilexpress
        "fg": (204, 0, 0),
        "accent": (35, 35, 35),
        "size": (256, 128)
    },
    "fcp": {
        "title": "SOPROLE",
        "sub": "LÁCTEOS Y DERIVADOS",
        "bg": (0, 51, 153),        # Azul Soprole
        "fg": (255, 255, 255),
        "accent": (220, 20, 60),
        "size": (256, 128)
    },
    "bcp": {
        "title": "CAROZZI",
        "sub": "ALIMENTOS Y HARINAS",
        "bg": (179, 0, 0),         # Rojo Carozzi
        "fg": (255, 255, 255),
        "accent": (255, 255, 255),
        "size": (256, 128)
    },
    "euroacres": {
        "title": "AGROSUPER",
        "sub": "ALIMENTOS DE CHILE",
        "bg": (227, 6, 19),        # Rojo Agrosuper
        "fg": (255, 255, 255),
        "accent": (255, 215, 0),
        "size": (256, 128)
    },
    "sanbuilders": {
        "title": "SODIMAC",
        "sub": "HOMECENTER CHILE",
        "bg": (0, 68, 124),        # Azul Sodimac
        "fg": (255, 255, 255),
        "accent": (245, 179, 36),   # Amarillo Sodimac
        "size": (256, 128)
    },
    "kaarfor": {
        "title": "CENCOSUD",
        "sub": "JUMBO / EASY / SANTA ISABEL",
        "bg": (0, 122, 51),        # Verde Cencosud
        "fg": (255, 255, 255),
        "accent": (255, 255, 255),
        "size": (512, 256)
    },
    "trameri": {
        "title": "COLUN",
        "sub": "LA MAGIA DEL SUR",
        "bg": (0, 102, 178),       # Azul Colun
        "fg": (255, 255, 255),
        "accent": (255, 255, 255),
        "size": (256, 128)
    },
    "treeet": {
        "title": "ARAUCO",
        "sub": "CELULOSA Y MADERAS",
        "bg": (0, 90, 54),         # Verde Arauco
        "fg": (255, 255, 255),
        "accent": (144, 238, 144),
        "size": (256, 128)
    },
    "stokes": {
        "title": "CCU",
        "sub": "BEBIDAS Y CERVEZAS",
        "bg": (11, 35, 65),        # Azul CCU
        "fg": (255, 255, 255),
        "accent": (212, 175, 55),   # Dorado
        "size": (256, 128)
    },
    "nbfc": {
        "title": "EMBONOR",
        "sub": "COCA-COLA CHILE",
        "bg": (204, 0, 0),         # Rojo Coca-Cola
        "fg": (255, 255, 255),
        "accent": (255, 255, 255),
        "size": (256, 128)
    },
    "wgcc": {
        "title": "SQM",
        "sub": "LITIO Y MINERALES",
        "bg": (0, 75, 135),        # Azul SQM
        "fg": (255, 255, 255),
        "accent": (255, 255, 255),
        "size": (256, 128)
    }
}


def render_corporate_sign(w: int, h: int, title: str, sub: str, bg: tuple, fg: tuple, accent: tuple) -> Image.Image:
    """Dibuja un cartel de entrada 3D corporativo de alta calidad."""
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Marco exterior plateado/metálico con bisel
    draw.rectangle([0, 0, w - 1, h - 1], fill=(195, 198, 202, 255), outline=(130, 134, 140, 255), width=2)
    # Fondo corporativo
    pad = 6 if w <= 256 else 12
    draw.rectangle([pad, pad, w - pad - 1, h - pad - 1], fill=(*bg, 255))

    # Franja inferior de acento
    banner_h = int(h * 0.26)
    banner_y = h - pad - banner_h
    draw.rectangle([pad, banner_y, w - pad - 1, h - pad - 1], fill=(*accent, 255))

    # Título principal
    scale = w / 256.0
    font_size_title = int((32 if len(title) <= 6 else (26 if len(title) <= 9 else 21)) * scale)
    try:
        font_title = ImageFont.truetype(FONT_BOLD, font_size_title)
    except Exception:
        font_title = ImageFont.load_default()

    center_y = (pad + banner_y) // 2
    # Sombra sutil de texto
    draw.text((w // 2 + 2, center_y + 2), title, font=font_title, fill=(0, 0, 0, 140), anchor="mm")
    draw.text((w // 2, center_y), title, font=font_title, fill=(*fg, 255), anchor="mm")

    # Subtítulo en franja de acento
    font_size_sub = int(11 * scale)
    try:
        font_sub = ImageFont.truetype(FONT_BOLD, font_size_sub)
    except Exception:
        font_sub = ImageFont.load_default()

    sub_center_y = banner_y + (banner_h // 2)
    # Contraste de texto de acento
    lum = (accent[0] * 0.299 + accent[1] * 0.587 + accent[2] * 0.114)
    sub_color = (20, 20, 20) if lum > 150 else (255, 255, 255)
    draw.text((w // 2, sub_center_y), sub.upper(), font=font_sub, fill=(*sub_color, 255), anchor="mm")

    return img


def generar_carteles_empresas():
    print("-> Generando carteles 3D de empresas en material/logo/...")
    target_dir = BASE_DIR / "material" / "logo"
    target_dir.mkdir(parents=True, exist_ok=True)

    for brand_id, bdata in COMPANY_3D_BRANDS.items():
        w, h = bdata["size"]
        im = render_corporate_sign(w, h, bdata["title"], bdata["sub"], bdata["bg"], bdata["fg"], bdata["accent"])
        save_dds(im, target_dir / f"{brand_id}.dds")
        copy_or_create_tobj(f"material/logo/{brand_id}.tobj", target_dir / f"{brand_id}.tobj", clamp=False)

    print(f"   [OK] {len(COMPANY_3D_BRANDS)} carteles 3D generados en material/logo/")


# ==============================================================================
# 3. TÓTEMS DE ENTRADA EN PREFABS (/prefab/tradeaux_warehouse/)
# ==============================================================================
def render_warehouse_totem(title: str, sub: str, bg: tuple, fg: tuple, accent: tuple) -> Image.Image:
    """Genera el letrero del tótem de entrada de 256x128 con marco metálico."""
    img = Image.new("RGBA", (256, 128), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Marco de chapa metálica cepillada gris
    draw.rectangle([0, 0, 255, 127], fill=(182, 185, 188, 255))
    draw.rectangle([4, 4, 251, 123], fill=(160, 163, 166, 255))
    draw.rectangle([8, 8, 247, 119], fill=(195, 198, 200, 255))

    # Panel interior con la marca chilena
    draw.rounded_rectangle([14, 16, 241, 111], radius=8, fill=(*bg, 255), outline=(255, 255, 255, 230), width=2)
    # Franja de acento inferior
    draw.rounded_rectangle([14, 84, 241, 111], radius=8, fill=(*accent, 255))
    draw.rectangle([14, 84, 241, 94], fill=(*accent, 255))

    # Título del tótem
    font_size = 24 if len(title) <= 9 else (20 if len(title) <= 12 else 17)
    font = ImageFont.truetype(FONT_BOLD, font_size)
    draw.text((128, 52), title, font=font, fill=(*fg, 255), anchor="mm")

    # Subtítulo
    lum = (accent[0] * 0.299 + accent[1] * 0.587 + accent[2] * 0.114)
    sub_color = (15, 15, 15) if lum > 150 else (255, 255, 255)
    font_sub = ImageFont.truetype(FONT_BOLD, 10)
    draw.text((128, 98), sub.upper(), font=font_sub, fill=(*sub_color, 255), anchor="mm")

    return img


def generar_totems_almacenes():
    print("-> Generando tótems de entrada en prefab/tradeaux_warehouse/...")
    target_dir = BASE_DIR / "prefab" / "tradeaux_warehouse"
    target_dir.mkdir(parents=True, exist_ok=True)

    # 1. Blue Express en lugar de Transinet
    im_bluex = render_warehouse_totem("BLUE EXPRESS", "DISTRIBUCIÓN NACIONAL", (0, 150, 214), (255, 255, 255), (255, 120, 0))
    save_dds(im_bluex, target_dir / "transinet_logo.dds")
    copy_or_create_tobj("prefab/tradeaux_warehouse/transinet_logo.tobj", target_dir / "transinet_logo.tobj")

    # 2. Starken en lugar de Tradeaux
    im_starken = render_warehouse_totem("STARKEN", "CARGA Y ENCOMIENDAS", (255, 102, 0), (255, 255, 255), (255, 235, 210))
    save_dds(im_starken, target_dir / "tradeaux_logo.dds")
    copy_or_create_tobj("prefab/tradeaux_warehouse/tradeaux_logo.tobj", target_dir / "tradeaux_logo.tobj")

    # 3. CCU en lugar de Stokes
    im_ccu = render_warehouse_totem("CCU", "CERVEZAS Y BEBIDAS", (11, 35, 65), (255, 255, 255), (212, 175, 55))
    save_dds(im_ccu, target_dir / "stokes_logo.dds")
    copy_or_create_tobj("prefab/tradeaux_warehouse/stokes_logo.tobj", target_dir / "stokes_logo.tobj")

    print("   [OK] Tótems de entrada generados exitosamente.")


# ==============================================================================
# 4. TÓTEMS DE ESTACIONES DE SERVICIO (/prefab/gas_small/)
# ==============================================================================
def render_fuel_price_stand(brand: str, sub: str, bg: tuple, fg: tuple, accent: tuple, prices: list) -> Image.Image:
    """
    Genera la textura 128x256 para el tótem de estación de servicio (price_stand).
    x=0..92: Panel de la marca y precios de combustible en CLP.
    x=93..127: Poste metálico y base de hormigón.
    """
    img = Image.new("RGBA", (128, 256), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Base de hormigón y poste metálico lateral
    draw.rectangle([94, 0, 127, 255], fill=(145, 148, 150, 255))
    for y_line in range(0, 256, 16):
        draw.line([(94, y_line), (127, y_line)], fill=(120, 122, 125, 255), width=1)
    draw.rectangle([0, 204, 127, 255], fill=(95, 92, 75, 255))  # Hormigón base

    # Panel del tótem (x=0..92, y=4..200)
    draw.rectangle([2, 4, 92, 200], fill=(*bg, 255), outline=(245, 245, 245, 255), width=2)

    # Cabecera de la marca
    font_brand = ImageFont.truetype(FONT_BOLD, 17 if len(brand) <= 5 else 13)
    draw.text((47, 22), brand, font=font_brand, fill=(*fg, 255), anchor="mm")

    # Franja de acento (Pronto / Upa! / Spacio 1)
    draw.rectangle([4, 38, 90, 58], fill=(*accent, 255))
    lum = (accent[0] * 0.299 + accent[1] * 0.587 + accent[2] * 0.114)
    sub_col = (20, 20, 20) if lum > 150 else (255, 255, 255)
    font_sub = ImageFont.truetype(FONT_BOLD, 10)
    draw.text((47, 48), sub.upper(), font=font_sub, fill=(*sub_col, 255), anchor="mm")

    # Panel digital de precios (pantalla LED negra)
    draw.rectangle([6, 64, 88, 168], fill=(18, 18, 18, 255), outline=(50, 50, 50, 255), width=1)

    font_grade = ImageFont.truetype(FONT_BOLD, 9)
    font_price = ImageFont.truetype(FONT_BOLD, 11)

    y_pos = 76
    for grade_name, grade_col, price_val in prices:
        # Nombre del combustible (ej. 93, 95, DIESEL)
        draw.text((12, y_pos), grade_name, font=font_grade, fill=(*grade_col, 255), anchor="lm")
        # Precio en pesos chilenos ($/litro)
        draw.text((82, y_pos), price_val, font=font_price, fill=(255, 215, 0, 255), anchor="rm")
        y_pos += 24

    # Pie del tótem
    font_foot = ImageFont.truetype(FONT_BOLD, 8)
    draw.text((47, 184), "24 HORAS", font=font_foot, fill=(255, 255, 255, 230), anchor="mm")

    return img


def generar_totems_combustible():
    print("-> Generando tótems de precios en prefab/gas_small/...")
    target_dir = BASE_DIR / "prefab" / "gas_small"
    target_dir.mkdir(parents=True, exist_ok=True)

    # Precios oficiales representativos de Chile en CLP/litro
    precios_copec = [
        ("93", (50, 205, 50), "$1.289"),
        ("95", (255, 190, 0), "$1.345"),
        ("97", (255, 50, 50), "$1.399"),
        ("DIE", (240, 240, 240), "$1.029")
    ]
    precios_shell = [
        ("V-Pow", (255, 60, 60), "$1.419"),
        ("95", (255, 210, 0), "$1.345"),
        ("93", (50, 205, 50), "$1.289"),
        ("EvoD", (240, 240, 240), "$1.029")
    ]
    precios_petrobras = [
        ("Pod", (255, 215, 0), "$1.429"),
        ("Grid", (50, 205, 50), "$1.345"),
        ("93", (255, 140, 0), "$1.289"),
        ("DIE", (240, 240, 240), "$1.029")
    ]

    # 1. Copec Pronto (price_stand_red.dds)
    im_copec = render_fuel_price_stand("COPEC", "PRONTO", (227, 6, 19), (255, 255, 255), (255, 255, 255), precios_copec)
    save_dds(im_copec, target_dir / "price_stand_red.dds")
    copy_or_create_tobj("prefab/gas_small/price_stand_red.tobj", target_dir / "price_stand_red.tobj")

    # 2. Shell Upa! (price_stand_blue.dds)
    im_shell = render_fuel_price_stand("SHELL", "UPA!", (255, 210, 0), (221, 29, 33), (221, 29, 33), precios_shell)
    save_dds(im_shell, target_dir / "price_stand_blue.dds")
    copy_or_create_tobj("prefab/gas_small/price_stand_blue.tobj", target_dir / "price_stand_blue.tobj")

    # 3. Petrobras Spacio 1 (price_stand_green.dds)
    im_petro = render_fuel_price_stand("PETROBRAS", "SPACIO 1", (0, 133, 66), (255, 255, 255), (255, 204, 0), precios_petrobras)
    save_dds(im_petro, target_dir / "price_stand_green.dds")
    copy_or_create_tobj("prefab/gas_small/price_stand_green.tobj", target_dir / "price_stand_green.tobj")

    print("   [OK] Tótems de combustible Copec, Shell y Petrobras generados.")


# ==============================================================================
# 5. MARQUESINAS Y ESTACIONES DE SERVICIO (/prefab/gas/)
# ==============================================================================
def generar_estaciones_servicio_prefabs():
    print("-> Generando texturas de marquesinas de estaciones en prefab/gas/...")
    target_dir = BASE_DIR / "prefab" / "gas"
    target_dir.mkdir(parents=True, exist_ok=True)

    base_dds_path = EXTRACT_DIR / "prefab" / "gas" / "gas_station.dds"
    if not base_dds_path.exists():
        print(f"   [AVISO] No se encontró {base_dds_path}, omitiendo modificación de textura base.")
        return

    # Cargar textura base SCS descomprimiendo DXT5
    with open(base_dds_path, "rb") as f:
        data = f.read()

    new_header = bytearray(data[:128])
    new_header[84:88] = b"DXT5"
    fixed_data = bytes(new_header) + data[148:]
    im_base = Image.open(io.BytesIO(fixed_data)).convert("RGBA")

    # 1. Versión COPEC PRONTO (gas_station.dds)
    # Marquesina roja Copec, franja blanca, logotipos COPEC y PRONTO
    im_copec = im_base.copy()
    draw_c = ImageDraw.Draw(im_copec)
    # Sustituir la franja azul europea de la marquesina con Rojo Copec
    draw_c.rectangle([0, 0, 1600, 360], fill=(227, 6, 19, 255))
    draw_c.rectangle([0, 320, 1600, 360], fill=(255, 255, 255, 255))  # Franja blanca

    font_copec = ImageFont.truetype(FONT_BOLD, 72)
    font_pronto = ImageFont.truetype(FONT_BOLD, 48)
    for x_brand in [250, 800, 1350]:
        draw_c.text((x_brand, 150), "COPEC", font=font_copec, fill=(255, 255, 255, 255), anchor="mm")
        draw_c.text((x_brand, 240), "PRONTO", font=font_pronto, fill=(255, 255, 255, 255), anchor="mm")

    save_dds(im_copec, target_dir / "gas_station.dds")
    copy_or_create_tobj("prefab/gas/gas_station.tobj", target_dir / "gas_station.tobj")

    # 2. Versión SHELL UPA! (gas_station_yellow.dds)
    # Marquesina amarilla Shell, franja roja, logotipos Shell y Upa!
    im_shell = im_base.copy()
    draw_s = ImageDraw.Draw(im_shell)
    draw_s.rectangle([0, 0, 1600, 360], fill=(255, 210, 0, 255))
    draw_s.rectangle([0, 320, 1600, 360], fill=(221, 29, 33, 255))  # Franja roja

    font_shell = ImageFont.truetype(FONT_BOLD, 72)
    font_upa = ImageFont.truetype(FONT_BOLD, 48)
    for x_brand in [250, 800, 1350]:
        draw_s.text((x_brand, 150), "SHELL", font=font_shell, fill=(221, 29, 33, 255), anchor="mm")
        draw_s.text((x_brand, 240), "upa!", font=font_upa, fill=(221, 29, 33, 255), anchor="mm")

    save_dds(im_shell, target_dir / "gas_station_yellow.dds")
    copy_or_create_tobj("prefab/gas/gas_station_yellow.tobj", target_dir / "gas_station_yellow.tobj")

    # 3. Versión PETROBRAS SPACIO 1 (gas_station_green.dds)
    # Marquesina verde Petrobras, franja amarilla, logotipos PETROBRAS y SPACIO 1
    im_petro = im_base.copy()
    draw_p = ImageDraw.Draw(im_petro)
    draw_p.rectangle([0, 0, 1600, 360], fill=(0, 133, 66, 255))
    draw_p.rectangle([0, 320, 1600, 360], fill=(255, 204, 0, 255))  # Franja amarilla

    font_petro = ImageFont.truetype(FONT_BOLD, 56)
    font_spacio = ImageFont.truetype(FONT_BOLD, 42)
    for x_brand in [250, 800, 1350]:
        draw_p.text((x_brand, 150), "PETROBRAS", font=font_petro, fill=(255, 255, 255, 255), anchor="mm")
        draw_p.text((x_brand, 240), "SPACIO 1", font=font_spacio, fill=(255, 204, 0, 255), anchor="mm")

    save_dds(im_petro, target_dir / "gas_station_green.dds")
    copy_or_create_tobj("prefab/gas/gas_station_green.tobj", target_dir / "gas_station_green.tobj")

    print("   [OK] Marquesinas de gasolinera Copec, Shell y Petrobras generadas.")


# ==============================================================================
# 6. TÓTEMS DE CARRETERA Y AUTOPISTA (/model/sign/gas/)
# ==============================================================================
def render_roadside_gas_sign(brand_idx: int) -> Image.Image:
    """Genera la textura 128x256 de los tótems de carretera para Europa sustituidos por Chile."""
    brands = [
        ("COPEC", "PRONTO", (227, 6, 19), (255, 255, 255), (255, 255, 255), "$1.289", "$1.345", "$1.029"),
        ("SHELL", "UPA!", (255, 210, 0), (221, 29, 33), (221, 29, 33), "$1.289", "$1.419", "$1.029"),
        ("PETROBRAS", "SPACIO 1", (0, 133, 66), (255, 255, 255), (255, 204, 0), "$1.289", "$1.345", "$1.029"),
        ("ARAMCO", "CHILE", (0, 163, 224), (255, 255, 255), (132, 189, 0), "$1.289", "$1.339", "$1.029")
    ]
    b = brands[brand_idx % len(brands)]
    name, store, bg, fg, accent, p93, p97, pdiesel = b

    img = Image.new("RGBA", (128, 256), (255, 255, 255, 255))
    draw = ImageDraw.Draw(img)

    # Panel superior de la marca
    draw.rectangle([0, 0, 127, 60], fill=(*bg, 255))
    font_name = ImageFont.truetype(FONT_BOLD, 18 if len(name) <= 6 else 14)
    draw.text((64, 24), name, font=font_name, fill=(*fg, 255), anchor="mm")

    # Franja de la tienda de conveniencia
    draw.rectangle([0, 60, 127, 86], fill=(*accent, 255))
    lum = (accent[0] * 0.299 + accent[1] * 0.587 + accent[2] * 0.114)
    store_col = (20, 20, 20) if lum > 150 else (255, 255, 255)
    font_store = ImageFont.truetype(FONT_BOLD, 11)
    draw.text((64, 73), store, font=font_store, fill=(*store_col, 255), anchor="mm")

    # Pantalla LED negra de precios
    draw.rectangle([0, 86, 127, 210], fill=(16, 16, 16, 255))
    font_lbl = ImageFont.truetype(FONT_BOLD, 10)
    font_val = ImageFont.truetype(FONT_BOLD, 12)

    # 93 Octanos
    draw.text((12, 110), "93", font=font_lbl, fill=(50, 205, 50, 255), anchor="lm")
    draw.text((116, 110), p93, font=font_val, fill=(255, 215, 0, 255), anchor="rm")

    # 97 Octanos / V-Power
    draw.text((12, 146), "97", font=font_lbl, fill=(255, 70, 70, 255), anchor="lm")
    draw.text((116, 146), p97, font=font_val, fill=(255, 215, 0, 255), anchor="rm")

    # Diesel
    draw.text((12, 182), "DIE", font=font_lbl, fill=(240, 240, 240, 255), anchor="lm")
    draw.text((116, 182), pdiesel, font=font_val, fill=(255, 215, 0, 255), anchor="rm")

    # Iconos inferiores de servicios (cafetería, cajero, baño, wifi)
    draw.rectangle([0, 210, 127, 255], fill=(235, 235, 235, 255))
    font_serv = ImageFont.truetype(FONT_BOLD, 9)
    draw.text((64, 232), "CAFÉ • WC • TAG", font=font_serv, fill=(40, 40, 40, 255), anchor="mm")

    return img


def generar_totems_carretera():
    print("-> Generando tótems de carretera en model/sign/gas/...")
    target_dir = BASE_DIR / "model" / "sign" / "gas"
    target_dir.mkdir(parents=True, exist_ok=True)

    sign_dir = EXTRACT_DIR / "model" / "sign" / "gas"
    if not sign_dir.exists():
        print(f"   [AVISO] No se encontró {sign_dir}, generando tótems principales.")
        paises = ["germany", "france", "austria", "czech", "poland", "uk", "italy", "dk", "swe", "nor", "swiss", "hungary"]
    else:
        paises = [f.stem.replace("gas_", "") for f in sign_dir.glob("gas_*.dds") if not f.stem.startswith("gas_big_")]

    for idx, p in enumerate(paises):
        im = render_roadside_gas_sign(idx)
        save_dds(im, target_dir / f"gas_{p}.dds")
        copy_or_create_tobj(f"model/sign/gas/gas_{p}.tobj", target_dir / f"gas_{p}.tobj")

        # Versión big (256x256)
        im_big = im.resize((256, 256), Image.Resampling.LANCZOS)
        save_dds(im_big, target_dir / f"gas_big_{p}.dds")
        copy_or_create_tobj(f"model/sign/gas/gas_big_{p}.tobj", target_dir / f"gas_big_{p}.tobj")

    print(f"   [OK] Tótems de carretera generados para {len(paises)} países base.")


# ==============================================================================
# 7. CARTELES MODERNOS DE EMPRESAS EN CIUDADES Y PREFABS (/model2/sign/company_logos/)
# ==============================================================================
# Sustituye los carteles de edificios, pórticos y tótems de los prefabs modernos
# (Euro Flow Ports -> STI Puerto San Antonio, ITCC -> ENAP, Transinet -> Blue Express, etc.)
MODEL2_COMPANY_MAPPING = {
    "euroflow": {
        "file": "euroflow",
        "title": "STI",
        "sub": "PUERTO SAN ANTONIO",
        "sec": "TERMINAL PORTUARIO",
        "bg": (0, 43, 73),
        "fg": (255, 255, 255),
        "accent": (0, 174, 239),
        "size": (512, 512),
    },
    "itcc": {
        "file": "itcc",
        "title": "ENAP",
        "sub": "REFINERÍAS DE CHILE",
        "sec": "PETRÓLEO Y ENERGÍA",
        "bg": (0, 45, 95),
        "fg": (255, 255, 255),
        "accent": (211, 17, 30),
        "size": (512, 256),
    },
    "transinet": {
        "file": "transinet_de",
        "title": "BLUE EXPRESS",
        "sub": "DISTRIBUCIÓN NACIONAL",
        "sec": "COURIER & CARGA CHILE",
        "bg": (0, 150, 214),
        "fg": (255, 255, 255),
        "accent": (255, 120, 0),
        "size": (512, 256),
    },
    "cargotras": {
        "file": "cargotras_it",
        "title": "BLUE EXPRESS",
        "sub": "CARGA PESADA",
        "sec": "DISTRIBUCIÓN NACIONAL",
        "bg": (0, 150, 214),
        "fg": (255, 255, 255),
        "accent": (255, 120, 0),
        "size": (512, 256),
    },
    "tradeaux": {
        "file": "tradeaux",
        "title": "STARKEN",
        "sub": "CARGA Y ENCOMIENDAS",
        "sec": "LOGÍSTICA INTEGRAL CHILE",
        "bg": (255, 102, 0),
        "fg": (255, 255, 255),
        "accent": (255, 235, 210),
        "size": (1024, 512),
    },
    "lkw": {
        "file": "lkw",
        "title": "STARKEN",
        "sub": "ENCOMIENDAS NACIONALES",
        "sec": "RED DE DISTRIBUCIÓN",
        "bg": (255, 102, 0),
        "fg": (255, 255, 255),
        "accent": (255, 235, 210),
        "size": (512, 256),
    },
    "gnt": {
        "file": "gnt_sc",
        "title": "STARKEN",
        "sub": "CENTRO DE ACOPIO",
        "sec": "HUB LOGÍSTICO",
        "bg": (255, 102, 0),
        "fg": (255, 255, 255),
        "accent": (255, 235, 210),
        "size": (512, 256),
    },
    "posped": {
        "file": "posped",
        "title": "CHILEXPRESS",
        "sub": "COURIER & LOGÍSTICA",
        "sec": "ENTREGAS EXPRESS",
        "bg": (255, 204, 0),
        "fg": (204, 0, 0),
        "accent": (35, 35, 35),
        "size": (512, 256),
    },
    "rt_log": {
        "file": "rt_log_ibe",
        "title": "CHILEXPRESS",
        "sub": "HUB DE DISTRIBUCIÓN",
        "sec": "LOGÍSTICA REGIONAL",
        "bg": (255, 204, 0),
        "fg": (204, 0, 0),
        "accent": (35, 35, 35),
        "size": (512, 256),
    },
    "fle": {
        "file": "fle_fr",
        "title": "CHILEXPRESS",
        "sub": "CTP AEROPUERTO",
        "sec": "CARGA AÉREA Y ENCOMIENDAS",
        "bg": (255, 204, 0),
        "fg": (204, 0, 0),
        "accent": (35, 35, 35),
        "size": (512, 256),
    },
    "euro_goodies": {
        "file": "euro_goodies",
        "title": "LIDER",
        "sub": "WALMART CHILE",
        "sec": "CENTRO DE DISTRIBUCIÓN",
        "bg": (0, 70, 145),
        "fg": (255, 255, 255),
        "accent": (255, 194, 32),
        "size": (512, 256),
    },
    "renat": {
        "file": "renat_balt",
        "title": "LIDER",
        "sub": "LIDER LOGÍSTICA",
        "sec": "ABASTECIMIENTO NACIONAL",
        "bg": (0, 70, 145),
        "fg": (255, 255, 255),
        "accent": (255, 194, 32),
        "size": (512, 256),
    },
    "sellplan": {
        "file": "sellplan",
        "title": "UNIMARC",
        "sub": "SUPERMERCADO CHILENO",
        "sec": "EL SUPERMERCADO DE CHILE",
        "bg": (211, 17, 30),
        "fg": (255, 255, 255),
        "accent": (255, 220, 220),
        "size": (512, 256),
    },
    "kaarfor": {
        "file": "kaarfor_fr",
        "title": "CENCOSUD",
        "sub": "JUMBO / EASY / SANTA ISABEL",
        "sec": "RETAIL Y DISTRIBUCIÓN",
        "bg": (0, 122, 51),
        "fg": (255, 255, 255),
        "accent": (255, 255, 255),
        "size": (512, 256),
    },
    "renar_logistik": {
        "file": "renar_logistik_sc",
        "title": "CENCOSUD",
        "sub": "CENCOSUD LOGÍSTICA",
        "sec": "CENTRO DE DISTRIBUCIÓN",
        "bg": (0, 122, 51),
        "fg": (255, 255, 255),
        "accent": (255, 255, 255),
        "size": (512, 256),
    },
    "san_builders": {
        "file": "san_builders",
        "title": "SODIMAC",
        "sub": "HOMECENTER CHILE",
        "sec": "CONSTRUCCIÓN Y HOGAR",
        "bg": (0, 68, 124),
        "fg": (255, 255, 255),
        "accent": (245, 179, 36),
        "size": (512, 256),
    },
    "eumefa": {
        "file": "eumefa",
        "title": "SODIMAC",
        "sub": "HOMECENTER",
        "sec": "MATERIALES DE CONSTRUCCIÓN",
        "bg": (0, 68, 124),
        "fg": (255, 255, 255),
        "accent": (245, 179, 36),
        "size": (512, 256),
    },
    "domdepo": {
        "file": "domdepo_balt",
        "title": "SODIMAC",
        "sub": "CONSTRUCTOR",
        "sec": "GRANDES OBRAS Y MATERIALES",
        "bg": (0, 68, 124),
        "fg": (255, 255, 255),
        "accent": (245, 179, 36),
        "size": (512, 256),
    },
    "ika_bohag": {
        "file": "ika_bohag_sc",
        "title": "FALABELLA",
        "sub": "RETAIL CHILE",
        "sec": "TIENDA POR DEPARTAMENTOS",
        "bg": (0, 168, 89),
        "fg": (255, 255, 255),
        "accent": (255, 255, 255),
        "size": (512, 256),
    },
    "cesare_smar": {
        "file": "cesare_smar_it",
        "title": "FALABELLA",
        "sub": "FALABELLA LOGÍSTICA",
        "sec": "DISTRIBUCIÓN NACIONAL",
        "bg": (0, 168, 89),
        "fg": (255, 255, 255),
        "accent": (255, 255, 255),
        "size": (512, 256),
    },
    "fcp": {
        "file": "fcp",
        "title": "SOPROLE",
        "sub": "LÁCTEOS Y DERIVADOS",
        "sec": "ALIMENTACIÓN SALUDABLE",
        "bg": (0, 51, 153),
        "fg": (255, 255, 255),
        "accent": (220, 20, 60),
        "size": (512, 256),
    },
    "bcp": {
        "file": "bcp_de",
        "title": "CAROZZI",
        "sub": "ALIMENTOS Y PASTAS",
        "sec": "TRADICIÓN CHILENA",
        "bg": (179, 0, 0),
        "fg": (255, 255, 255),
        "accent": (255, 255, 255),
        "size": (512, 256),
    },
    "granoro": {
        "file": "granoro",
        "title": "CAROZZI",
        "sub": "MOLINOS Y HARINAS",
        "sec": "MOLIENDA DE TRIGO",
        "bg": (179, 0, 0),
        "fg": (255, 255, 255),
        "accent": (255, 255, 255),
        "size": (512, 256),
    },
    "euro_acres": {
        "file": "euro_acres",
        "title": "AGROSUPER",
        "sub": "ALIMENTOS DE CHILE",
        "sec": "PRODUCCIÓN PECUARIA",
        "bg": (227, 6, 19),
        "fg": (255, 255, 255),
        "accent": (255, 215, 0),
        "size": (512, 256),
    },
    "libellula": {
        "file": "libellula_it",
        "title": "AGROSUPER",
        "sub": "COMPLEJO LO MIRANDA",
        "sec": "AGROINDUSTRIA CHILE",
        "bg": (227, 6, 19),
        "fg": (255, 255, 255),
        "accent": (255, 215, 0),
        "size": (512, 256),
    },
    "trameri": {
        "file": "trameri",
        "title": "COLUN",
        "sub": "LA MAGIA DEL SUR",
        "sec": "COOPERATIVA LECHERA",
        "bg": (0, 102, 178),
        "fg": (255, 255, 255),
        "accent": (255, 255, 255),
        "size": (512, 256),
    },
    "charmey": {
        "file": "charmey_ch",
        "title": "COLUN",
        "sub": "QUESOS DEL SUR",
        "sec": "PLANTA LECHERA LA UNIÓN",
        "bg": (0, 102, 178),
        "fg": (255, 255, 255),
        "accent": (255, 255, 255),
        "size": (512, 256),
    },
    "treeet": {
        "file": "treeet",
        "title": "ARAUCO",
        "sub": "CELULOSA Y MADERAS",
        "sec": "FORESTAL ARAUCO",
        "bg": (0, 90, 54),
        "fg": (255, 255, 255),
        "accent": (144, 238, 144),
        "size": (512, 256),
    },
    "scs_paper": {
        "file": "scs_paper_blke",
        "title": "CMPC",
        "sub": "PAPELES Y CELULOSA",
        "sec": "FORESTAL MININCO",
        "bg": (0, 102, 68),
        "fg": (255, 255, 255),
        "accent": (255, 255, 255),
        "size": (512, 256),
    },
    "stokes": {
        "file": "stokes",
        "title": "CCU",
        "sub": "BEBIDAS Y CERVEZAS",
        "sec": "COMPAÑÍA CERVECERÍAS UNIDAS",
        "bg": (11, 35, 65),
        "fg": (255, 255, 255),
        "accent": (212, 175, 55),
        "size": (512, 256),
    },
    "nbfc": {
        "file": "nbfc",
        "title": "EMBONOR",
        "sub": "COCA-COLA CHILE",
        "sec": "EMBOTELLADORA EMBONOR",
        "bg": (204, 0, 0),
        "fg": (255, 255, 255),
        "accent": (255, 255, 255),
        "size": (512, 256),
    },
    "shuttle_cola": {
        "file": "shuttle_cola",
        "title": "ANDINA",
        "sub": "COCA-COLA CHILE",
        "sec": "EMBOTELLADORA ANDINA",
        "bg": (227, 6, 19),
        "fg": (255, 255, 255),
        "accent": (255, 255, 255),
        "size": (512, 256),
    },
    "spinelli": {
        "file": "spinelli_it",
        "title": "CONCHA Y TORO",
        "sub": "VIÑA DE CHILE",
        "sec": "BODEGAS Y VINIFICACIÓN",
        "bg": (88, 17, 26),
        "fg": (255, 255, 255),
        "accent": (212, 175, 55),
        "size": (512, 256),
    },
    "wgcc": {
        "file": "wgcc",
        "title": "SQM",
        "sub": "LITIO Y MINERALES",
        "sec": "SALAR DE ATACAMA",
        "bg": (0, 75, 135),
        "fg": (255, 255, 255),
        "accent": (255, 255, 255),
        "size": (512, 256),
    },
    "kathode": {
        "file": "kathode_at",
        "title": "CAP ACERO",
        "sub": "SIDERÚRGICA HUACHIPATO",
        "sec": "ACEROS DE CHILE",
        "bg": (45, 55, 72),
        "fg": (255, 255, 255),
        "accent": (245, 158, 11),
        "size": (512, 256),
    },
    "aci": {
        "file": "aci_it",
        "title": "ACEROS AZA",
        "sub": "SIDERÚRGICA DE CHILE",
        "sec": "ACEROS RECICLADOS",
        "bg": (35, 45, 60),
        "fg": (255, 255, 255),
        "accent": (220, 38, 38),
        "size": (512, 256),
    },
    "cnp": {
        "file": "cnp_it",
        "title": "MOLYMET",
        "sub": "MOLIBDENO & RENIO",
        "sec": "MINERÍA ESPECIALIZADA",
        "bg": (30, 58, 138),
        "fg": (255, 255, 255),
        "accent": (96, 165, 250),
        "size": (512, 256),
    },
    "piac": {
        "file": "piac_it",
        "title": "CAP MINERÍA",
        "sub": "HIERRO ATACAMA",
        "sec": "MINA LOS COLORADOS",
        "bg": (120, 53, 15),
        "fg": (255, 255, 255),
        "accent": (245, 158, 11),
        "size": (512, 256),
    },
    "stronghold": {
        "file": "stronghold",
        "title": "POLPAICO",
        "sub": "CEMENTO & HORMIGÓN",
        "sec": "MATERIALES DE CONSTRUCCIÓN",
        "bg": (208, 16, 24),
        "fg": (255, 255, 255),
        "accent": (255, 255, 255),
        "size": (512, 256),
    },
    "dfh": {
        "file": "dfh_de",
        "title": "IANSA",
        "sub": "EMPRESAS IANSA",
        "sec": "ALIMENTOS Y AZÚCAR",
        "bg": (0, 132, 61),
        "fg": (255, 255, 255),
        "accent": (255, 255, 255),
        "size": (512, 256),
    },
    "suikersmij": {
        "file": "suikersmij",
        "title": "IANSA",
        "sub": "PLANTA AZUCARERA",
        "sec": "REMOLACHA Y DERIVADOS",
        "bg": (0, 132, 61),
        "fg": (255, 255, 255),
        "accent": (255, 255, 255),
        "size": (512, 256),
    },
    "polar_fish": {
        "file": "polar_fish_sc",
        "title": "AQUACHILE",
        "sub": "SALMONES DEL SUR",
        "sec": "PUERTO MONTT - AYSÉN",
        "bg": (0, 102, 153),
        "fg": (255, 255, 255),
        "accent": (135, 206, 250),
        "size": (512, 256),
    },
    "globeur": {
        "file": "globeur_fr",
        "title": "DOLE CHILE",
        "sub": "FRUTAS DE EXPORTACIÓN",
        "sec": "VALLES DE CHILE",
        "bg": (0, 128, 0),
        "fg": (255, 255, 255),
        "accent": (255, 215, 0),
        "size": (512, 256),
    },
    "fallow_cargo": {
        "file": "fallow_cargo_blke",
        "title": "IDEAL",
        "sub": "PANIFICACIÓN BIMBO",
        "sec": "PLANTA QUILICURA",
        "bg": (240, 240, 240),
        "fg": (0, 51, 153),
        "accent": (204, 0, 0),
        "size": (512, 256),
    },
    "drekkartrans": {
        "file": "drekkartrans_sc",
        "title": "WATT'S",
        "sub": "ALIMENTOS Y LÁCTEOS",
        "sec": "DISTRIBUCIÓN NACIONAL",
        "bg": (255, 119, 0),
        "fg": (255, 255, 255),
        "accent": (255, 255, 255),
        "size": (512, 256),
    },
    "agronord": {
        "file": "agronord_sc",
        "title": "WATT'S",
        "sub": "LONCOLECHE",
        "sec": "PLANTA OSORNO",
        "bg": (255, 119, 0),
        "fg": (255, 255, 255),
        "accent": (255, 255, 255),
        "size": (512, 256),
    },
    "tesore_gust": {
        "file": "tesore_gust_it",
        "title": "WATT'S",
        "sub": "PLANTAS LECHERAS",
        "sec": "LACTEOS DEL SUR",
        "bg": (255, 119, 0),
        "fg": (255, 255, 255),
        "accent": (255, 255, 255),
        "size": (512, 256),
    },
    "bhv": {
        "file": "bhv_sc",
        "title": "SIMUNOVIC",
        "sub": "FRIGORÍFICO AUSTRAL",
        "sec": "PUNTA ARENAS PATAGONIA",
        "bg": (102, 0, 0),
        "fg": (255, 255, 255),
        "accent": (255, 255, 255),
        "size": (512, 256),
    },
    "balkan_loco": {
        "file": "balkan_loco_blke",
        "title": "FEPASA",
        "sub": "FERROCARRIL DEL PACÍFICO",
        "sec": "TRANSPORTE FERROVIARIO",
        "bg": (0, 75, 140),
        "fg": (255, 255, 255),
        "accent": (245, 158, 11),
        "size": (512, 256),
    },
    "eolo_lines": {
        "file": "eolo_lines_it",
        "title": "TRANSMARCHILAY",
        "sub": "FERRIES DE CHILE",
        "sec": "CONECTIVIDAD CANAL DE CHACAO",
        "bg": (0, 51, 102),
        "fg": (255, 255, 255),
        "accent": (0, 180, 230),
        "size": (512, 256),
    },
    "marina": {
        "file": "marina_it",
        "title": "TABSA",
        "sub": "TRANSBORDADORES AUSTRAL",
        "sec": "CONECTIVIDAD MAGALLANES",
        "bg": (0, 40, 85),
        "fg": (255, 255, 255),
        "accent": (255, 204, 0),
        "size": (512, 256),
    },
    "cont_port_it": {
        "file": "cont_port_it",
        "title": "PUERTO CORONEL",
        "sub": "TERMINAL MARÍTIMO",
        "sec": "EXPORTACIÓN FORESTAL BÍOBÍO",
        "bg": (0, 102, 102),
        "fg": (255, 255, 255),
        "accent": (255, 255, 255),
        "size": (512, 256),
    },
    "subse": {
        "file": "subse_fr",
        "title": "TPS",
        "sub": "PUERTO VALPARAÍSO",
        "sec": "TERMINAL PACÍFICO SUR",
        "bg": (0, 51, 102),
        "fg": (255, 255, 255),
        "accent": (0, 204, 255),
        "size": (512, 256),
    },
    "tdc_auto": {
        "file": "tdc_auto_ibe",
        "title": "PUERTO SAN ANTONIO",
        "sub": "TERMINAL AUTOMÓVILES",
        "sec": "DESEMBARQUE VEHICULAR",
        "bg": (0, 43, 73),
        "fg": (255, 255, 255),
        "accent": (0, 174, 239),
        "size": (512, 256),
    },
    "voitureux": {
        "file": "voitureux_fr",
        "title": "GILDEMEISTER",
        "sub": "AUTOMOTRIZ CHILE",
        "sec": "IMPORTACIÓN VEHÍCULOS",
        "bg": (20, 35, 60),
        "fg": (255, 255, 255),
        "accent": (220, 38, 38),
        "size": (512, 256),
    },
}


def render_model2_sign_512x256(title: str, sub: str, sec: str, bg: tuple, fg: tuple, accent: tuple, w: int = 512, h: int = 256) -> Image.Image:
    """Renderiza el cartel corporativo moderno para model2/sign/company_logos (512x256 o 1024x512)."""
    scale = w / 512.0
    im = Image.new("RGBA", (w, h), (218, 220, 222, 255))
    draw = ImageDraw.Draw(im)

    # Marco exterior metálico
    draw.rectangle([0, 0, w - 1, h - 1], outline=(145, 148, 150, 255), width=int(3 * scale))

    # Panel principal del cartel (blanco con borde del color de marca)
    pad_x = int(12 * scale)
    pad_y = int(20 * scale)
    draw.rounded_rectangle([pad_x, pad_y, w - pad_x, h - pad_y], radius=int(12 * scale), fill=(255, 255, 255, 255), outline=(*bg, 255), width=int(4 * scale))

    # Barra superior de acento con color de marca
    bar_top_h = int(24 * scale)
    draw.rounded_rectangle([pad_x, pad_y, w - pad_x, pad_y + bar_top_h], radius=int(12 * scale), fill=(*bg, 255))
    draw.rectangle([pad_x, pad_y + int(12 * scale), w - pad_x, pad_y + bar_top_h], fill=(*bg, 255))

    # Título principal de la empresa chilena
    font_size_t = int((54 if len(title) <= 6 else (42 if len(title) <= 10 else 32)) * scale)
    font_t = ImageFont.truetype(FONT_BOLD, font_size_t)
    draw.text((w // 2, int(108 * scale)), title, font=font_t, fill=(*bg, 255), anchor="mm")

    # Franja intermedia de acento
    accent_y = int(155 * scale)
    accent_h = int(8 * scale)
    draw.rectangle([int(30 * scale), accent_y, w - int(30 * scale), accent_y + accent_h], fill=(*accent, 255))

    # Subtítulo (ej. REFINERÍAS DE CHILE, DISTRIBUCIÓN NACIONAL)
    font_size_s = int(20 * scale)
    font_s = ImageFont.truetype(FONT_BOLD, font_size_s)
    draw.text((w // 2, int(185 * scale)), sub.upper(), font=font_s, fill=(*bg, 255), anchor="mm")

    # Línea secundaria de ubicación / giro
    font_size_sec = int(12 * scale)
    font_sec = ImageFont.truetype(FONT_BOLD, font_size_sec)
    draw.text((w // 2, int(216 * scale)), sec.upper(), font=font_sec, fill=(100, 105, 110, 255), anchor="mm")

    return im


def render_model2_euroflow_512x512() -> Image.Image:
    """Renderiza el cartel de Puerto San Antonio (STI) adaptado a la geometría de euroflow.dds (512x512)."""
    im = Image.new("RGBA", (512, 512), (210, 212, 215, 255))
    draw = ImageDraw.Draw(im)

    # Marco exterior metálico
    draw.rectangle([0, 0, 511, 511], outline=(150, 153, 156, 255), width=4)

    # Panel del letrero de azotea y tótem (x=20..492, y=60..360)
    draw.rounded_rectangle([20, 60, 492, 360], radius=16, fill=(255, 255, 255, 255), outline=(0, 43, 73, 255), width=5)

    font_sti = ImageFont.truetype(FONT_BOLD, 78)
    font_sub = ImageFont.truetype(FONT_BOLD, 28)
    font_sec = ImageFont.truetype(FONT_BOLD, 16)

    # Título STI
    draw.text((256, 140), "STI", font=font_sti, fill=(0, 43, 73, 255), anchor="mm")

    # Franja cian marítima
    draw.rectangle([60, 195, 452, 205], fill=(0, 174, 239, 255))

    # PUERTO SAN ANTONIO
    draw.text((256, 245), "PUERTO SAN ANTONIO", font=font_sub, fill=(0, 43, 73, 255), anchor="mm")

    # SAN ANTONIO TERMINAL INTERNACIONAL
    draw.text((256, 305), "SAN ANTONIO TERMINAL INTERNACIONAL", font=font_sec, fill=(0, 120, 180, 255), anchor="mm")

    # Paneles direccionales y flechas inferiores (y=380..500)
    draw.rounded_rectangle([20, 380, 246, 500], radius=8, fill=(255, 255, 255, 255), outline=(0, 43, 73, 255), width=3)
    draw.text((133, 425), "STI", font=ImageFont.truetype(FONT_BOLD, 36), fill=(0, 43, 73, 255), anchor="mm")
    draw.text((133, 470), "ACCESO PUERTO", font=ImageFont.truetype(FONT_BOLD, 13), fill=(0, 174, 239, 255), anchor="mm")

    draw.rounded_rectangle([266, 380, 492, 500], radius=8, fill=(0, 43, 73, 255))
    draw.text((379, 425), "ENTRADA", font=ImageFont.truetype(FONT_BOLD, 24), fill=(255, 255, 255, 255), anchor="mm")
    draw.text((379, 470), "CARGA Y CONTENEDORES", font=ImageFont.truetype(FONT_BOLD, 11), fill=(0, 174, 239, 255), anchor="mm")

    return im


def generar_carteles_model2_modernos():
    print("-> Generando carteles modernos de prefabs en model2/sign/company_logos/...")
    base_m2 = BASE_DIR / "model2" / "sign" / "company_logos"

    count = 0
    for comp_dir, info in MODEL2_COMPANY_MAPPING.items():
        fname = info["file"]
        target_dir = base_m2 / comp_dir
        target_dir.mkdir(parents=True, exist_ok=True)

        w, h = info["size"]
        if comp_dir == "euroflow":
            im = render_model2_euroflow_512x512()
        else:
            im = render_model2_sign_512x256(info["title"], info["sub"], info["sec"], info["bg"], info["fg"], info["accent"], w, h)

        dds_path = target_dir / f"{fname}.dds"
        save_dds(im, dds_path)

        tobj_path = target_dir / f"{fname}.tobj"
        copy_or_create_tobj(f"model2/sign/company_logos/{comp_dir}/{fname}.tobj", tobj_path, clamp=False)
        count += 1

    print(f"   [OK] {count} carteles modernos generados exitosamente en model2/sign/company_logos/")


# ==============================================================================
# FUNCIÓN PRINCIPAL
# ==============================================================================
def main():
    print("=" * 75)
    print(" TRANSPORTE AUSTRAL - GENERADOR DE TEXTURAS 3D Y MARCAS CHILENAS (ETS2)")
    print("=" * 75)
    generar_carteles_empresas()
    generar_totems_almacenes()
    generar_totems_combustible()
    generar_estaciones_servicio_prefabs()
    generar_totems_carretera()
    generar_carteles_model2_modernos()
    print("=" * 75)
    print("¡Generación 3D completada con éxito!")
    print("=" * 75)


if __name__ == "__main__":
    main()
