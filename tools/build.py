#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# TRANSPORTE AUSTRAL - Compilador de dos paquetes SCS

import os, sys, zipfile, re, shutil
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DIST_DIR = BASE_DIR / "dist"

OUTPUT_BASE   = "RutaChile_Base.scs"
OUTPUT_ASSETS = "RutaChile_Assets.scs"
LEGACY_SCS    = "Transporte_Austral_Chile.scs"

INCLUDED_EXTENSIONS = {
    ".sii", ".sui", ".txt", ".png", ".jpg", ".dds", ".tobj",
    ".mat", ".pmd", ".pmg", ".pma", ".mbd",
    ".base", ".data", ".desc", ".aux", ".layer", ".snd"
}
BASE_FOLDERS   = {"map", "def", "locale"}
ASSETS_FOLDERS = {"material", "model", "model2", "prefab", "prefab2"}
EXCLUDED_PATTERNS = {
    ".git", "__pycache__", "tools", "dist",
    ".vscode", ".idea", ".agents", "scratch", "backups", "temp", "tmp"
}

MANIFEST_BASE = """SiiNunit
{
mod_package : _nameless
{
 package_version: "1.0.0"
 display_name: "RutaChile Base"
 author: "Transporte Austral"
 description_file: "description.txt"
 icon: "mod_icon.jpg"
 category[]: "map"
 compatible_versions[]: "1.49.*"
 compatible_versions[]: "1.50.*"
 compatible_versions[]: "1.51.*"
 compatible_versions[]: "1.52.*"
 compatible_versions[]: "1.53.*"
 compatible_versions[]: "1.54.*"
 compatible_versions[]: "1.55.*"
 compatible_versions[]: "1.56.*"
 compatible_versions[]: "1.57.*"
 compatible_versions[]: "1.58.*"
 compatible_versions[]: "1.59.*"
 compatible_versions[]: "1.60.*"
 compatible_versions[]: "1.61.*"
}
}
"""

MANIFEST_ASSETS = """SiiNunit
{
mod_package : _nameless
{
 package_version: "1.0.0"
 display_name: "RutaChile Assets"
 author: "Transporte Austral"
 description_file: "description.txt"
 icon: "mod_icon.jpg"
 category[]: "map"
 compatible_versions[]: "1.49.*"
 compatible_versions[]: "1.50.*"
 compatible_versions[]: "1.51.*"
 compatible_versions[]: "1.52.*"
 compatible_versions[]: "1.53.*"
 compatible_versions[]: "1.54.*"
 compatible_versions[]: "1.55.*"
 compatible_versions[]: "1.56.*"
 compatible_versions[]: "1.57.*"
 compatible_versions[]: "1.58.*"
 compatible_versions[]: "1.59.*"
 compatible_versions[]: "1.60.*"
 compatible_versions[]: "1.61.*"
}
}
"""

DESCRIPTION_BASE = (
    "RutaChile Base - Estructura del mapa chileno para ETS2.\n"
    "Contiene el mapa, definiciones de ciudades, empresas, paises,\n"
    "cargamentos y ficheros de localizacion.\n"
    "Activa DESPUES de RutaChile Assets en el gestor de mods.\n"
)

DESCRIPTION_ASSETS = (
    "RutaChile Assets - Recursos graficos del mapa chileno para ETS2.\n"
    "Contiene modelos, materiales, texturas, prefabs y escudos MOP.\n"
    "Activa ANTES de RutaChile Base en el gestor de mods (prioridad alta).\n"
)

CHILEAN_TO_BASE = {
    "copec": "primel", "shell_cl": "pegi", "petrobras": "nada",
    "petrobras_cl": "nada", "aramco": "apus", "lider": "eurogoodies",
    "cencosud": "kaarfor", "unimarc": "sellplan", "falabella": "ika_bohag",
    "ripley": "ika_bohag", "sodimac": "sanbuilders", "arauco": "tree_et",
    "cmpc": "scs_paper", "codelco": "quarry", "escondida": "steinbr_str",
    "sqm": "wgcc", "enap": "itcc", "cap_acero": "kathode",
    "molymet": "ns_chem", "melon": "sanbuild_cem", "cbb_cemento": "sanbuild_bas",
    "polpaico": "batisse", "agrosuper": "euroacres", "colun": "trameri",
    "soprole": "fcp", "carozzi": "bcp", "iansa": "dfh",
    "ideal_cl": "fallow", "watts": "drekkar", "simunovic": "bhv",
    "dole_cl": "globe_eur", "aquachile": "polar_fish", "ccu": "stokes",
    "andina": "shuttle", "embonor": "nbfc", "concha_toro": "scout",
    "kunstmann": "stokes", "austral_pza": "polar", "starken": "lkwlog",
    "chilexpress": "posped", "correos_cl": "tradeaux", "bluex": "transinet",
    "tpa_arica": "cont_port", "sti_san_ant": "euroflow", "tps_valp": "cont_port",
    "pto_coronel": "cont_port_it", "tabsa": "marina",
}


def sincronizar_mapa_desde_juego():
    posibles = [
        Path(r"D:\SteamLibrary\steamapps\common\Euro Truck Simulator 2\base\map"),
        Path(r"C:\Program Files (x86)\Steam\steamapps\common\Euro Truck Simulator 2\base\map"),
        Path(r"E:\SteamLibrary\steamapps\common\Euro Truck Simulator 2\base\map"),
        Path.home() / "OneDrive" / "Documentos" / "Euro Truck Simulator 2" / "base" / "map",
        Path.home() / "Documents" / "Euro Truck Simulator 2" / "base" / "map",
    ]
    dst = BASE_DIR / "map"
    dst.mkdir(parents=True, exist_ok=True)
    for bp in posibles:
        mbd = bp / "chile.mbd"
        if mbd.exists():
            shutil.copy2(mbd, dst / "chile.mbd")
            print(f"[SYNC] chile.mbd desde {bp}")
            sd = bp / "chile"
            if sd.exists():
                dd = dst / "chile"
                dd.mkdir(parents=True, exist_ok=True)
                for f in sd.glob("*.*"):
                    shutil.copy2(f, dd / f.name)
            break


def validar_mod():
    sincronizar_mapa_desde_juego()
    print("[1/4] Validando...")
    errores = []
    if not (BASE_DIR / "map" / "chile.mbd").exists():
        print("  [AVISO] chile.mbd no encontrado")
    else:
        print("  -> chile.mbd OK")
    rx = re.compile(r'@include\s+"([^"]+)"')
    for rel in ["def/country.sii","def/city.sii","def/company.sii","def/cargo.sii","def/ferry.sii"]:
        p = BASE_DIR / rel
        if not p.exists():
            errores.append(f"Falta: {rel}")
            continue
        for line in p.read_text(encoding="utf-8", errors="ignore").splitlines():
            m = rx.search(line)
            if m:
                inc = BASE_DIR / "def" / m.group(1)
                if not inc.exists():
                    errores.append(f"Include faltante: {m.group(1)}")
    if errores:
        [print(f"  ERR: {e}") for e in errores]
        return False
    print("  -> OK")
    return True


def _walk_folders(zf, folders, packed):
    count = 0
    for fn in folders:
        d = BASE_DIR / fn
        if not d.exists():
            continue
        for root, dirs, files in os.walk(d):
            dirs[:] = [x for x in dirs if x not in EXCLUDED_PATTERNS and not x.startswith(".")]
            for file in files:
                fp = Path(root) / file
                if file.startswith(".") or file.endswith((".tmp",".bak",".swp","~")):
                    continue
                if fp.suffix.lower() in INCLUDED_EXTENSIONS:
                    arc = fp.relative_to(BASE_DIR).as_posix()
                    if arc not in packed:
                        zf.write(fp, arcname=arc)
                        packed.add(arc)
                        count += 1
    return count


def empaquetar_base(op):
    print(f"[2/4] Empaquetando {op.name}...")
    op.parent.mkdir(parents=True, exist_ok=True)
    packed = set()
    n = 0
    with zipfile.ZipFile(op, "w", compression=zipfile.ZIP_STORED) as zf:
        zf.writestr("manifest.sii", MANIFEST_BASE)
        zf.writestr("description.txt", DESCRIPTION_BASE)
        packed.update(["manifest.sii","description.txt"])
        n += 2
        for ico in ["mod_icon.jpg","mod_icon.png"]:
            p = BASE_DIR / ico
            if p.exists():
                zf.write(p, arcname=ico); packed.add(ico); n += 1; break
        n += _walk_folders(zf, BASE_FOLDERS, packed)
        sc = BASE_DIR / "scratch" / "def" / "def" / "company"
        dc = BASE_DIR / "def" / "company"
        if sc.exists() and dc.exists():
            for cf in dc.iterdir():
                if not cf.is_dir(): continue
                ed = cf / "editor"
                if not ed.exists() or not list(ed.glob("*.sii")): continue
                src = sc / cf.name
                if not src.exists() and cf.name in CHILEAN_TO_BASE:
                    src = sc / CHILEAN_TO_BASE[cf.name]
                if not src.exists(): continue
                sui = src / f"{src.name}.sui"
                a_sui = f"def/company/{cf.name}.sui"
                if a_sui not in packed and sui.exists():
                    zf.write(sui, arcname=a_sui); packed.add(a_sui); n += 1
                for sub in ["in","out"]:
                    ss = src / sub
                    if ss.exists():
                        for sf in ss.glob("*.sii"):
                            if len(sf.stem) > 12: continue
                            arc = f"def/company/{cf.name}/{sub}/{sf.name}"
                            if arc not in packed:
                                zf.write(sf, arcname=arc); packed.add(arc); n += 1
    mb = op.stat().st_size / 1048576
    print(f"  -> {n} archivos | {mb:.2f} MB")
    return True


def empaquetar_assets(op):
    print(f"[3/4] Empaquetando {op.name}...")
    op.parent.mkdir(parents=True, exist_ok=True)
    packed = set()
    n = 0
    with zipfile.ZipFile(op, "w", compression=zipfile.ZIP_STORED) as zf:
        zf.writestr("manifest.sii", MANIFEST_ASSETS)
        zf.writestr("description.txt", DESCRIPTION_ASSETS)
        packed.update(["manifest.sii","description.txt"])
        n += 2
        for ico in ["mod_icon.jpg","mod_icon.png"]:
            p = BASE_DIR / ico
            if p.exists():
                zf.write(p, arcname=ico); packed.add(ico); n += 1; break
        n += _walk_folders(zf, ASSETS_FOLDERS, packed)
    mb = op.stat().st_size / 1048576
    print(f"  -> {n} archivos | {mb:.2f} MB")
    return True


def instalar_en_ets2(scs_list):
    print("[4/4] Instalando...")
    rutas = [
        Path.home() / "OneDrive" / "Documentos" / "Euro Truck Simulator 2" / "mod",
        Path.home() / "OneDrive" / "Documents"  / "Euro Truck Simulator 2" / "mod",
        Path.home() / "Documents"  / "Euro Truck Simulator 2" / "mod",
        Path.home() / "Documentos" / "Euro Truck Simulator 2" / "mod",
        Path(os.environ.get("USERPROFILE","")) / "OneDrive" / "Documentos" / "Euro Truck Simulator 2" / "mod",
        Path(os.environ.get("USERPROFILE","")) / "Documents"  / "Euro Truck Simulator 2" / "mod",
        Path(os.environ.get("USERPROFILE","")) / "Documentos" / "Euro Truck Simulator 2" / "mod",
    ]
    md = None
    for r in rutas:
        if r.parent.exists():
            md = r; break
    if not md:
        print("  [AVISO] Carpeta de mods ETS2 no encontrada")
        return
    md.mkdir(parents=True, exist_ok=True)
    leg = md / LEGACY_SCS
    if leg.exists():
        leg.unlink()
        print(f"  -> Eliminado: {LEGACY_SCS}")
    for sp in scs_list:
        dst = md / sp.name
        shutil.copy2(sp, dst)
        print(f"  -> {sp.name} => {dst}")
    cfg = md.parent / "config.cfg"
    if cfg.exists():
        try:
            t = cfg.read_text(encoding="utf-8", errors="ignore")
            if 'uset g_force_economy_reset "' in t:
                t = re.sub(r'uset g_force_economy_reset "[01]"', 'uset g_force_economy_reset "1"', t)
            else:
                t += '\nuset g_force_economy_reset "1"\n'
            cfg.write_text(t, encoding="utf-8")
            print("  -> config.cfg: economy_reset=1 OK")
        except Exception as e:
            print(f"  [AVISO] config.cfg: {e}")
    print()
    print("  +---------------------------------------------------------+")
    print("  |   ORDEN DE ACTIVACION EN EL GESTOR DE MODS DE ETS2     |")
    print("  +---------------------------------------------------------+")
    print("  |  1. RutaChile_Assets  <- ARRIBA  (prioridad alta)      |")
    print("  |  2. RutaChile_Base    <- ABAJO   (prioridad base)      |")
    print("  +---------------------------------------------------------+")


def main():
    print("=" * 65)
    print("  RUTA CHILE - COMPILADOR DE DOS PAQUETES SCS PARA ETS2")
    print("=" * 65)
    if not validar_mod():
        sys.exit(1)
    b = DIST_DIR / OUTPUT_BASE
    a = DIST_DIR / OUTPUT_ASSETS
    if not empaquetar_base(b): sys.exit(1)
    if not empaquetar_assets(a): sys.exit(1)
    instalar_en_ets2([a, b])
    print()
    print("=" * 65)
    print("  COMPILACION FINALIZADA!")
    print(f"  Base:   {b}")
    print(f"  Assets: {a}")
    print("=" * 65)


if __name__ == "__main__":
    main()
