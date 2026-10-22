#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
==============================================================================
TRANSPORTE AUSTRAL - GENERADOR BINARIO DE ARCHIVO MBD (CHILE.MBD)
==============================================================================
Genera la cabecera binaria oficial de Prism3D para Euro Truck Simulator 2
correspondiente a un módulo de mapa independiente (chile.mbd).
"""

import struct
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
MAP_DIR = BASE_DIR / "map"
MBD_FILE = MAP_DIR / "chile.mbd"
EUROPE_MBD = MAP_DIR / "europe.mbd"

# Token charset SCS
CHARSET = [
    '\0', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'a', 'b',
    'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o',
    'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', '_'
]


def string_to_token(s: str) -> int:
    token = 0
    for i, c in enumerate(s.lower()):
        token += (38 ** i) * CHARSET.index(c)
    return token


def crear_chile_mbd():
    MAP_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Header SCS Prism3D Map
    core_map_version = 907            # Map format version (ETS2 1.50 - 1.61+)
    game_id = string_to_token("euro2") # 7668833 (euro2 token)
    game_map_version = 3              # uint32

    # 2. Map descriptor
    editor_map_id = 0x123456789ABCDEF0 # ulong
    start_pos_x = -39700.0            # Santiago centro (coordenadas reales en sector sec-0010-0003)
    start_pos_y = 100.0
    start_pos_z = -11000.0
    start_sector_magic = 0x4B000800    # uint32
    rot_x = 0.0                        # Quaternion identity
    rot_y = 0.0
    rot_z = 0.0
    rot_w = 1.0
    game_tag = 2998976734              # uint32
    normal_scale = 19.0                # float 1:19
    city_scale = 3.0                   # float 1:3
    europe_map_ui_corrections = 0      # byte

    # Empaquetar en little-endian estándar de x86_64
    binary_data = struct.pack(
        "<IQIQfffIffffIffB",
        core_map_version,
        game_id,
        game_map_version,
        editor_map_id,
        start_pos_x, start_pos_y, start_pos_z,
        start_sector_magic,
        rot_x, rot_y, rot_z, rot_w,
        game_tag,
        normal_scale,
        city_scale,
        europe_map_ui_corrections
    )

    with open(MBD_FILE, "wb") as f:
        f.write(binary_data)
    print(f"-> Archivo '{MBD_FILE.name}' generado exitosamente ({len(binary_data)} bytes).")

    with open(EUROPE_MBD, "wb") as f:
        f.write(binary_data)
    print(f"-> Archivo '{EUROPE_MBD.name}' generado exitosamente ({len(binary_data)} bytes, sustituye el mapa base de Europa).")

    return MBD_FILE


if __name__ == "__main__":
    crear_chile_mbd()
