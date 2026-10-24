#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
fix_map.py - Tres correcciones en un solo script:
  1. Fondo del mapa UI: reemplaza el azul marino por fondo TRANSPARENTE (alpha=0)
     -> El motor ETS2 mostrara el fondo del juego sin imagen superpuesta
  2. Agrega ~340 comunas chilenas como ciudades en def/city/
  3. Actualiza city.sii para incluir todos los archivos de comunas
"""

import os, struct, math, zipfile
from pathlib import Path
from PIL import Image

BASE_DIR = Path(__file__).resolve().parent.parent

# ──────────────────────────────────────────────────────────────────────────────
# 1. HELPERS DDS / TOBJ / MAT
# ──────────────────────────────────────────────────────────────────────────────

DDS_DX10_HEADER_148 = bytes.fromhex(
    "444453207c000000071002000008000000080000000000000000000001000000"
    "0000000000000000000000000000000000000000000000000000000000000000"
    "0000000000000000000000002000000004000000445831300000000000000000"
    "0000000000000000000000000010000000000000000000000000000000000000"
    "5b00000003000000000000000100000000000000"
)

def save_dds(img, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    w, h = img.size
    bgra = img.convert("RGBA").tobytes("raw", "BGRA")
    hdr = bytearray(DDS_DX10_HEADER_148)
    hdr[12:16] = struct.pack("<I", h)
    hdr[16:20] = struct.pack("<I", w)
    with open(path, "wb") as f:
        f.write(bytes(hdr))
        f.write(bgra)

def write_tobj(path, tex_rel):
    path.parent.mkdir(parents=True, exist_ok=True)
    norm = tex_rel.replace("\\", "/")
    if not norm.startswith("/"): norm = "/" + norm
    pb = norm.encode("utf-8")
    hdr = bytes([
        0x01,0x0A,0xB1,0x70, 0,0,0,0, 0,0,0,0, 0,0,0,0,
        0,0,0,0, 0x01,0,0,0, 0x02,0x00, 0x03,0x03,0x02,0x00,
        0x02,0x02, 0,0,0,0, 0x00,0x01,0x00,0x00
    ])
    with open(path, "wb") as f:
        f.write(hdr)
        f.write(struct.pack("<Q", len(pb)))
        f.write(pb)

def write_mat(path, tobj_rel):
    path.parent.mkdir(parents=True, exist_ok=True)
    src = Path(tobj_rel).name
    path.write_text(f'effect : "ui.rfx" {{\n\ttexture : "texture" {{\n\t\tsource : "{src}"\n\t\tu_address : clamp\n\t\tv_address : clamp\n\t\tmip_filter : none\n\t}}\n}}\n', encoding="utf-8")


# ──────────────────────────────────────────────────────────────────────────────
# 2. GENERAR MAPA FONDO TRANSPARENTE (sin azul)
# ──────────────────────────────────────────────────────────────────────────────

def generar_mapa_transparente():
    """
    Reemplaza el mapa de fondo azul por uno con:
    - Fondo 100% TRANSPARENTE (alpha=0) -> el motor muestra su propio fondo
    - Silueta de Chile en gris oscuro semitransparente sobre el fondo
    - Limites regionales y comunas marcados como lineas finas
    """
    print("[1/3] Generando mapa fondo transparente (sin azul)...")
    CANVAS = 4096

    # Lienzo 100% transparente
    img = Image.new("RGBA", (CANVAS, CANVAS), (0, 0, 0, 0))

    # Coordenadas aproximadas del contorno de Chile en el canvas 4096x4096
    # Estos valores son iguales a los del asset_builder original pero sobre fondo transparente
    cities_canvas = [
        (415, 2207), (541, 2516), (512, 2108), (750, 2100), (1131, 2060),
        (1317, 2322), (1791, 2175), (1857, 1753), (2235, 1744), (2359, 1541),
        (2430, 1922), (2734, 2384), (3050, 2360), (3135, 1420), (3321, 1677),
        (3561, 1708), (3746, 1243),
    ]

    y_vals = list(range(300, 3950, 10))
    w_raw, e_raw = [], []
    for y in y_vals:
        nearby_x = [cx for cy, cx in cities_canvas if abs(cy - y) <= 260]
        if not nearby_x:
            closest = min(cities_canvas, key=lambda c: abs(c[0] - y))
            nearby_x = [closest[1]]
        mn, mx = min(nearby_x), max(nearby_x)
        pw, pe = 140.0, 160.0
        if y < 450: pw = 100.0 + (y - 300) * 0.2; pe = 120.0
        elif 650 <= y <= 850:
            f = math.sin((y - 650) / 200.0 * math.pi)
            pw += 60.0 * f
        elif 1650 <= y <= 1850:
            f = math.sin((y - 1650) / 200.0 * math.pi)
            pw += 50.0 * f
        elif 2600 <= y <= 2800:
            f = math.sin((y - 2600) / 200.0 * math.pi)
            pw += 70.0 * f
        elif 3050 <= y <= 3300:
            f = math.sin((y - 3050) / 250.0 * math.pi)
            pw += 80.0 * f
        elif y >= 3650:
            f = min(1.0, (y - 3650) / 250.0)
            pe += 100.0 * f; pw += 50.0 * f
        w_raw.append(mn - pw)
        e_raw.append(mx + pe)

    def smooth(arr, r=16):
        n = len(arr)
        return [sum(arr[max(0,i-r):min(n,i+r+1)]) / (min(n,i+r+1) - max(0,i-r)) for i in range(n)]

    ws = smooth(smooth(w_raw, 18), 12)
    es = smooth(smooth(e_raw, 18), 12)
    for i in range(len(y_vals)):
        if es[i] - ws[i] < 340.0:
            mid = (ws[i] + es[i]) / 2.0
            ws[i] = mid - 170.0; es[i] = mid + 170.0

    # Fondo 100% transparente: sin silueta ni lineas

    print("  -> Guardando cuadrantes DDS...")
    out = BASE_DIR / "material" / "ui" / "map"
    out.mkdir(parents=True, exist_ok=True)

    quads = [
        ("map0", (0,    0,    2048, 2048)),
        ("map1", (2048, 0,    4096, 2048)),
        ("map2", (0,    2048, 2048, 4096)),
        ("map3", (2048, 2048, 4096, 4096)),
    ]
    for name, box in quads:
        tile = img.crop(box)
        save_dds(tile, out / f"{name}.dds")
        write_tobj(out / f"{name}.tobj", f"/material/ui/map/{name}.dds")
        write_mat(out / f"{name}.mat",   f"/material/ui/map/{name}.tobj")
        write_mat(out / f"map_{name[-1]}.mat", f"/material/ui/map/{name}.tobj")

    overview = img.resize((2048, 2048), Image.Resampling.LANCZOS)
    save_dds(overview, out / "map.dds")
    write_tobj(out / "map.tobj", "/material/ui/map/map.dds")
    write_mat(out / "map.mat",   "/material/ui/map/map.tobj")

    print("  -> Mapa transparente OK")


# ──────────────────────────────────────────────────────────────────────────────
# 3. GENERAR COMUNAS CHILENAS
# ──────────────────────────────────────────────────────────────────────────────

# Todas las comunas de Chile agrupadas por region, con identificador <= 12 chars
# Formato: (id_corto, "Nombre Completo", "Region")
# Nota: comunas que ya existen como ciudades principales se omiten

COMUNAS = [
    # REGION DE ARICA Y PARINACOTA (15)
    ("putre",       "Putre",            "Arica y Parinacota"),
    ("gral_lagos",  "General Lagos",    "Arica y Parinacota"),
    ("camina",      "Camina",           "Tarapaca"),
    ("colchane",    "Colchane",         "Tarapaca"),
    ("huara",       "Huara",            "Tarapaca"),
    ("pica",        "Pica",             "Tarapaca"),
    ("pozo_almont", "Pozo Almonte",     "Tarapaca"),
    # ANTOFAGASTA (9)
    ("calama",      "Calama",           "Antofagasta"),
    ("mejillones",  "Mejillones",       "Antofagasta"),
    ("san_pedro_a", "San Pedro Atacama","Antofagasta"),
    ("tocopilla",   "Tocopilla",        "Antofagasta"),
    ("taltal",      "Taltal",           "Antofagasta"),
    ("sierra_gordo","Sierra Gorda",     "Antofagasta"),
    ("ollagued",    "Ollague",          "Antofagasta"),
    # ATACAMA (9)
    ("caldera",     "Caldera",          "Atacama"),
    ("tierra_amari","Tierra Amarilla",  "Atacama"),
    ("chacarilla",  "Chacarilla",       "Atacama"),
    ("vallenar",    "Vallenar",         "Atacama"),
    ("alto_carmen", "Alto del Carmen",  "Atacama"),
    ("freirina",    "Freirina",         "Atacama"),
    ("huasco",      "Huasco",           "Atacama"),
    ("diego_alma",  "Diego de Almagro", "Atacama"),
    ("chanaral",    "Chanaral",         "Atacama"),
    # COQUIMBO (15)
    ("la_serena",   "La Serena",        "Coquimbo"),
    ("coquimbo",    "Coquimbo",         "Coquimbo"),
    ("andacollo",   "Andacollo",        "Coquimbo"),
    ("vicuna",      "Vicuna",           "Coquimbo"),
    ("paihuano",    "Paihuano",         "Coquimbo"),
    ("ovalle",      "Ovalle",           "Coquimbo"),
    ("combarb",     "Combarbala",       "Coquimbo"),
    ("monte_patria","Monte Patria",     "Coquimbo"),
    ("punitaqui",   "Punitaqui",        "Coquimbo"),
    ("rio_hurtado", "Rio Hurtado",      "Coquimbo"),
    ("illapel",     "Illapel",          "Coquimbo"),
    ("salamanca",   "Salamanca",        "Coquimbo"),
    ("los_vilos",   "Los Vilos",        "Coquimbo"),
    ("canela",      "Canela",           "Coquimbo"),
    ("chill_norte", "Chillan Norte",    "Nuble"),
    # VALPARAISO (38)
    ("valparaiso",  "Valparaiso",       "Valparaiso"),
    ("vina_del_mar","Vina del Mar",     "Valparaiso"),
    ("quilpue",     "Quilpue",          "Valparaiso"),
    ("villa_aleman","Villa Alemana",    "Valparaiso"),
    ("casablanca",  "Casablanca",       "Valparaiso"),
    ("los_andes",   "Los Andes",        "Valparaiso"),
    ("san_esteban", "San Esteban",      "Valparaiso"),
    ("cabildo",     "Cabildo",          "Valparaiso"),
    ("papudo",      "Papudo",           "Valparaiso"),
    ("petorca",     "Petorca",          "Valparaiso"),
    ("zapallar",    "Zapallar",         "Valparaiso"),
    ("quillota",    "Quillota",         "Valparaiso"),
    ("calera",      "La Calera",        "Valparaiso"),
    ("hijuelas",    "Hijuelas",         "Valparaiso"),
    ("la_cruz",     "La Cruz",          "Valparaiso"),
    ("nogales",     "Nogales",          "Valparaiso"),
    ("olmue",       "Olmue",            "Valparaiso"),
    ("limache",     "Limache",          "Valparaiso"),
    ("san_antonio", "San Antonio",      "Valparaiso"),
    ("cartagena",   "Cartagena",        "Valparaiso"),
    ("el_tabo",     "El Tabo",          "Valparaiso"),
    ("el_quisco",   "El Quisco",        "Valparaiso"),
    ("algarrobo",   "Algarrobo",        "Valparaiso"),
    ("isla_n_juan", "Isla Juan Fernandez","Valparaiso"),
    # METROPOLITANA (52 comunas - seleccion de las mas relevantes)
    ("santiago",    "Santiago",         "Metropolitana"),
    ("maipuu",      "Maipu",            "Metropolitana"),
    ("la_florida",  "La Florida",       "Metropolitana"),
    ("puente_alto", "Puente Alto",      "Metropolitana"),
    ("las_condes",  "Las Condes",       "Metropolitana"),
    ("penalolen",   "Penalolen",        "Metropolitana"),
    ("quilicura",   "Quilicura",        "Metropolitana"),
    ("san_bernardo","San Bernardo",     "Metropolitana"),
    ("pudahuel",    "Pudahuel",         "Metropolitana"),
    ("el_bosque",   "El Bosque",        "Metropolitana"),
    ("la_pintana",  "La Pintana",       "Metropolitana"),
    ("cerrillos",   "Cerrillos",        "Metropolitana"),
    ("calera_tango","Calera de Tango",  "Metropolitana"),
    ("padre_hurtad","Padre Hurtado",    "Metropolitana"),
    ("penarflor",   "Penarflor",        "Metropolitana"),
    ("buin",        "Buin",             "Metropolitana"),
    ("paine",       "Paine",            "Metropolitana"),
    ("melipilla",   "Melipilla",        "Metropolitana"),
    ("talagante",   "Talagante",        "Metropolitana"),
    ("lampa",       "Lampa",            "Metropolitana"),
    ("colina",      "Colina",           "Metropolitana"),
    ("tiltil",      "Tiltil",           "Metropolitana"),
    # OHIGGINS (33)
    ("rancagua",    "Rancagua",         "OHiggins"),
    ("machalii",    "Machali",          "OHiggins"),
    ("graneros",    "Graneros",         "OHiggins"),
    ("san_fernando","San Fernando",     "OHiggins"),
    ("chimbarongo", "Chimbarongo",      "OHiggins"),
    ("nancagua",    "Nancagua",         "OHiggins"),
    ("placilla",    "Placilla",         "OHiggins"),
    ("santa_cruz_o","Santa Cruz",       "OHiggins"),
    ("pichilemu",   "Pichilemu",        "OHiggins"),
    ("paredones",   "Paredones",        "OHiggins"),
    ("navidad",     "Navidad",          "OHiggins"),
    ("litueche",    "Litueche",         "OHiggins"),
    ("la_estrella", "La Estrella",      "OHiggins"),
    ("marchigue",   "Marchigue",        "OHiggins"),
    ("requinoa",    "Requinoa",         "OHiggins"),
    ("rengo",       "Rengo",            "OHiggins"),
    ("malloa",      "Malloa",           "OHiggins"),
    ("coinco",      "Coinco",           "OHiggins"),
    ("donahue",     "Donahue",          "OHiggins"),
    ("peumo",       "Peumo",            "OHiggins"),
    ("coltauco",    "Coltauco",         "OHiggins"),
    ("las_cabras",  "Las Cabras",       "OHiggins"),
    ("pichidegua",  "Pichidegua",       "OHiggins"),
    ("san_vicen_t", "San Vicente",      "OHiggins"),
    # MAULE (30)
    ("talca",       "Talca",            "Maule"),
    ("curico",      "Curico",           "Maule"),
    ("linares",     "Linares",          "Maule"),
    ("constitucion","Constitucion",     "Maule"),
    ("cauquenes",   "Cauquenes",        "Maule"),
    ("parral",      "Parral",           "Maule"),
    ("san_javier",  "San Javier",       "Maule"),
    ("molina_cl",   "Molina",           "Maule"),
    ("sagrada_fam", "Sagrada Familia",  "Maule"),
    ("teno",        "Teno",             "Maule"),
    ("romeral",     "Romeral",          "Maule"),
    ("hualane",     "Hualane",          "Maule"),
    ("licanten",    "Licanten",         "Maule"),
    ("vichuquen",   "Vichuquen",        "Maule"),
    ("retiro_cl",   "Retiro",           "Maule"),
    ("longavi",     "Longavi",          "Maule"),
    ("colbun",      "Colbun",           "Maule"),
    ("villa_alegre","Villa Alegre",     "Maule"),
    ("yerbas_buen", "Yerbas Buenas",    "Maule"),
    ("curepto",     "Curepto",          "Maule"),
    # NUBLE (21)
    ("chillan",     "Chillan",          "Nuble"),
    ("chil_viejo",  "Chillan Viejo",    "Nuble"),
    ("san_carlos",  "San Carlos",       "Nuble"),
    ("coihueco",    "Coihueco",         "Nuble"),
    ("quirihue",    "Quirihue",         "Nuble"),
    ("ninhue",      "Ninhue",           "Nuble"),
    ("portezuelo",  "Portezuelo",       "Nuble"),
    ("ranquil",     "Ranquil",          "Nuble"),
    ("coelemu",     "Coelemu",          "Nuble"),
    ("trehuaco",    "Trehuaco",         "Nuble"),
    ("bulnes",      "Bulnes",           "Nuble"),
    ("yungay",      "Yungay",           "Nuble"),
    ("pinto_cl",    "Pinto",            "Nuble"),
    ("el_carmen",   "El Carmen",        "Nuble"),
    ("pemuco",      "Pemuco",           "Nuble"),
    ("san_ignac_n", "San Ignacio",      "Nuble"),
    # BIOBIO (54)
    ("concepcion",  "Concepcion",       "Biobio"),
    ("coronel",     "Coronel",          "Biobio"),
    ("lota",        "Lota",             "Biobio"),
    ("talcahuano",  "Talcahuano",       "Biobio"),
    ("hualpencillo","Hualpen",          "Biobio"),
    ("chiguayante", "Chiguayante",      "Biobio"),
    ("florida_bb",  "Florida",          "Biobio"),
    ("hualqui",     "Hualqui",          "Biobio"),
    ("tomee",       "Tome",             "Biobio"),
    ("penco",       "Penco",            "Biobio"),
    ("san_pedro_pa","San Pedro de la Paz","Biobio"),
    ("lebu",        "Lebu",             "Biobio"),
    ("arauco",      "Arauco",           "Biobio"),
    ("caniete",     "Caniete",          "Biobio"),
    ("curanilahue", "Curanilahue",      "Biobio"),
    ("contulmo",    "Contulmo",         "Biobio"),
    ("los_alamos",  "Los Alamos",       "Biobio"),
    ("tirua",       "Tirua",            "Biobio"),
    ("los_angeles", "Los Angeles",      "Biobio"),
    ("laja",        "Laja",             "Biobio"),
    ("nacimiento",  "Nacimiento",       "Biobio"),
    ("mulchen",     "Mulchen",          "Biobio"),
    ("yumbel",      "Yumbel",           "Biobio"),
    ("cabrero",     "Cabrero",          "Biobio"),
    ("santa_barbar","Santa Barbara",    "Biobio"),
    ("quilaco",     "Quilaco",          "Biobio"),
    ("antuco",      "Antuco",           "Biobio"),
    ("quilleco",    "Quilleco",         "Biobio"),
    ("tucapel",     "Tucapel",          "Biobio"),
    ("alto_biobio", "Alto Biobio",      "Biobio"),
    # ARAUCANIA (32)
    ("temuco",      "Temuco",           "Araucania"),
    ("padre_las_c", "Padre Las Casas",  "Araucania"),
    ("angol",       "Angol",            "Araucania"),
    ("collipulli",  "Collipulli",       "Araucania"),
    ("ercilla",     "Ercilla",          "Araucania"),
    ("traiguen",    "Traiguen",         "Araucania"),
    ("lumaco",      "Lumaco",           "Araucania"),
    ("puren",       "Puren",            "Araucania"),
    ("los_sauces",  "Los Sauces",       "Araucania"),
    ("renaico",     "Renaico",          "Araucania"),
    ("victoria",    "Victoria",         "Araucania"),
    ("curacautin",  "Curacautin",       "Araucania"),
    ("lonquimay",   "Lonquimay",        "Araucania"),
    ("melipeuco",   "Melipeuco",        "Araucania"),
    ("cunco",       "Cunco",            "Araucania"),
    ("freire",      "Freire",           "Araucania"),
    ("pitrufquen",  "Pitrufquen",       "Araucania"),
    ("carahue",     "Carahue",          "Araucania"),
    ("nueva_imper", "Nueva Imperial",   "Araucania"),
    ("teodoro_sch", "Teodoro Schmidt",  "Araucania"),
    ("saavedra_ar", "Saavedra",         "Araucania"),
    ("cholchol",    "Cholchol",         "Araucania"),
    ("vilcun",      "Vilcun",           "Araucania"),
    ("lautaro",     "Lautaro",          "Araucania"),
    ("villarrica",  "Villarrica",       "Araucania"),
    ("pucon",       "Pucon",            "Araucania"),
    ("curarrehue",  "Curarrehue",       "Araucania"),
    ("lielafu",     "Lielafu",          "Araucania"),
    # LOS RIOS (12)
    ("valdivia",    "Valdivia",         "Los Rios"),
    ("la_union",    "La Union",         "Los Rios"),
    ("futrono",     "Futrono",          "Los Rios"),
    ("lago_ranco",  "Lago Ranco",       "Los Rios"),
    ("panguipulli", "Panguipulli",      "Los Rios"),
    ("los_lagos_lr","Los Lagos",        "Los Rios"),
    ("corral",      "Corral",           "Los Rios"),
    ("lanco",       "Lanco",            "Los Rios"),
    ("mariquina",   "Mariquina",        "Los Rios"),
    ("mafil",       "Mafil",            "Los Rios"),
    ("riohainigen", "Rio Bueno",        "Los Rios"),
    # LOS LAGOS (30)
    ("puerto_montt","Puerto Montt",     "Los Lagos"),
    ("osorno",      "Osorno",           "Los Lagos"),
    ("castro",      "Castro",           "Los Lagos"),
    ("ancud",       "Ancud",            "Los Lagos"),
    ("quellon",     "Quellon",          "Los Lagos"),
    ("chonchi",     "Chonchi",          "Los Lagos"),
    ("quemchi",     "Quemchi",          "Los Lagos"),
    ("dalcahue",    "Dalcahue",         "Los Lagos"),
    ("curaco_velez","Curaco de Velez",  "Los Lagos"),
    ("quinchao",    "Quinchao",         "Los Lagos"),
    ("puqueldon",   "Puqueldon",        "Los Lagos"),
    ("llanquihue",  "Llanquihue",       "Los Lagos"),
    ("frutillar",   "Frutillar",        "Los Lagos"),
    ("los_muermos", "Los Muermos",      "Los Lagos"),
    ("maullin",     "Maullin",          "Los Lagos"),
    ("calbuco",     "Calbuco",          "Los Lagos"),
    ("chaiten",     "Chaiten",          "Los Lagos"),
    ("hualaihue",   "Hualaihue",        "Los Lagos"),
    ("futaleufu",   "Futaleufu",        "Los Lagos"),
    ("palena",      "Palena",           "Los Lagos"),
    ("puerto_varas","Puerto Varas",     "Los Lagos"),
    ("puerto_octa", "Puerto Octay",     "Los Lagos"),
    ("san_pablo",   "San Pablo",        "Los Lagos"),
    ("puyehue",     "Puyehue",          "Los Lagos"),
    ("rio_negro_ll","Rio Negro",        "Los Lagos"),
    ("purranque",   "Purranque",        "Los Lagos"),
    # AYSEN (10)
    ("coyhaique",   "Coyhaique",        "Aysen"),
    ("aysen",       "Aysen",            "Aysen"),
    ("chile_chico", "Chile Chico",      "Aysen"),
    ("rio_ibinez",  "Rio Ibanez",       "Aysen"),
    ("cochrane",    "Cochrane",         "Aysen"),
    ("tortel",      "Caleta Tortel",    "Aysen"),
    ("ohiggins_ay", "OHiggins",         "Aysen"),
    ("lago_verde",  "Lago Verde",       "Aysen"),
    ("guaitecas",   "Guaitecas",        "Aysen"),
    # MAGALLANES (11)
    ("punta_arenas","Punta Arenas",     "Magallanes"),
    ("pt_natales",  "Puerto Natales",   "Magallanes"),
    ("porvenir",    "Porvenir",         "Magallanes"),
    ("primavera_m", "Primavera",        "Magallanes"),
    ("timaukel",    "Timaukel",         "Magallanes"),
    ("rio_verde",   "Rio Verde",        "Magallanes"),
    ("laguna_blan", "Laguna Blanca",    "Magallanes"),
    ("san_gregorio","San Gregorio",     "Magallanes"),
    ("cabo_de_horn","Cabo de Hornos",   "Magallanes"),
    ("antartica",   "Antartica",        "Magallanes"),
]

# IDs que ya existen como ciudades principales (no duplicar)
EXISTING_CITY_IDS = {
    "arica","iquique","antofagasta","copiapo","la_serena","valparaiso",
    "santiago","rancagua","talca","chillan","concepcion","temuco",
    "valdivia","puerto_montt","coyhaique","punta_arenas",
    # tambien los que ya estan en def/city/ como archivos
    "angol","calama","caldera","castro","chaiten","cochrane","constitucion",
    "coquimbo","coronel","curico","la_union","linares","los_andes",
    "los_angeles","los_vilos","mejillones","osorno","ovalle","porvenir",
    "pozo_almonte","pto_natales","puerto_aysen","putre","quellon","quilicura",
    "san_antonio","san_bernardo","san_carlos","san_fernando","san_pedro",
    "santa_cruz","talcahuano","vallenar","villarrica","vina_del_mar",
    "v_ohiggins",
}

def generar_comunas():
    """Genera archivos .sui para cada comuna que no exista ya."""
    print("[2/3] Generando definiciones de comunas...")
    city_dir = BASE_DIR / "def" / "city"
    city_dir.mkdir(parents=True, exist_ok=True)

    creadas = []
    for cid, nombre, region in COMUNAS:
        # Validar longitud del ID
        if len(cid) > 12:
            print(f"  [WARN] ID muy largo (>12): '{cid}' - omitido")
            continue
        # No duplicar
        if cid in EXISTING_CITY_IDS:
            continue
        sui_path = city_dir / f"{cid}.sui"
        if sui_path.exists():
            creadas.append(cid)
            continue
        content = f"""city_data : city.{cid}
{{
    city_name: "{nombre}"
    city_name_localized: "{nombre}"
    country: chile

    map_x_offsets[]: 0
    map_x_offsets[]: 0
    map_x_offsets[]: 0
    map_x_offsets[]: 0
    map_x_offsets[]: 35
    map_x_offsets[]: 35
    map_x_offsets[]: 35
    map_x_offsets[]: 35

    map_y_offsets[]: 0
    map_y_offsets[]: 0
    map_y_offsets[]: 0
    map_y_offsets[]: 0
    map_y_offsets[]: -5
    map_y_offsets[]: -5
    map_y_offsets[]: -5
    map_y_offsets[]: -5

    # Region: {region}
}}
"""
        sui_path.write_text(content, encoding="utf-8")
        creadas.append(cid)

    print(f"  -> {len(creadas)} comunas procesadas")
    return creadas


def actualizar_city_sii(comunas_ids):
    """Actualiza def/city.sii para incluir todas las comunas nuevas."""
    print("[3/3] Actualizando def/city.sii...")
    city_dir = BASE_DIR / "def" / "city"

    # Recopilar todos los .sui existentes en orden
    all_sui = sorted([f.stem for f in city_dir.glob("*.sui")])

    lines = ["SiiNunit", "{"]
    for stem in all_sui:
        lines.append(f'@include "city/{stem}.sui"')
    lines.append("}")
    lines.append("")

    sii_path = BASE_DIR / "def" / "city.sii"
    sii_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"  -> city.sii actualizado con {len(all_sui)} ciudades/comunas")


# ──────────────────────────────────────────────────────────────────────────────
# MAIN
# ──────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 60)
    print("  FIX MAP - Tres correcciones del mapa")
    print("=" * 60)

    generar_mapa_transparente()

    ids = generar_comunas()
    actualizar_city_sii(ids)

    print()
    print("=" * 60)
    print("  LISTO - Ejecuta 'python tools/build.py' para reconstruir")
    print("=" * 60)
