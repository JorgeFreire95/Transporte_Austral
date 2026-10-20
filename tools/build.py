#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
==============================================================================
TRANSPORTE AUSTRAL - COMPILADOR Y EMPAQUETADOR DE MOD SCS (ETS2)
==============================================================================
Herramienta de compilación y validación automática para Euro Truck Simulator 2:
1. Valida la sintaxis de archivos SII y la existencia de dependencias SUI.
2. Empaqueta el mod en un archivo .scs estándar (ZIP con compresión STORED).
3. Detecta automáticamente la carpeta de mods de ETS2 en Windows y puede
   instalar el archivo generado para probarlo de inmediato.
"""

import os
import sys
import zipfile
import re
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DIST_DIR = BASE_DIR / "dist"
OUTPUT_NAME = "Transporte_Austral_Chile.scs"

# Extensiones y archivos a incluir en el mod
INCLUDED_EXTENSIONS = {
    ".sii", ".sui", ".txt", ".png", ".jpg", ".dds", ".tobj",
    ".mat", ".pmd", ".pmg", ".pma", ".mbd", ".base", ".data", ".desc", ".aux", ".snd"
}

# Carpetas o archivos a ignorar durante el empaquetado
EXCLUDED_PATTERNS = {
    ".git", "__pycache__", "tools", "dist", ".vscode", ".idea", ".agents", "scratch", "backups", "temp", "tmp"
}


def sincronizar_mapa_desde_juego():
    """Detecta si el SCS Map Editor ha guardado chile.mbd en base/map/ y lo sincroniza."""
    posibles_bases = [
        Path(r"D:\SteamLibrary\steamapps\common\Euro Truck Simulator 2\base\map"),
        Path(r"C:\Program Files (x86)\Steam\steamapps\common\Euro Truck Simulator 2\base\map"),
        Path(r"E:\SteamLibrary\steamapps\common\Euro Truck Simulator 2\base\map"),
        Path.home() / "OneDrive" / "Documentos" / "Euro Truck Simulator 2" / "base" / "map",
        Path.home() / "Documents" / "Euro Truck Simulator 2" / "base" / "map",
    ]

    map_dest = BASE_DIR / "map"
    map_dest.mkdir(parents=True, exist_ok=True)

    for base_map in posibles_bases:
        mbd_file = base_map / "chile.mbd"
        if mbd_file.exists():
            import shutil
            shutil.copy2(mbd_file, map_dest / "chile.mbd")
            print(f"[SYNC] Archivo chile.mbd detectado y copiado desde: {base_map}")

            # Copiar sectores si existen
            sec_dir = base_map / "chile"
            if sec_dir.exists():
                dest_sec = map_dest / "chile"
                dest_sec.mkdir(parents=True, exist_ok=True)
                for f in sec_dir.glob("*.*"):
                    shutil.copy2(f, dest_sec / f.name)
                print(f"[SYNC] Sectores sincronizados en: {dest_sec}")
            break


def validar_mod():
    """Valida la integridad de los archivos del mod antes de empaquetar."""
    sincronizar_mapa_desde_juego()
    print("[1/3] Validando estructura e integridad del mod...")
    errores = []

    # Verificar presencia de chile.mbd para mapa standalone
    chile_mbd = BASE_DIR / "map" / "chile.mbd"
    if not chile_mbd.exists():
        print(" [AVISO MÓDULO STANDALONE] Aún no se ha generado 'map/chile.mbd'.")
        print("  -> Para habilitar 'chile.mbd' en el menú 'Módulo de mapa', guarda el mapa una vez en el editor con: save chile")
    else:
        print(" -> Módulo de mapa independiente 'chile.mbd' detectado: OK.")

    # Verificar manifest y description
    manifest = BASE_DIR / "manifest.sii"
    if not manifest.exists():
        errores.append("No se encontró manifest.sii en la raíz del proyecto.")

    desc = BASE_DIR / "description.txt"
    if not desc.exists():
        errores.append("No se encontró description.txt en la raíz del proyecto.")

    icon_png = BASE_DIR / "mod_icon.png"
    icon_jpg = BASE_DIR / "mod_icon.jpg"
    if not icon_png.exists() and not icon_jpg.exists():
        errores.append("No se encontró icono del mod (mod_icon.png o mod_icon.jpg).")

    # Verificar master SII files y sus includes (standalone puro)
    master_files = [
        BASE_DIR / "def" / "country.sii",
        BASE_DIR / "def" / "city.sii",
        BASE_DIR / "def" / "company.sii",
        BASE_DIR / "def" / "cargo.sii",
    ]

    include_regex = re.compile(r'@include\s+"([^"]+)"')

    for master in master_files:
        if not master.exists():
            errores.append(f"Falta archivo maestro: {master.relative_to(BASE_DIR)}")
            continue

        with open(master, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()

        for line in lines:
            match = include_regex.search(line)
            if match:
                rel_include = match.group(1)
                included_file = BASE_DIR / "def" / rel_include
                if not included_file.exists():
                    errores.append(f"Archivo incluido no encontrado: {rel_include} (referenciado en {master.name})")

    # Validar que los identificadores de cargas y sucursales no excedan el límite de 12 caracteres de SCS
    for c_file in (BASE_DIR / "def" / "cargo").glob("*.sui"):
        if len(c_file.stem) > 12:
            errores.append(f"El nombre de la carga '{c_file.stem}' supera los 12 caracteres máximos de SCS.")

    for comp_sii in (BASE_DIR / "def" / "company").glob("**/*.sii"):
        if comp_sii.parent.name in ("in", "out") and len(comp_sii.stem) > 12:
            errores.append(f"El archivo de carga '{comp_sii.relative_to(BASE_DIR)}' supera los 12 caracteres de SCS.")

    if errores:
        print("ERROR: Se encontraron problemas en el mod:")
        for err in errores:
            print(f"  - {err}")
        return False

    print(" -> Validación de definiciones e integridad: OK.")
    return True


def empaquetar_scs(output_path: Path):
    """Empaqueta el directorio del proyecto en un archivo .scs (ZIP sin compresión)."""
    print(f"[2/3] Empaquetando mod en: {output_path.name}...")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    archivos_empaquetados = 0
    packed_arcnames = set()

    with zipfile.ZipFile(output_path, "w", compression=zipfile.ZIP_STORED) as scs_zip:
        for root, dirs, files in os.walk(BASE_DIR):
            # Filtrar carpetas excluidas
            dirs[:] = [d for d in dirs if d not in EXCLUDED_PATTERNS and not d.startswith(".")]

            for file in files:
                file_path = Path(root) / file
                rel_path = file_path.relative_to(BASE_DIR)

                first_part = rel_path.parts[0]
                if first_part in EXCLUDED_PATTERNS:
                    continue

                if file.startswith(".") or file.endswith((".tmp", ".bak", ".swp", "~")):
                    continue

                if file_path.suffix.lower() in INCLUDED_EXTENSIONS or file in ["manifest.sii", "description.txt", "mod_icon.png", "mod_icon.jpg"]:
                    # Guardar con separador UNIX '/' requerido por el motor SCS
                    zip_arcname = rel_path.as_posix()
                    scs_zip.write(file_path, arcname=zip_arcname)
                    packed_arcnames.add(zip_arcname)
                    archivos_empaquetados += 1

        # Mapeo de empresas chilenas a sus empresas base para heredar catálogo masivo de cargas
        CHILEAN_TO_BASE = {
            "copec": "primel",
            "shell_cl": "pegi",
            "petrobras": "nada",
            "petrobras_cl": "nada",
            "aramco": "apus",
            "lider": "eurogoodies",
            "cencosud": "kaarfor",
            "unimarc": "sellplan",
            "falabella": "ika_bohag",
            "ripley": "ika_bohag",
            "sodimac": "sanbuilders",
            "arauco": "tree_et",
            "cmpc": "scs_paper",
            "codelco": "quarry",
            "escondida": "steinbr_str",
            "sqm": "wgcc",
            "enap": "itcc",
            "cap_acero": "kathode",
            "molymet": "ns_chem",
            "melon": "sanbuild_cem",
            "cbb_cemento": "sanbuild_bas",
            "polpaico": "batisse",
            "agrosuper": "euroacres",
            "colun": "trameri",
            "soprole": "fcp",
            "carozzi": "bcp",
            "iansa": "dfh",
            "ideal_cl": "fallow",
            "watts": "drekkar",
            "simunovic": "bhv",
            "dole_cl": "globe_eur",
            "aquachile": "polar_fish",
            "ccu": "stokes",
            "andina": "shuttle",
            "embonor": "nbfc",
            "concha_toro": "scout",
            "kunstmann": "stokes",
            "austral_pza": "polar",
            "starken": "lkwlog",
            "chilexpress": "posped",
            "correos_cl": "tradeaux",
            "bluex": "transinet",
            "tpa_arica": "cont_port",
            "sti_san_ant": "euroflow",
            "tps_valp": "cont_port",
            "pto_coronel": "cont_port_it",
            "tabsa": "marina",
        }

        # Empaquetar definiciones completas de in/ y out/ para empresas activas en Chile
        # desde scratch/def/def/company/ para garantizar ofertas de trabajo sin inflar Git
        scratch_comp_dir = BASE_DIR / "scratch" / "def" / "def" / "company"
        def_comp_dir = BASE_DIR / "def" / "company"
        if scratch_comp_dir.exists() and def_comp_dir.exists():
            for comp_folder in def_comp_dir.iterdir():
                if not comp_folder.is_dir():
                    continue
                ed_dir = comp_folder / "editor"
                if not ed_dir.exists() or not list(ed_dir.glob("*.sii")):
                    continue

                src_comp = scratch_comp_dir / comp_folder.name
                if not src_comp.exists() and comp_folder.name in CHILEAN_TO_BASE:
                    src_comp = scratch_comp_dir / CHILEAN_TO_BASE[comp_folder.name]

                if not src_comp.exists():
                    continue

                # Incluir archivo .sui de la empresa si falta
                sui_file = src_comp / f"{src_comp.name}.sui"
                arc_sui = f"def/company/{comp_folder.name}.sui"
                if arc_sui not in packed_arcnames and sui_file.exists():
                    scs_zip.write(sui_file, arcname=arc_sui)
                    packed_arcnames.add(arc_sui)
                    archivos_empaquetados += 1

                # Incluir todos los archivos in/ y out/ de cargas
                for subfolder in ["in", "out"]:
                    sub_src = src_comp / subfolder
                    if sub_src.exists():
                        for sii_file in sub_src.glob("*.sii"):
                            if len(sii_file.stem) > 12:
                                continue
                            arc = f"def/company/{comp_folder.name}/{subfolder}/{sii_file.name}"
                            if arc not in packed_arcnames:
                                scs_zip.write(sii_file, arcname=arc)
                                packed_arcnames.add(arc)
                                archivos_empaquetados += 1

    size_mb = output_path.stat().st_size / (1024 * 1024)
    print(f" -> Empaquetado completado: {archivos_empaquetados} archivos | Tamaño: {size_mb:.2f} MB")
    return True


def instalar_en_ets2(scs_path: Path):
    """Copia el .scs directamente a la carpeta mod de ETS2 si existe."""
    print("[3/3] Buscando directorio de mods de Euro Truck Simulator 2...")

    posibles_rutas = [
        Path.home() / "OneDrive" / "Documentos" / "Euro Truck Simulator 2" / "mod",
        Path.home() / "OneDrive" / "Documents" / "Euro Truck Simulator 2" / "mod",
        Path.home() / "Documents" / "Euro Truck Simulator 2" / "mod",
        Path.home() / "Documentos" / "Euro Truck Simulator 2" / "mod",
        Path(os.environ.get("USERPROFILE", "")) / "OneDrive" / "Documentos" / "Euro Truck Simulator 2" / "mod",
        Path(os.environ.get("USERPROFILE", "")) / "Documents" / "Euro Truck Simulator 2" / "mod",
        Path(os.environ.get("USERPROFILE", "")) / "Documentos" / "Euro Truck Simulator 2" / "mod",
    ]

    target_mod_dir = None
    for ruta in posibles_rutas:
        if ruta.parent.exists():
            target_mod_dir = ruta
            break

    if target_mod_dir:
        target_mod_dir.mkdir(parents=True, exist_ok=True)
        dest = target_mod_dir / scs_path.name
        import shutil
        shutil.copy2(scs_path, dest)
        print(f" -> Mod copiado con éxito a tu carpeta de ETS2:")
        print(f"    {dest}")
    else:
        print(" -> No se detectó la carpeta ETS2 en Documentos por defecto.")
        print(f"    Puedes copiar manualmente '{scs_path}' a:")
        print("    C:\\Users\\<TuUsuario>\\Documents\\Euro Truck Simulator 2\\mod\\")


def main():
    print("=" * 70)
    print(" TRANSPORTE AUSTRAL - COMPILADOR Y GENERADOR DE ARCHIVO .SCS")
    print("===============================================================")

    if not validar_mod():
        sys.exit(1)

    dist_scs = DIST_DIR / OUTPUT_NAME
    if not empaquetar_scs(dist_scs):
        sys.exit(1)

    instalar_en_ets2(dist_scs)

    print("=" * 70)
    print(" ¡PROCESO FINALIZADO CON ÉXITO!")
    print(" Mod listo para activar en el Gestor de Modificaciones de ETS2.")
    print("=" * 70)


if __name__ == "__main__":
    main()
