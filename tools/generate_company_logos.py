#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
==============================================================================
TRANSPORTE AUSTRAL - GENERADOR DE LOGOS UI DE EMPRESAS CHILENAS (ETS2)
==============================================================================
Genera las texturas DDS, descriptores TOBJ y materiales MAT para:
1. material/ui/company/<comp_id>.dds / .tobj / .mat (Logos de la bolsa de fletes, 256x128)
2. material/ui/company/small/<comp_id>.dds / .tobj / .mat (Iconos del mapa / GPS, 64x64)

Sustituye completamente los logos europeos (EuroGoodies, SellPlan, Tree-Et, etc.)
por las marcas oficiales de Chile en la pantalla de selección de trabajos.
"""

import os
import sys
import struct
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR / "tools"))

import generator

# Paleta y estilos corporativos por marca chilena
BRAND_STYLES = {
    "unimarc":       {"bg": (211, 17, 30),   "fg": (255, 255, 255), "accent": (255, 220, 220), "title": "UNIMARC",      "sub": "SUPERMERCADO"},
    "lider":         {"bg": (0, 70, 145),    "fg": (255, 255, 255), "accent": (255, 194, 32),  "title": "LIDER",        "sub": "WALMART CHILE"},
    "cencosud":      {"bg": (0, 122, 51),    "fg": (255, 255, 255), "accent": (255, 255, 255), "title": "CENCOSUD",     "sub": "JUMBO / EASY"},
    "arauco":        {"bg": (0, 90, 54),     "fg": (255, 255, 255), "accent": (144, 238, 144), "title": "ARAUCO",       "sub": "CELULOSA Y MADERAS"},
    "cmpc":          {"bg": (0, 102, 68),    "fg": (255, 255, 255), "accent": (255, 255, 255), "title": "CMPC",         "sub": "FORESTAL Y PAPEL"},
    "enap":          {"bg": (0, 51, 102),    "fg": (255, 255, 255), "accent": (204, 0, 0),     "title": "ENAP",         "sub": "REFINERÍAS DE CHILE"},
    "starken":       {"bg": (255, 102, 0),   "fg": (255, 255, 255), "accent": (255, 230, 200), "title": "STARKEN",      "sub": "CARGA Y ENCOMIENDAS"},
    "chilexpress":   {"bg": (255, 204, 0),   "fg": (204, 0, 0),     "accent": (51, 51, 51),     "title": "CHILEXPRESS",  "sub": "COURIER & LOGÍSTICA"},
    "bluex":         {"bg": (0, 150, 214),   "fg": (255, 255, 255), "accent": (255, 255, 255), "title": "BLUE EXPRESS", "sub": "DISTRIBUCIÓN NACIONAL"},
    "correos_cl":    {"bg": (0, 48, 135),    "fg": (255, 255, 255), "accent": (227, 6, 19),    "title": "CORREOS",      "sub": "DE CHILE"},
    "agrosuper":     {"bg": (227, 6, 19),    "fg": (255, 255, 255), "accent": (255, 215, 0),   "title": "AGROSUPER",    "sub": "ALIMENTOS DE CHILE"},
    "colun":         {"bg": (0, 102, 178),   "fg": (255, 255, 255), "accent": (255, 255, 255), "title": "COLUN",        "sub": "LA MAGIA DEL SUR"},
    "soprole":       {"bg": (0, 51, 153),    "fg": (255, 255, 255), "accent": (220, 20, 60),   "title": "SOPROLE",      "sub": "LÁCTEOS Y DERIVADOS"},
    "carozzi":       {"bg": (179, 0, 0),     "fg": (255, 255, 255), "accent": (255, 255, 255), "title": "CAROZZI",      "sub": "ALIMENTOS Y HARINAS"},
    "ccu":           {"bg": (11, 35, 65),    "fg": (255, 255, 255), "accent": (212, 175, 55),  "title": "CCU",          "sub": "BEBIDAS Y CERVEZAS"},
    "andina":        {"bg": (227, 6, 19),    "fg": (255, 255, 255), "accent": (255, 255, 255), "title": "ANDINA",       "sub": "COCA-COLA CHILE"},
    "embonor":       {"bg": (204, 0, 0),     "fg": (255, 255, 255), "accent": (255, 255, 255), "title": "EMBONOR",      "sub": "COCA-COLA EMBONOR"},
    "concha_toro":   {"bg": (88, 17, 26),    "fg": (255, 255, 255), "accent": (212, 175, 55),  "title": "CONCHA Y TORO","sub": "VIÑA DE CHILE"},
    "austral_pza":   {"bg": (0, 26, 51),     "fg": (255, 255, 255), "accent": (102, 178, 255), "title": "AUSTRAL",      "sub": "PATAGONIA CHILE"},
    "kunstmann":     {"bg": (139, 69, 19),   "fg": (255, 255, 255), "accent": (255, 215, 0),   "title": "KUNSTMANN",    "sub": "VALDIVIA CHILE"},
    "iansa":         {"bg": (0, 132, 61),    "fg": (255, 255, 255), "accent": (255, 255, 255), "title": "IANSA",        "sub": "EMPRESAS IANSA"},
    "copec":         {"bg": (227, 6, 19),    "fg": (255, 255, 255), "accent": (255, 255, 255), "title": "COPEC",        "sub": "PRONTO & PUNTO"},
    "shell_cl":      {"bg": (255, 210, 0),   "fg": (221, 29, 33),   "accent": (221, 29, 33),   "title": "SHELL",        "sub": "UPA! & CHILE"},
    "petrobras":     {"bg": (0, 133, 66),    "fg": (255, 255, 255), "accent": (255, 204, 0),   "title": "PETROBRAS",    "sub": "SPACIO 1"},
    "petrobras_cl":  {"bg": (0, 133, 66),    "fg": (255, 255, 255), "accent": (255, 204, 0),   "title": "PETROBRAS",    "sub": "SPACIO 1"},
    "aramco":        {"bg": (0, 163, 224),   "fg": (255, 255, 255), "accent": (132, 189, 0),   "title": "ARAMCO",       "sub": "CHILE"},
    "codelco":       {"bg": (200, 90, 23),   "fg": (255, 255, 255), "accent": (255, 220, 180), "title": "CODELCO",      "sub": "MINERÍA DEL COBRE"},
    "escondida":     {"bg": (26, 43, 76),    "fg": (255, 255, 255), "accent": (241, 90, 36),   "title": "ESCONDIDA",    "sub": "BHP CHILE"},
    "sqm":           {"bg": (0, 75, 135),    "fg": (255, 255, 255), "accent": (255, 255, 255), "title": "SQM",          "sub": "LITIO Y NITRATOS"},
    "cap_acero":     {"bg": (45, 55, 72),    "fg": (255, 255, 255), "accent": (245, 158, 11),  "title": "CAP ACERO",    "sub": "SIDERÚRGICA HUACHIPATO"},
    "molymet":       {"bg": (30, 58, 138),   "fg": (255, 255, 255), "accent": (96, 165, 250),  "title": "MOLYMET",      "sub": "MOLIBDENO & RENIO"},
    "sodimac":       {"bg": (0, 68, 124),    "fg": (255, 255, 255), "accent": (245, 179, 36),  "title": "SODIMAC",      "sub": "HOMECENTER"},
    "falabella":     {"bg": (0, 168, 89),    "fg": (255, 255, 255), "accent": (255, 255, 255), "title": "FALABELLA",    "sub": "RETAIL CHILE"},
    "ripley":        {"bg": (102, 45, 145),  "fg": (255, 255, 255), "accent": (255, 255, 255), "title": "RIPLEY",       "sub": "RETAIL & LOGÍSTICA"},
    "melon":         {"bg": (51, 51, 51),    "fg": (255, 255, 255), "accent": (255, 209, 0),   "title": "MELÓN",        "sub": "CEMENTOS CHILE"},
    "cbb_cemento":   {"bg": (0, 56, 107),    "fg": (255, 255, 255), "accent": (255, 255, 255), "title": "CBB",          "sub": "CEMENTOS BÍO BÍO"},
    "polpaico":      {"bg": (208, 16, 24),   "fg": (255, 255, 255), "accent": (255, 255, 255), "title": "POLPAICO",     "sub": "CEMENTO & HORMIGÓN"},
    "sti_san_ant":   {"bg": (0, 43, 73),     "fg": (255, 255, 255), "accent": (0, 174, 239),   "title": "STI",          "sub": "PUERTO SAN ANTONIO"},
    "tps_valp":      {"bg": (0, 51, 102),    "fg": (255, 255, 255), "accent": (0, 204, 255),   "title": "TPS",          "sub": "PUERTO VALPARAÍSO"},
    "tpa_arica":     {"bg": (0, 75, 135),    "fg": (255, 255, 255), "accent": (255, 102, 0),   "title": "TPA ARICA",    "sub": "TERMINAL PORTUARIO"},
    "pto_coronel":   {"bg": (0, 102, 102),   "fg": (255, 255, 255), "accent": (255, 255, 255), "title": "PTO CORONEL", "sub": "EXPORTACIÓN FORESTAL"},
    "tabsa":         {"bg": (0, 40, 85),     "fg": (255, 255, 255), "accent": (255, 204, 0),   "title": "TABSA",        "sub": "CONECTIVIDAD AUSTRAL"},
    "ideal_cl":      {"bg": (240, 240, 240), "fg": (0, 51, 153),   "accent": (204, 0, 0),     "title": "IDEAL",        "sub": "PANIFICACIÓN BIMBO"},
    "watts":         {"bg": (255, 119, 0),   "fg": (255, 255, 255), "accent": (255, 255, 255), "title": "WATT'S",       "sub": "LONCOLECHE & ALIMENTOS"},
    "dole_cl":       {"bg": (0, 128, 0),     "fg": (255, 255, 255), "accent": (255, 215, 0),   "title": "DOLE CHILE",   "sub": "FRUTAS DE EXPORTACIÓN"},
    "aquachile":     {"bg": (0, 102, 153),   "fg": (255, 255, 255), "accent": (135, 206, 250), "title": "AQUACHILE",    "sub": "SALMONES DEL SUR"},
    "simunovic":     {"bg": (102, 0, 0),     "fg": (255, 255, 255), "accent": (255, 255, 255), "title": "SIMUNOVIC",    "sub": "FRIGORÍFICO AUSTRAL"}
}


def write_tobj(file_path: Path, texture_rel_path: str, clamp: bool = True):
    file_path.parent.mkdir(parents=True, exist_ok=True)
    norm_path = texture_rel_path.replace("\\", "/")
    if not norm_path.startswith("/"):
        norm_path = "/" + norm_path

    path_bytes = norm_path.encode("utf-8")
    path_len = len(path_bytes)
    addr = 0x01 if clamp else 0x00

    header_bytes = bytes([
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

    with open(file_path, "wb") as f:
        f.write(header_bytes)
        f.write(struct.pack("<Q", path_len))
        f.write(path_bytes)


def write_mat(file_path: Path, tobj_rel_path: str):
    file_path.parent.mkdir(parents=True, exist_ok=True)
    norm_path = tobj_rel_path.replace("\\", "/")
    content = f"""material : "ui"
{{
    texture : "{norm_path}"
    texture_name : "texture"
}}
"""
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)


def get_style_for_company(comp_id: str):
    # Buscar directo
    if comp_id in BRAND_STYLES:
        return BRAND_STYLES[comp_id]
    # Buscar en REBRAND_BASE_COMPANIES
    if comp_id in generator.REBRAND_BASE_COMPANIES:
        trailer = generator.REBRAND_BASE_COMPANIES[comp_id].get("trailer", "")
        if trailer in BRAND_STYLES:
            return BRAND_STYLES[trailer]
        name = generator.REBRAND_BASE_COMPANIES[comp_id].get("nombre", comp_id)
        sort = generator.REBRAND_BASE_COMPANIES[comp_id].get("sort", comp_id.upper())
        return {
            "bg": (24, 43, 73),
            "fg": (255, 255, 255),
            "accent": (255, 194, 32),
            "title": sort[:12],
            "sub": name[:24]
        }
    # Buscar en EMPRESAS_CHILENAS
    if comp_id in generator.EMPRESAS_CHILENAS:
        name = generator.EMPRESAS_CHILENAS[comp_id].get("nombre", comp_id)
        return {
            "bg": (20, 50, 90),
            "fg": (255, 255, 255),
            "accent": (255, 255, 255),
            "title": comp_id.upper()[:12],
            "sub": name[:24]
        }
    # Fallback
    return {
        "bg": (30, 41, 59),
        "fg": (255, 255, 255),
        "accent": (255, 204, 0),
        "title": comp_id.upper()[:12],
        "sub": "CHILE"
    }


def generar_logo_ui(comp_id: str, company_dir: Path, small_dir: Path):
    style = get_style_for_company(comp_id)
    title = style["title"]
    sub = style["sub"]
    bg = style["bg"]
    fg = style["fg"]
    accent = style["accent"]

    # Tipografías
    font_bold = r"C:\Windows\Fonts\arialbd.ttf"
    font_reg = r"C:\Windows\Fonts\arial.ttf"

    # 1. Logo principal para el Mercado de Trabajo (256x128)
    img_main = Image.new("RGBA", (256, 128), (0, 0, 0, 0))
    draw_main = ImageDraw.Draw(img_main)

    # Fondo insignia con esquinas redondeadas
    draw_main.rounded_rectangle([6, 8, 250, 120], radius=14, fill=(*bg, 255), outline=(255, 255, 255, 240), width=3)
    # Franja inferior de acento
    draw_main.rounded_rectangle([6, 94, 250, 120], radius=14, fill=(*accent, 255))
    draw_main.rectangle([6, 94, 250, 104], fill=(*accent, 255))

    # Título principal
    font_size_main = 30 if len(title) <= 8 else (24 if len(title) <= 11 else 20)
    font_title = ImageFont.truetype(font_bold, font_size_main)
    draw_main.text((128, 52), title, font=font_title, fill=(*fg, 255), anchor="mm")

    # Subtítulo en franja de acento
    sub_color = (20, 20, 20) if (accent[0]*0.299 + accent[1]*0.587 + accent[2]*0.114) > 160 else (255, 255, 255)
    font_sub = ImageFont.truetype(font_bold, 11)
    draw_main.text((128, 107), sub.upper(), font=font_sub, fill=(*sub_color, 255), anchor="mm")

    # Guardar DDS, TOBJ y MAT principal
    dds_main = company_dir / f"{comp_id}.dds"
    img_main.save(dds_main, format="DDS")
    tobj_main = company_dir / f"{comp_id}.tobj"
    write_tobj(tobj_main, f"/material/ui/company/{comp_id}.dds")
    mat_main = company_dir / f"{comp_id}.mat"
    write_mat(mat_main, f"/material/ui/company/{comp_id}.tobj")

    # 2. Icono para Mapa y GPS (64x64): insignia circular con monograma, sin texto largo
    S = 8
    big = Image.new("RGBA", (64 * S, 64 * S), (0, 0, 0, 0))
    db = ImageDraw.Draw(big)
    db.ellipse([2 * S, 2 * S, 62 * S, 62 * S], fill=(*bg, 255), outline=(255, 255, 255, 255), width=3 * S)
    db.ellipse([9 * S, 9 * S, 55 * S, 55 * S], outline=(*accent, 255), width=2 * S)
    words = title.replace("'", "").split()
    mono = title if len(title) <= 4 else (words[0][0] + words[1][0] if len(words) > 1 else words[0][0])
    mono = mono.upper()
    fsz = {1: 36, 2: 28, 3: 17, 4: 13}[len(mono)] * S
    db.text((32 * S, 32 * S), mono, font=ImageFont.truetype(font_bold, fsz), fill=(*fg, 255), anchor="mm")
    img_small = big.resize((64, 64), Image.LANCZOS)

    dds_small = small_dir / f"{comp_id}.dds"
    img_small.save(dds_small, format="DDS")
    tobj_small = small_dir / f"{comp_id}.tobj"
    write_tobj(tobj_small, f"/material/ui/company/small/{comp_id}.dds")
    mat_small = small_dir / f"{comp_id}.mat"
    write_mat(mat_small, f"/material/ui/company/small/{comp_id}.tobj")


def generar_todos_los_logos():
    print("=" * 70)
    print(" TRANSPORTE AUSTRAL - GENERADOR DE LOGOS CORPORATIVOS DE CHILE (ETS2)")
    print("=" * 70)

    company_dir = BASE_DIR / "material" / "ui" / "company"
    small_dir = company_dir / "small"
    company_dir.mkdir(parents=True, exist_ok=True)
    small_dir.mkdir(parents=True, exist_ok=True)

    # Conjunto total de empresas: 47 chilenas + 95 prefabs base rebrandeados
    all_companies = set()
    for cid in generator.EMPRESAS_CHILENAS:
        if len(cid) <= 12:
            all_companies.add(cid)

    for bid in generator.REBRAND_BASE_COMPANIES:
        if len(bid) <= 12:
            all_companies.add(bid)

    # Concesionarios
    for dlr in ["scania_dlr", "volvo_dlr", "daf_dlr", "daf_fac"]:
        all_companies.add(dlr)

    print(f"-> Generando logos UI completos (256x128 y 64x64) para {len(all_companies)} empresas...")

    count = 0
    for comp in sorted(all_companies):
        generar_logo_ui(comp, company_dir, small_dir)
        count += 1

    print(f"-> {count} logos corporativos generados exitosamente en material/ui/company/")
    print(f"-> {count} iconos de mapa generados exitosamente en material/ui/company/small/")
    print("=" * 70)


if __name__ == "__main__":
    generar_todos_los_logos()
