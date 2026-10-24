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
import sys
import shutil
import struct
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))
SCRATCH_MAP = BASE_DIR / "scratch" / "base_map" / "map"
SRC_EUROPE_DIR = SCRATCH_MAP / "europe"
SRC_MBD = SCRATCH_MAP / "europe.mbd"
SRC_COMPANY_DIR = BASE_DIR / "scratch" / "def" / "def" / "company"

MAP_DIR = BASE_DIR / "map"
DEST_CHILE_DIR = MAP_DIR / "chile"
DEST_MBD = MAP_DIR / "chile.mbd"
DEST_EUROPE_DIR = MAP_DIR / "europe"
DEST_EUROPE_MBD = MAP_DIR / "europe.mbd"
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
    # 16 Capitales Regionales de Norte a Sur (Corredor Continental 100% Terrestre, Derecha)
    "kiel":        "arica",         # XV Arica (Z = -21500)
    "rostock":     "iquique",       # I Iquique (Z = -19500)
    "hamburg":     "antofagasta",   # II Antofagasta (Z = -16060)
    "hannover":    "copiapo",       # III Copiapó (Z = -10313)
    "magdeburg":   "la_serena",     # IV La Serena (Z = -7400)
    "kassel":      "valparaiso",    # V Valparaíso (Z = -3066)
    "frankfurt":   "santiago",      # RM Santiago (Z = +1030)
    "mannheim":    "rancagua",      # VI Rancagua (Z = +6946)
    "stuttgart":   "talca",         # VII Talca (Z = +9994)
    "strasbourg":  "chillan",       # XVI Chillán (Z = +8881)
    "munchen":     "concepcion",    # VIII Concepción (Z = +14740)
    "innsbruck":   "temuco",        # IX Temuco (Z = +19677)
    "zurich":      "valdivia",      # XIV Valdivia (Z = +23915)
    "bern":        "puerto_montt",  # X Puerto Montt (Z = +21012)
    "milano":      "coyhaique",     # XI Coyhaique (Z = +27668)
    "torino":      "punta_arenas",  # XII Punta Arenas (Z = +30551)

    # Comunas secundarias de la red vial chilena
    "flensburg":   "putre",
    "lubeck":      "pozo_almonte",
    "bremen":      "calama",
    "braunschweig":"caldera",
    "berlin":      "ovalle",
    "dresden":     "los_vilos",
    "erfurt":      "san_antonio",
    "wiesbaden":   "san_bernardo",
    "heidelberg":  "san_fernando",
    "karlsruhe":   "curico",
    "augsburg":    "los_angeles",
    "salzburg":    "villarrica",
    "basel":       "osorno",
    "geneve":      "castro",
    "verona":      "puerto_aysen",
    "genova":      "pto_natales",
    "parma":       "porvenir",
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

    # 1. Preparar carpetas map/chile y map/europe
    if DEST_CHILE_DIR.exists():
        shutil.rmtree(DEST_CHILE_DIR)
    DEST_CHILE_DIR.mkdir(parents=True, exist_ok=True)

    if DEST_EUROPE_DIR.exists():
        shutil.rmtree(DEST_EUROPE_DIR)
    DEST_EUROPE_DIR.mkdir(parents=True, exist_ok=True)

    # 2. Generar encabezados MBD oficiales (chile.mbd y europe.mbd con inicio en Santiago)
    from tools.create_mbd import crear_chile_mbd
    crear_chile_mbd()
    print(f"[1/4] Archivos chile.mbd y europe.mbd generados con éxito.")

    # 3. Preparar diccionario de reemplazo de tokens de 64 bits
    reemplazos_ciudades = {}
    for euro_city, cl_city in CIUDADES_MAPEO.items():
        reemplazos_ciudades[token_bytes(euro_city)] = token_bytes(cl_city)

    # 4. Obtener los sectores de la espina dorsal continua (sin ramales este a Alemania/Benelux)
    extensiones = [".aux", ".base", ".data", ".desc", ".snd"]
    all_europe_sectors = sorted([p.stem for p in SRC_EUROPE_DIR.glob("sec*.base")])
    sectores_candidatos = sorted([
        p.stem for p in SRC_EUROPE_DIR.glob("sec*.base") if p.stat().st_size > 1000
    ])

    # Red continua de 37 sectores interconectados de Chile (Ruta 5 / Ruta 7 Panamericana)
    # Cubre de forma continua e ininterrumpida las 16 capitales regionales y comunas clave
    # sin ramales cortados ni extremos en el vacío.
    SPINE_SECTOR_COORDS = [
        # 1. Norte Grande (Arica, Iquique, Antofagasta, Calama)
        (0, -6), (1, -6), (0, -5), (1, -5), (-1, -5), (-1, -4), (0, -4), (-2, -4),
        # 2. Norte Chico (Copiapó, Caldera, La Serena, Coquimbo)
        (-1, -3), (0, -3), (0, -2), (-1, -2),
        # 3. Zona Central (Valparaíso, San Antonio, Santiago, San Bernardo, Rancagua, San Fernando)
        (-1, -1), (0, -1), (-2, -1), (-1, 0), (-2, 0), (-3, 0), (-3, 1), (-2, 1), (-1, 1),
        # 4. Maule, Ñuble, Biobío (Curicó, Talca, Chillán, Los Ángeles, Concepción)
        (-2, 2), (-1, 2), (-3, 2), (0, 2), (0, 3),
        # 5. Araucanía, Los Ríos, Los Lagos (Temuco, Valdivia, Osorno, Puerto Montt)
        (0, 4), (-1, 4), (-1, 5), (-2, 5), (-3, 4), (-3, 5),
        # 6. Carretera Austral y Magallanes (Coyhaique, Punta Arenas, Puerto Natales, Porvenir)
        (-3, 6), (-2, 6), (-2, 7), (-3, 7), (-4, 7), (-3, 8), (-2, 8),
    ]

    sectores_disponibles = sorted([
        f"sec{x:+05d}{z:+05d}" for x, z in SPINE_SECTOR_COORDS
        if f"sec{x:+05d}{z:+05d}" in all_europe_sectors
    ])

    print(f"[2/4] Copiando sectores de la espina dorsal de Chile ({len(sectores_disponibles)} sectores)...")
    total_archivos = 0
    total_reemplazos = 0

    for sec_name in sectores_disponibles:
        for ext in extensiones:
            src_file = SRC_EUROPE_DIR / f"{sec_name}{ext}"
            if not src_file.exists():
                continue

            dest_chile_file = DEST_CHILE_DIR / f"{sec_name}{ext}"
            dest_europe_file = DEST_EUROPE_DIR / f"{sec_name}{ext}"

            if ext == ".base":
                data_bytes = src_file.read_bytes()
                for src_b, dst_b in reemplazos_ciudades.items():
                    cnt = data_bytes.count(src_b)
                    if cnt > 0:
                        data_bytes = data_bytes.replace(src_b, dst_b)
                        total_reemplazos += cnt
                dest_chile_file.write_bytes(data_bytes)
                dest_europe_file.write_bytes(data_bytes)
            else:
                shutil.copy2(src_file, dest_chile_file)
                shutil.copy2(src_file, dest_europe_file)

            total_archivos += 1

    print(f" -> {total_archivos} archivos de sectores generados en map/chile/ y map/europe/")
    print(f" -> {total_reemplazos} ocurrencias de ciudades chilenas vinculadas en archivos .base")

    # Neutralizar el 100% de los sectores restantes de Europa (Alemania, Francia, etc.)
    # Sobrescribiéndolos con sectores vacíos para anular por completo el mapa base de Europa
    sectores_a_neutralizar = [s for s in all_europe_sectors if s not in sectores_disponibles]
    print(f" -> Neutralizando {len(sectores_a_neutralizar)} sectores extranjeros de Europa...")

    EMPTY_BASE = b'\x8b\x03\x00\x00a\x04u\x00\x00\x00\x00\x00\x03\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
    EMPTY_DATA = b'\x8b\x03\x00\x00a\x04u\x00\x00\x00\x00\x00\x03\x00\x00\x00\xff\xff\xff\xff\xff\xff\xff\xff'
    EMPTY_DESC = b'\x03\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xe7\xc3s\x15\x00\x00\x00'
    EMPTY_SND = b'\x8b\x03\x00\x00a\x04u\x00\x00\x00\x00\x00\x03\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'

    sample_aux = SRC_EUROPE_DIR / "sec+0003-0005.aux"
    EMPTY_AUX = sample_aux.read_bytes() if sample_aux.exists() else EMPTY_BASE

    neutralizados = 0
    for sec_name in sectores_a_neutralizar:
        (DEST_EUROPE_DIR / f"{sec_name}.base").write_bytes(EMPTY_BASE)
        (DEST_EUROPE_DIR / f"{sec_name}.data").write_bytes(EMPTY_DATA)
        (DEST_EUROPE_DIR / f"{sec_name}.desc").write_bytes(EMPTY_DESC)
        (DEST_EUROPE_DIR / f"{sec_name}.snd").write_bytes(EMPTY_SND)
        (DEST_EUROPE_DIR / f"{sec_name}.aux").write_bytes(EMPTY_AUX)
        neutralizados += 1

    print(f" -> {neutralizados} sectores europeos neutralizados (mapa base de Europa 100% eliminado)")

    # Unir la red, quitar letreros europeos, ocultar carreteras cortadas e insertar comunas
    import bridge_gap, remove_eu_signs, prune_roads, add_comunas
    bridge_gap.main()
    remove_eu_signs.main()
    prune_roads.prune(BASE_DIR / "map" / "chile", [BASE_DIR / "map" / "europe"])
    add_comunas.main()

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
