#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
==============================================================================
TRANSPORTE AUSTRAL - ADMINISTRADOR DE SECTORES DEL MAPA (SCS MAP EDITOR)
==============================================================================
Herramienta de utilidad para:
1. Listar y auditar los sectores .base/.data/.desc creados en map/chile/
2. Crear copias de seguridad (backups) automáticas con marca de tiempo.
3. Identificar qué comunas o rutas de Chile caen dentro de cada sector guardado.
"""

import os
import sys
import shutil
import re
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
MAP_DIR = BASE_DIR / "map" / "chile"
BACKUP_DIR = BASE_DIR / "backups"


def auditar_sectores():
    """Analiza los archivos de sectores generados por el SCS Map Editor"""
    print("=" * 70)
    print(" AUDITORÍA DE SECTORES: map/chile/")
    print("=" * 70)

    if not MAP_DIR.exists():
        MAP_DIR.mkdir(parents=True, exist_ok=True)
        print("-> Carpeta map/chile/ creada. Aún no se han guardado sectores del editor.")
        print("   Para guardar sectores: En el editor de mapa de ETS2 pulsa consola y escribe: save chile")
        return

    archivos = list(MAP_DIR.glob("sec*.*"))
    if not archivos:
        print("-> No hay sectores guardados en map/chile/ todavía.")
        print("   Cuando guardes tu mapa en el editor con 'save chile', los sectores aparecerán aquí.")
        return

    sectores_base = list(MAP_DIR.glob("sec*.base"))
    print(f"-> Total de sectores base (.base) encontrados: {len(sectores_base)}")
    print(f"-> Total de archivos auxiliares (.data, .desc, .aux): {len(archivos) - len(sectores_base)}")

    sector_regex = re.compile(r"sec([+-]\d{4})([+-]\d{4})\.base")

    for sec in sorted(sectores_base):
        m = sector_regex.match(sec.name)
        if m:
            sx = int(m.group(1))
            sz = int(m.group(2))
            # Rango en coordenadas del juego
            x_min = sx * 4000
            x_max = (sx + 1) * 4000
            z_min = sz * 4000
            z_max = (sz + 1) * 4000
            print(f"   Sector {sec.name:<18} | Rango X: [{x_min:8d}, {x_max:8d}] | Rango Z: [{z_min:8d}, {z_max:8d}]")


def crear_backup():
    """Crea un backup zip o copia de seguridad de la carpeta map/"""
    if not MAP_DIR.exists() or not any(MAP_DIR.iterdir()):
        print("-> No hay sectores que respaldar en map/chile/.")
        return

    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = BACKUP_DIR / f"map_chile_backup_{timestamp}.zip"

    shutil.make_archive(str(backup_file.with_suffix("")), "zip", BASE_DIR / "map")
    print(f"-> Backup creado exitosamente: {backup_file.name}")


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "backup":
        crear_backup()
    else:
        auditar_sectores()


if __name__ == "__main__":
    main()
