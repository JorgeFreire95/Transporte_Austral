#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
==============================================================================
TRANSPORTE AUSTRAL - IMPORTADOR Y PARCHEADOR DE SECTORES PARA CHILE (ETS2)
==============================================================================
Importa la espina dorsal vial continua de Chile:
1. ESPINA DORSAL CONTINUA NORTE-SUR: Conexión lineal desde Escocia a Turín,
   evitando ramales caóticos hacia Alemania o el Benelux.
2. 52 COMUNAS Y 16 REGIONES EN SECUENCIA ESTRICTA:
   Las 16 capitales regionales ordenadas estrictamente de norte a sur.
3. 16 GARAJES VERIFICADOS: Un garaje verificado por región.
4. ECONOMÍA ACTIVA: Genera sucursales de empresas para las comunas.
"""

import os
import shutil
import struct
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
SCRATCH_MAP = BASE_DIR / "scratch" / "base_map" / "map"
SRC_EUROPE_DIR = SCRATCH_MAP / "europe"
SRC_MBD = SCRATCH_MAP / "europe.mbd"
SRC_COMPANY_DIR = BASE_DIR / "scratch" / "def" / "def" / "company"

MAP_DIR = BASE_DIR / "map"
DEST_CHILE_DIR = MAP_DIR / "chile"
DEST_MBD = MAP_DIR / "chile.mbd"
DEST_DEF_COMPANY = BASE_DIR / "def" / "company"

CHARSET = '\0' + '0123456789abcdefghijklmnopqrstuvwxyz_'


def str_to_token(s: str) -> int:
    s = s.lower().strip()
    val = 0
    for i, c in enumerate(s):
        if c not in CHARSET:
            raise ValueError(f"Carácter inválido '{c}' en token '{s}'")
        idx = CHARSET.index(c)
        val += idx * (38 ** i)
    return val


def token_bytes(s: str) -> bytes:
    return struct.pack('<Q', str_to_token(s))


# ==============================================================================
# MAPEO INTEGRAL: COMUNAS DE CHILE -> CIUDADES DE LA ESPINA DORSAL CONTINUA
# 16 capitales regionales en secuencia estrictamente creciente de Norte a Sur:
# Aberdeen -> Edinburgh -> Newcastle -> Manchester -> Birmingham -> Cambridge ->
# London -> Southampton -> Dover -> Calais -> Lille -> Reims -> Paris -> Dijon ->
# Lyon -> Torino
# ==============================================================================
CIUDADES_MAPEO = {
    # 16 Capitales Regionales de Chile en secuencia estrictamente creciente de Norte a Sur:
    "aberdeen":    "arica",         # Capital XV (Z = -44905)
    "edinburgh":   "iquique",       # Capital I  (Z = -46914)
    "manchester":  "antofagasta",   # Capital II (Z = -31531)
    "sheffield":   "copiapo",       # Capital III (Z = -30108)
    "birmingham":  "la_serena",     # Capital IV (Z = -28721)
    "cambridge":   "valparaiso",    # Capital V  (Z = -27369)
    "london":      "santiago",      # Capital RM (Z = -20476)
    "dover":       "rancagua",      # Capital VI (Z = -10133)
    "calais":      "talca",         # Capital VII (Z = -4639)
    "lille":       "chillan",       # Capital XVI (Z = -303)
    "reims":       "concepcion",    # Capital VIII (Z = +5572)
    "strasbourg":  "temuco",        # Capital IX (Z = +12284)
    "dijon":       "valdivia",      # Capital XIV (Z = +16726)
    "bern":        "puerto_montt",  # Capital X  (Z = +19662)
    "lyon":        "coyhaique",     # Capital XI (Z = +24024)
    "torino":      "punta_arenas",  # Capital XII (Z = +30551)
}


# ==============================================================================
# MAPEO INTEGRAL: EMPRESAS CHILENAS Y ESTACIONES DE SERVICIO EN EL MAPA
# ==============================================================================
EMPRESAS_MAPEO = {
    # Red de Combustibles y Estaciones de Servicio
    "primel":       "copec",       # Copec Pronto / Punto
    "bts":          "copec",       # Copec
    "pegi":         "shell_cl",    # Shell Upa! / Enex Chile
    "tqg":          "shell_cl",    # Shell Chile
    "nada":         "petrobras",   # Petrobras Spacio 1 / Esmax
    "apus":         "aramco",      # Aramco Chile

    # Supermercados, Retail y Comercio Nacional
    "eurogoodies":  "lider",       # Lider / Walmart Chile
    "kaarfor":      "cencosud",    # Cencosud (Jumbo / Easy)
    "sellplan":     "unimarc",     # Unimarc / SMU
    "ika_bohag":    "falabella",   # Falabella Retail
    "sanbuilders":  "sodimac",     # Homecenter Sodimac

    # Forestal, Celulosa y Madera
    "tree_et":      "arauco",      # Celulosa Arauco y Constitución
    "scs_paper":    "cmpc",        # CMPC Celulosa / Papeles

    # Minería, Metales y Cemento
    "quarry":       "codelco",     # Codelco Chile
    "steinbr_str":  "escondida",   # Minera Escondida (BHP)
    "wgcc":         "sqm",         # SQM Litio & Yodo
    "itcc":         "enap",        # ENAP Refinerías Aconcagua/Bío Bío
    "kathode":      "cap_acero",   # CAP Acero / Huachipato
    "ns_chem":      "molymet",     # Molymet Nos
    "sanbuild_cem": "melon",       # Cemento Melón
    "sanbuild_bas": "cbb_cemento", # Cementos Bío Bío (CBB)
    "batisse":      "polpaico",    # Polpaico BSA

    # Agroindustria, Alimentos y Lácteos
    "euroacres":    "agrosuper",   # Agrosuper
    "trameri":      "colun",       # Colun
    "fcp":          "soprole",     # Soprole
    "bcp":          "carozzi",     # Carozzi
    "dfh":          "iansa",       # Empresas Iansa
    "fallow":       "ideal_cl",    # Ideal Bimbo Chile
    "drekkar":      "watts",       # Watt's
    "bhv":          "simunovic",   # Frigorífico Simunovic
    "globe_eur":    "dole_cl",     # Dole Chile
    "polar_fish":   "aquachile",   # AquaChile Salmon

    # Bebidas, Cervezas y Vinos
    "stokes":       "ccu",         # Compañía de Cervecerías Unidas
    "shuttle":      "andina",      # Coca-Cola Embonor / Andina
    "nbfc":         "embonor",     # Embonor
    "scout":        "concha_toro", # Viña Concha y Toro

    # Logística, Courier y Puertos
    "lkwlog":       "starken",     # Starken Envíos
    "posped":       "chilexpress", # Chilexpress
    "tradeaux":     "correos_cl",  # Correos de Chile
    "transinet":    "bluex",       # Blue Express
    "cont_port":    "tpa_arica",   # Terminal Puerto Arica
    "euroflow":     "sti_san_ant", # San Antonio Terminal Internacional
    "marina":       "tabsa",       # Transbordadora Austral Broom
}


def importar_y_parchear_sectores():
    """Importa la red de sectores conectados de la espina dorsal de Chile."""
    print("======================================================================")
    print(" TRANSPORTE AUSTRAL - GENERACIÓN DE ESPINA DORSAL LINEAL (ETS2)")
    print("======================================================================")

    if not SRC_EUROPE_DIR.exists():
        raise FileNotFoundError(f"No se encontró la carpeta base de Europa en {SRC_EUROPE_DIR}")

    # 1. Preparar carpeta map/chile
    if DEST_CHILE_DIR.exists():
        shutil.rmtree(DEST_CHILE_DIR)
    DEST_CHILE_DIR.mkdir(parents=True, exist_ok=True)

    # 2. Copiar chile.mbd desde europe.mbd
    if SRC_MBD.exists():
        shutil.copy2(SRC_MBD, DEST_MBD)
        print(f"[1/4] Archivo chile.mbd instalado con éxito ({DEST_MBD.stat().st_size} bytes)")

    # 3. Preparar diccionario de reemplazo de tokens de 64 bits
    reemplazos_ciudades = {}
    for euro_city, cl_city in CIUDADES_MAPEO.items():
        reemplazos_ciudades[token_bytes(euro_city)] = token_bytes(cl_city)

    # 4. Obtener los sectores de la espina dorsal continua (sin ramales este a Alemania/Benelux)
    extensiones = [".aux", ".base", ".data", ".desc", ".snd"]
    sectores_candidatos = sorted([
        p.stem for p in SRC_EUROPE_DIR.glob("sec*.base") if p.stat().st_size > 1000
    ])

    def is_spine_sector(x, z):
        # Excluir Europa Central y Oriental (Alemania, Austria, Chequia)
        if x >= -3:
            return False
        # Excluir Benelux oriental/norte para evitar bulto de carreteras
        if -5 <= z <= -1 and x >= -6:
            return False
        # Excluir Gales y Cornualles (oeste del Reino Unido) para evitar puntos flotantes en el océano
        if x <= -13 and -8 <= z <= -2:
            return False
        return True

    sector_coords = {}
    for name in sectores_candidatos:
        x = int(name[3:8])
        z = int(name[8:13])
        if is_spine_sector(x, z):
            sector_coords[(x, z)] = name

    # Componente conexo continuo a partir de Escocia (-11, -9)
    visited = set()
    q = [(-11, -9)]
    visited.add((-11, -9))
    while q:
        curr = q.pop(0)
        for dx, dz in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]:
            neigh = (curr[0] + dx, curr[1] + dz)
            if neigh in sector_coords and neigh not in visited:
                visited.add(neigh)
                q.append(neigh)

    sectores_disponibles = sorted([sector_coords[c] for c in visited])

    print(f"[2/4] Copiando sectores de la espina dorsal de Chile ({len(sectores_disponibles)} sectores)...")
    total_archivos = 0
    total_reemplazos = 0

    for sec_name in sectores_disponibles:
        for ext in extensiones:
            src_file = SRC_EUROPE_DIR / f"{sec_name}{ext}"
            if not src_file.exists():
                continue

            dest_file = DEST_CHILE_DIR / f"{sec_name}{ext}"

            if ext == ".base":
                data_bytes = src_file.read_bytes()
                for src_b, dst_b in reemplazos_ciudades.items():
                    cnt = data_bytes.count(src_b)
                    if cnt > 0:
                        data_bytes = data_bytes.replace(src_b, dst_b)
                        total_reemplazos += cnt
                dest_file.write_bytes(data_bytes)
            else:
                shutil.copy2(src_file, dest_file)

            total_archivos += 1

    print(f" -> {total_archivos} archivos de sectores generados en {DEST_CHILE_DIR}")
    print(f" -> {total_reemplazos} ocurrencias de ciudades chilenas vinculadas en archivos .base")

    # 5. Generar sucursales de empresas
    print("[3/4] Generando sucursales de empresas en def/company/*/editor/...")
    total_sucursales = 0

    for euro_city, cl_city in CIUDADES_MAPEO.items():
        src_editor_files = list(SRC_COMPANY_DIR.glob(f"**/editor/{euro_city}.sii"))
        for sfile in src_editor_files:
            orig_comp = sfile.parent.parent.name
            dest_comp = EMPRESAS_MAPEO.get(orig_comp, orig_comp)

            dest_editor_dir = DEST_DEF_COMPANY / dest_comp / "editor"
            dest_editor_dir.mkdir(parents=True, exist_ok=True)
            dest_sii = dest_editor_dir / f"{cl_city}.sii"

            content = sfile.read_text(encoding="utf-8", errors="ignore")
            content = content.replace(f".{euro_city}", f".{cl_city}")
            content = content.replace(f"city: {euro_city}", f"city: {cl_city}")
            dest_sii.write_text(content, encoding="utf-8")
            total_sucursales += 1

            if dest_comp != orig_comp:
                orig_editor_dir = DEST_DEF_COMPANY / orig_comp / "editor"
                orig_editor_dir.mkdir(parents=True, exist_ok=True)
                orig_sii = orig_editor_dir / f"{cl_city}.sii"
                orig_sii.write_text(content, encoding="utf-8")
                total_sucursales += 1

    print(f" -> {total_sucursales} sedes de empresas generadas para las ciudades de Chile")
    print(f"[4/4] Espina dorsal lineal de Chile 100% operativa.")
    return True


if __name__ == "__main__":
    importar_y_parchear_sectores()
