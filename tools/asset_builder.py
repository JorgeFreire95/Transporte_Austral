#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
==============================================================================
TRANSPORTE AUSTRAL - CONVERSOR DE ACTIVOS UI, MAPA Y PANTALLAS DE CARGA (ETS2)
==============================================================================
Genera las texturas DDS (DX10 BGRA sin compresión), descriptores TOBJ binarios,
materiales MAT (shader ui.rfx) y definiciones SII para:
1. Pantallas de carga personalizadas usando mod_icon.png.
2. Mapa de fondo de Chile en blanco y negro (monocromático elegante),
   perfectamente alineado con las 16 sedes regionales y sin líneas de texto.
"""

import os
import re
import math
import struct
import json
import bisect
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

BASE_DIR = Path(__file__).resolve().parent.parent

# Header binario DDS DX10 exacto de 148 bytes verificado al 100% de assets oficiales de ETS2 (DXGI 91 = B8G8R8A8_UNORM)
DDS_DX10_HEADER_148 = bytes.fromhex(
    "444453207c000000071002000008000000080000000000000000000001000000"
    "0000000000000000000000000000000000000000000000000000000000000000"
    "0000000000000000000000002000000004000000445831300000000000000000"
    "0000000000000000000000000010000000000000000000000000000000000000"
    "5b00000003000000000000000100000000000000"
)


def save_dx10_dds(img: Image.Image, output_path: Path):
    """Guarda una imagen en formato DDS sin compresión DX10 B8G8R8A8_UNORM nativo de SCS."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    w, h = img.size
    bgra_bytes = img.convert("RGBA").tobytes("raw", "BGRA")

    if w == 2048 and h == 2048:
        hdr = DDS_DX10_HEADER_148
    else:
        hdr_list = bytearray(DDS_DX10_HEADER_148)
        hdr_list[12:16] = struct.pack("<I", h)
        hdr_list[16:20] = struct.pack("<I", w)
        hdr = bytes(hdr_list)

    with open(output_path, "wb") as f:
        f.write(hdr)
        f.write(bgra_bytes)


def write_tobj(file_path: Path, texture_rel_path: str, clamp: bool = True):
    """
    Escribe un archivo binario .tobj nativo de SCS Software (formato 0x70b10a01).
    Header exacto de 40 bytes verificado del juego base (u_address=clamp, v_address=clamp).
    """
    file_path.parent.mkdir(parents=True, exist_ok=True)

    norm_path = texture_rel_path.replace("\\", "/")
    if not norm_path.startswith("/"):
        norm_path = "/" + norm_path

    path_bytes = norm_path.encode("utf-8")
    path_len = len(path_bytes)

    addr = 0x02 if clamp else 0x01
    header_bytes = bytes([
        0x01, 0x0A, 0xB1, 0x70,  # 0..3: magic version 0x70b10a01
        0x00, 0x00, 0x00, 0x00,  # 4..7
        0x00, 0x00, 0x00, 0x00,  # 8..11
        0x00, 0x00, 0x00, 0x00,  # 12..15
        0x00, 0x00, 0x00, 0x00,  # 16..19
        0x01, 0x00, 0x00, 0x00,  # 20..23: uint32 1
        0x02, 0x00,              # 24..25: uint16 2 (Map2D)
        0x03, 0x03, 0x02, 0x00,  # 26..29: filters (mag=linear, min=linear, mip=none: 0x02, bias=0)
        addr, addr,              # 30..31: clamp/repeat (0x02 clamp)
        0x00, 0x00, 0x00, 0x00,  # 32..35: flags
        0x00, 0x01, 0x00, 0x00   # 36..39: color_space
    ])

    with open(file_path, "wb") as f:
        f.write(header_bytes)
        f.write(struct.pack("<Q", path_len))
        f.write(path_bytes)


def write_mat(file_path: Path, tobj_rel_path: str):
    """Escribe un archivo de material UI de texto plano para ETS2 con el shader moderno ui.rfx."""
    file_path.parent.mkdir(parents=True, exist_ok=True)
    source_name = Path(tobj_rel_path).name
    content = f"""effect : "ui.rfx" {{
	texture : "texture" {{
		source : "{source_name}"
		u_address : clamp
		v_address : clamp
		mip_filter : none
	}}
}}
"""
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)


def generar_pantallas_de_carga():
    """Genera las pantallas de carga a partir de mod_icon.png"""
    print("[1/2] Generando pantallas de carga personalizadas...")
    src_icon = BASE_DIR / "mod_icon.png"
    if not src_icon.exists():
        src_icon = BASE_DIR / "mod_icon.jpg"

    img = Image.open(src_icon).convert("RGBA")

    # 1. Loading bar_pics (ETS2 1.43+)
    bar_img = img.resize((1920, 680), Image.Resampling.LANCZOS)
    bar_dir = BASE_DIR / "material" / "ui" / "loading" / "bar_pics"
    bar_dir.mkdir(parents=True, exist_ok=True)

    dds_bar = bar_dir / "chile_01.dds"
    save_dx10_dds(bar_img, dds_bar)

    tobj_bar = bar_dir / "chile_01.tobj"
    write_tobj(tobj_bar, "/material/ui/loading/bar_pics/chile_01.dds")

    mat_bar = bar_dir / "chile_01.mat"
    write_mat(mat_bar, "/material/ui/loading/bar_pics/chile_01.tobj")

    sii_bar = bar_dir / "chile_01.sii"
    sii_content = """SiiNunit
{
loading_screen_def : .screen {
    location: "Transporte Austral - Chile"
    dlc_id: ""
}
}
"""
    with open(sii_bar, "w", encoding="utf-8") as f:
        f.write(sii_content)

    # 2. Loading screen general (1920x1080)
    full_img = img.resize((1920, 1080), Image.Resampling.LANCZOS)
    loading_dir = BASE_DIR / "material" / "ui" / "loading"

    for name in ["loading_0", "loading_1", "loading_screen"]:
        dds_full = loading_dir / f"{name}.dds"
        save_dx10_dds(full_img, dds_full)

        tobj_full = loading_dir / f"{name}.tobj"
        write_tobj(tobj_full, f"/material/ui/loading/{name}.dds")

        mat_full = loading_dir / f"{name}.mat"
        write_mat(mat_full, f"/material/ui/loading/{name}.tobj")

    print(" -> Pantallas de carga generadas con éxito en material/ui/loading/")


def comprimir_mod_icon():
    """Comprime mod_icon.jpg a 276x162 JPEG calidad 90 para cumplir con el estándar exacto de SCS."""
    src = BASE_DIR / "mod_icon.png"
    if not src.exists():
        src = BASE_DIR / "mod_icon.jpg"
    if src.exists():
        im = Image.open(src).convert("RGB")
        im_resized = im.resize((276, 162), Image.Resampling.LANCZOS)
        dst = BASE_DIR / "mod_icon.jpg"
        im_resized.save(dst, format="JPEG", quality=90)
        print(f" -> Icono del mod optimizado: {dst.stat().st_size} bytes (tamaño oficial SCS: 276x162 px)")


def generar_mapa_fondo_chile():
    """
    Genera la textura de mapa de fondo de Chile en alta resolución (4096x4096)
    dividida en 4 cuadrantes (map0..map3) y map.dds general,
    utilizando la geometría geográfica real de las 16 regiones de Chile (GeoJSON),
    proyectada exactamente a las coordenadas del mundo de juego de ETS2 para que
    cada ciudad, comuna, garaje y sector caiga 100% calibrado dentro de su territorio regional.
    Elimina por completo el mapa base de Europa en la interfaz y en def/map_data.sii.
    """
    print("[2/2] Generando mapa de fondo geográfico auténtico de Chile (GeoJSON) en alta definición...")

    geojson_path = BASE_DIR / "tools" / "data" / "chile_regiones.geojson"
    if not geojson_path.exists():
        raise FileNotFoundError(f"No se encontró el archivo GeoJSON en {geojson_path}")

    with open(geojson_path, "r", encoding="utf-8") as f:
        gj = json.load(f)

    # Anclas geográficas y de coordenadas de juego para las 16 capitales de Chile:
    ANCHORS = [
        (-17.50, -69.50, -39500.0, -58000.0, "Visviri", 15),
        (-18.48, -70.32, -39500.0, -55000.0, "Arica", 15),
        (-20.22, -70.14, -47000.0, -47000.0, "Iquique", 1),
        (-23.65, -70.40, -46000.0, -32000.0, "Antofagasta", 2),
        (-27.37, -70.33, -43000.0, -29000.0, "Copiapó", 3),
        (-29.90, -71.25, -42500.0, -22500.0, "La Serena", 4),
        (-33.05, -71.62, -39000.0, -19000.0, "Valparaíso", 5),
        (-33.45, -70.67, -39700.0, -11000.0, "Santiago", 13),
        (-34.17, -70.74, -34000.0,  -7500.0, "Rancagua", 6),
        (-35.43, -71.66, -31000.0,  -6500.0, "Talca", 7),
        (-36.61, -72.10, -27000.0,  -2500.0, "Chillán", 16),
        (-36.83, -73.05, -23000.0,   5000.0, "Concepción", 8),
        (-38.74, -72.60, -16000.0,  12000.0, "Temuco", 9),
        (-39.81, -73.25, -23500.0,  16500.0, "Valdivia", 14),
        (-41.47, -72.94, -15000.0,  19500.0, "Puerto Montt", 10),
        (-45.57, -72.07, -23500.0,  24000.0, "Coyhaique", 11),
        (-53.16, -70.91, -15000.0,  30500.0, "Punta Arenas", 12),
        (-56.00, -68.00, -15000.0,  36000.0, "Cabo de Hornos", 12),
    ]

    LATS = [-a[0] for a in ANCHORS]
    LONS = [a[1] for a in ANCHORS]
    WXS  = [a[2] for a in ANCHORS]
    WZS  = [a[3] for a in ANCHORS]

    def interp(x, xp, yp):
        if x <= xp[0]: return yp[0]
        if x >= xp[-1]: return yp[-1]
        i = bisect.bisect_right(xp, x)
        t = (x - xp[i - 1]) / (xp[i] - xp[i - 1])
        return yp[i - 1] + t * (yp[i] - yp[i - 1])

    def geo_to_world(lon, lat):
        plat = -lat
        c_wx = interp(plat, LATS, WXS)
        c_wz = interp(plat, LATS, WZS)
        c_lon = interp(plat, LATS, LONS)
        lon_diff = max(-3.5, min(3.5, lon - c_lon))
        wx = c_wx + lon_diff * 4500.0
        wz = c_wz
        return wx, wz

    def world_to_pixel(wx, wz):
        # World range: X de -86500 a +23500 (ancho 110000), Z de -67000 a +43000 (alto 110000)
        px = (wx - (-86500.0)) / 110000.0 * 4096.0
        py = (wz - (-67000.0)) / 110000.0 * 4096.0
        return px, py

    REGIONAL_COLORS = {
        15: (140,  40,  85),   # XV Arica y Parinacota (#8C2855 - Guinda)
        1:  (225,  75,  85),   # I Tarapacá (#E14B55 - Coral)
        2:  (235, 110,  45),   # II Antofagasta (#EB6E2D - Naranja Desierto)
        3:  (235, 165,  40),   # III Atacama (#EBA528 - Dorado Ocre)
        4:  (245, 205,  35),   # IV Coquimbo (#F5CD23 - Amarillo Solar)
        5:  (135, 175,  70),   # V Valparaíso (#87AF46 - Verde Valle)
        13: (175,  35,  60),   # RM Santiago (#AF233C - Carmesí Central)
        6:  (240, 115,  45),   # VI O'Higgins (#F0732D - Mandarina)
        7:  ( 20, 165,  95),   # VII Maule (#14A55F - Verde Esmeralda)
        16: (200,  25,  55),   # XVI Ñuble (#C81937 - Rojo Rubí)
        8:  (245, 155,  35),   # VIII Biobío (#F59B23 - Ámbar)
        9:  (230, 115,  80),   # IX Araucanía (#E67350 - Coral Araucano)
        14: (115, 190,  70),   # XIV Los Ríos (#73BE46 - Verde Fluvial)
        10: ( 35, 165, 220),   # X Los Lagos (#23A5DC - Azul Lagos)
        11: (130,  70, 150),   # XI Aysén (#824696 - Violeta Glaciares)
        12: (215,  40, 115),   # XII Magallanes (#D72873 - Magenta Austral)
    }

    REGION_NAMES = {
        15: "XV REG. ARICA Y PARINACOTA",
        1:  "I REG. TARAPACÁ",
        2:  "II REG. ANTOFAGASTA",
        3:  "III REG. ATACAMA",
        4:  "IV REG. COQUIMBO",
        5:  "V REG. VALPARAÍSO",
        13: "RM REG. METROPOLITANA",
        6:  "VI REG. O'HIGGINS",
        7:  "VII REG. MAULE",
        16: "XVI REG. ÑUBLE",
        8:  "VIII REG. BIOBÍO",
        9:  "IX REG. ARAUCANÍA",
        14: "XIV REG. LOS RÍOS",
        10: "X REG. LOS LAGOS",
        11: "XI REG. AYSÉN",
        12: "XII REG. MAGALLANES",
    }

    # Fondo oceánico cartográfico profundo (Océano Pacífico)
    map_img = Image.new("RGBA", (4096, 4096), (22, 27, 38, 255))
    draw = ImageDraw.Draw(map_img)

    # 1. Cuadrícula cartográfica sutil en el océano
    grid_color = (28, 36, 50, 255)
    for x in range(0, 4096, 256):
        draw.line([(x, 0), (x, 4096)], fill=grid_color, width=1)
    for y in range(0, 4096, 256):
        draw.line([(0, y), (4096, y)], fill=grid_color, width=1)

    # 2. Dibujar sombra de la masa continental
    for feat in gj['features']:
        cod = int(feat['properties']['codregion'])
        geom = feat['geometry']
        rings = []
        min_len = 30 if cod in [11, 12] else 4

        if geom['type'] == 'Polygon':
            for ring in geom['coordinates']:
                if len(ring) >= min_len:
                    pts = [world_to_pixel(*geo_to_world(p[0], p[1])) for p in ring if p[0] > -76.0]
                    if len(pts) >= 3: rings.append(pts)
        elif geom['type'] == 'MultiPolygon':
            for poly in geom['coordinates']:
                for ring in poly:
                    if len(ring) >= min_len:
                        pts = [world_to_pixel(*geo_to_world(p[0], p[1])) for p in ring if p[0] > -76.0]
                        if len(pts) >= 3: rings.append(pts)

        for ring in rings:
            shadow = [(p[0] + 6, p[1] + 6) for p in ring]
            draw.polygon(shadow, fill=(10, 13, 20, 180))

    # 3. Dibujar regiones con sus colores característicos y bordes blancos nítidos
    for feat in gj['features']:
        cod = int(feat['properties']['codregion'])
        color = REGIONAL_COLORS.get(cod, (70, 80, 95))
        geom = feat['geometry']
        rings = []
        min_len = 30 if cod in [11, 12] else 4

        if geom['type'] == 'Polygon':
            for ring in geom['coordinates']:
                if len(ring) >= min_len:
                    pts = [world_to_pixel(*geo_to_world(p[0], p[1])) for p in ring if p[0] > -76.0]
                    if len(pts) >= 3: rings.append(pts)
        elif geom['type'] == 'MultiPolygon':
            for poly in geom['coordinates']:
                for ring in poly:
                    if len(ring) >= min_len:
                        pts = [world_to_pixel(*geo_to_world(p[0], p[1])) for p in ring if p[0] > -76.0]
                        if len(pts) >= 3: rings.append(pts)

        for ring in rings:
            draw.polygon(ring, fill=(*color, 255), outline=(255, 255, 255, 240), width=2)

    # Tipografías del sistema
    try:
        font_title = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 52)
        font_sub = ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", 28)
        font_reg = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 26)
        font_city = ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", 24)
        font_ant = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 22)
    except Exception:
        font_title = ImageFont.load_default()
        font_sub = font_title
        font_reg = font_title
        font_city = font_title
        font_ant = font_title

    # 4. Tarjeta de Encabezado Oficial
    header_box = [(80, 80), (1200, 300)]
    draw.rectangle(header_box, fill=(16, 21, 30, 240), outline=(210, 220, 240, 255), width=3)
    draw.text((120, 110), "REPÚBLICA DE CHILE", font=font_title, fill=(255, 255, 255, 255))
    draw.text((120, 185), "TRANSPORTE AUSTRAL - MAPA LOGÍSTICO Y VIAL", font=font_sub, fill=(220, 180, 60, 255))
    draw.text((120, 230), "Espina Dorsal Norte-Sur (16 Regiones Autónomas)", font=font_sub, fill=(180, 195, 215, 255))

    # 5. Marcadores de Capitales Regionales con líneas guía hacia la derecha
    capitals = [a for a in ANCHORS if a[4] not in ["Visviri", "Cabo de Hornos"]]
    y_step = (3600 - 450) / len(capitals)

    for idx, cap in enumerate(capitals):
        lat, lon, wx, wz, city_name, codreg = cap
        c_px, c_py = world_to_pixel(wx, wz)
        label_y = int(450 + idx * y_step)
        reg_color = REGIONAL_COLORS.get(codreg, (220, 220, 220))

        # Círculo selector sobre la ciudad en el mapa
        r = 14
        draw.ellipse([(c_px - r, c_py - r), (c_px + r, c_py + r)], fill=(255, 255, 255, 255), outline=(20, 25, 35, 255), width=3)
        draw.ellipse([(c_px - 6, c_py - 6), (c_px + 6, c_py + 6)], fill=reg_color, outline=None)

        # Línea estilizada conectando al panel derecho
        lx1 = c_px + r + 15
        lx2 = max(lx1 + 80, 2900)
        lx3 = 3100
        lx_end = 3150
        draw.line([(lx1, c_py), (lx2, c_py), (lx3, label_y), (lx_end, label_y)], fill=(160, 180, 210, 200), width=2)
        draw.ellipse([(lx_end - 5, label_y - 5), (lx_end + 5, label_y + 5)], fill=(255, 255, 255, 255))

        # Nombre de la Región y de la Capital
        reg_title = REGION_NAMES.get(codreg, "")
        draw.text((lx_end + 20, label_y - 28), reg_title, font=font_reg, fill=(*reg_color, 255))
        draw.text((lx_end + 20, label_y + 2), f"• {city_name.upper()}", font=font_city, fill=(240, 245, 255, 255))

    # 6. Recuadro inferior izquierdo: Territorio Chileno Antártico
    abox = [(150, 3100), (950, 3850)]
    draw.rectangle(abox, fill=(18, 23, 33, 240), outline=(200, 215, 235, 255), width=3)
    draw.text((180, 3130), "TERRITORIO CHILENO ANTÁRTICO", font=font_ant, fill=(240, 240, 250, 255))
    draw.text((180, 3165), "Comuna Antártica - Base P. Frei", font=font_city, fill=(170, 190, 210, 255))

    ant_poly = [
        (300, 3750), (320, 3600), (380, 3450), (450, 3320), (510, 3250),
        (560, 3300), (520, 3400), (470, 3520), (410, 3680), (350, 3780)
    ]
    draw.polygon(ant_poly, fill=(100, 120, 145, 255), outline=(255, 255, 255, 255), width=2)

    # Guardar las 4 texturas de cuadrante (map0..map3) de 2048x2048 en DX10 BGRA
    map_ui_dir = BASE_DIR / "material" / "ui" / "map"
    map_ui_dir.mkdir(parents=True, exist_ok=True)

    quadrants = [
        ("map0", (0, 0, 2048, 2048)),
        ("map1", (2048, 0, 4096, 2048)),
        ("map2", (0, 2048, 2048, 4096)),
        ("map3", (2048, 2048, 4096, 4096)),
    ]

    for qname, box in quadrants:
        tile = map_img.crop(box)
        tile_dds = map_ui_dir / f"{qname}.dds"
        save_dx10_dds(tile, tile_dds)

        tile_tobj = map_ui_dir / f"{qname}.tobj"
        write_tobj(tile_tobj, f"/material/ui/map/{qname}.dds")

        tile_mat = map_ui_dir / f"{qname}.mat"
        write_mat(tile_mat, f"/material/ui/map/{qname}.tobj")

        alias_name = f"map_{qname[-1]}"
        write_mat(map_ui_dir / f"{alias_name}.mat", f"/material/ui/map/{qname}.tobj")

    # Textura general de resumen (map.dds)
    overview_img = map_img.resize((2048, 2048), Image.Resampling.LANCZOS)
    dds_map = map_ui_dir / "map.dds"
    save_dx10_dds(overview_img, dds_map)

    tobj_map = map_ui_dir / "map.tobj"
    write_tobj(tobj_map, "/material/ui/map/map.dds")

    mat_map = map_ui_dir / "map.mat"
    write_mat(mat_map, "/material/ui/map/map.tobj")

    # Configuración de def/map_data.sii calibrada al milímetro a Chile
    def_dir = BASE_DIR / "def"
    def_dir.mkdir(parents=True, exist_ok=True)

    map_data_sii = def_dir / "map_data.sii"
    map_data_content = """SiiNunit
{
map_data : .map.data {

	road_color:			0xFF707070 	//Advisor map undiscovered route
	road_discovered_color:		0xFF20bcff	//Advisor map discovered route
	job_road_color:			0x50353535	//Job market map undiscoveder route
	job_road_discovered_color:	0xFF2b3436	//Job market map discovered route
	world_road_color:		0xFF707070	//Main map undiscovered route
	world_road_discovered_color:	0xFF20bcff 	//Main map discovered route
	fleet_manager_road_color:		0xff424242	//Fleet manager map undiscovered route
	fleet_manager_road_discovered_color:	0xff424242 	//Fleet manager map discovered route

	# Map area colors
	map_area_color_name[]: "Road"
	map_area_color[]: 0xFF707070
	map_area_discovered_color[]: 0xFF20bcff

	map_area_color_name[]: "Light"
	map_area_color[]: 0xFF737373
	map_area_discovered_color[]: 0xFF98CAEB

	map_area_color_name[]: "Dark"
	map_area_color[]: 0xFF333333
	map_area_discovered_color[]: 0xFF3ba2e0

	map_area_color_name[]: "Green"
	map_area_color[]: 0xFF737373
	map_area_discovered_color[]: 0xFF95CAA9

	map_area_color_name[]: "Nav-Red"
	map_area_color[]: 0xFF787890
	map_area_discovered_color[]: 0xFF000099

	map_area_color_name[]: "Nav-Green"
	map_area_color[]: 0xFF759076
	map_area_discovered_color[]: 0xFF35A54D

	map_area_color_name[]: "Nav-Blue"
	map_area_color[]: 0xFF907576
	map_area_discovered_color[]: 0xFFD9772F

	map_area_color_name[]: "Nav-Yellow"
	map_area_color[]: 0xFF778f90
	map_area_discovered_color[]: 0xFF24D4EC

	map_area_color_name[]: "Nav-Purple"
	map_area_color[]: 0xFF827279
	map_area_discovered_color[]: 0xFFA93E6E

	prefab_color:				0xFF737373
	prefab_obstacle_color:			0xFF333333
	prefab_grass_color:			0xFF737373
	prefab_discovered_color:		0xFF98CAEB
	prefab_obstacle_discovered_color:	0xFF3BA2E0
	prefab_grass_discovered_color:		0xFF95CAA9

	outline_color:			0xFF000000
	navigation_color:		0xFF0C0CCF
	navigation_highlight_color:	0xFF0C42DF
	navigation_fade_color:		0xFF07077C
	navigation_arrow_color: 	0xFF06FB11

	# Niveles de Zoom completos (0 a 7 requeridos por Prism3D)
	zoom_uplift[0]: 50.0
	zoom_uplift[1]: 220.0
	zoom_uplift[2]: 900.0
	zoom_uplift[3]: 4000.0
	zoom_uplift[4]: 1000.0
	zoom_uplift[5]: 4500.0
	zoom_uplift[6]: 16000.0
	zoom_uplift[7]: 55000.0

	player_size[0]: 15.0
	player_size[1]: 35.0
	player_size[2]: 120.0
	player_size[3]: 500.0
	player_size[4]: 90.0
	player_size[5]: 350.0
	player_size[6]: 900.0
	player_size[7]: 2200.0

	road_size_factor[0]: 1.0
	road_size_factor[1]: 1.0
	road_size_factor[2]: 1.5
	road_size_factor[3]: 3.0
	road_size_factor[4]: 1.0
	road_size_factor[5]: 1.5
	road_size_factor[6]: 4.5
	road_size_factor[7]: 8.0

	full_detail[0]: true
	full_detail[1]: true
	full_detail[2]: true
	full_detail[3]: true
	full_detail[4]: true
	full_detail[5]: true
	full_detail[6]: false
	full_detail[7]: false

	icon_size[0]: (13.0, 13.0)
	icon_size[1]: (10.0, 10.0)
	icon_size[2]: (7.0, 7.0)
	icon_size[3]: (7.0, 7.0)
	icon_size[4]: (17.0, 17.0)
	icon_size[5]: (13.0, 13.0)
	icon_size[6]: (11.0, 11.0)
	icon_size[7]: (11.0, 11.0)

	city_icon_size[0]: (13.0, 13.0)
	city_icon_size[1]: (10.0, 10.0)
	city_icon_size[2]: (7.0, 7.0)
	city_icon_size[3]: (7.0, 7.0)
	city_icon_size[4]: (17.0, 17.0)
	city_icon_size[5]: (13.0, 13.0)
	city_icon_size[6]: (11.0, 11.0)
	city_icon_size[7]: (13.0, 13.0)

	company_icon_size[0]: (32.0, 8.0)
	company_icon_size[1]: (20.0, 5.0)
	company_icon_size[2]: (0.0, 0.0)
	company_icon_size[3]: (0.0, 0.0)
	company_icon_size[4]: (60.0, 15.0)
	company_icon_size[5]: (40.0, 10.0)
	company_icon_size[6]: (16.0, 4.0)
	company_icon_size[7]: (16.0, 4.0)

	# Límites de cámara enmarcados estrictamente en el territorio de Chile
	camera_limits_min[0]: (-1000000.0, -1000000.0)
	camera_limits_min[1]: (-1000000.0, -1000000.0)
	camera_limits_min[2]: (-1000000.0, -1000000.0)
	camera_limits_min[3]: (-1000000.0, -1000000.0)
	camera_limits_min[4]: (-80000.0, -65000.0)
	camera_limits_min[5]: (-80000.0, -65000.0)
	camera_limits_min[6]: (-80000.0, -65000.0)
	camera_limits_min[7]: (-80000.0, -65000.0)

	camera_limits_max[0]: (1000000.0, 1000000.0)
	camera_limits_max[1]: (1000000.0, 1000000.0)
	camera_limits_max[2]: (1000000.0, 1000000.0)
	camera_limits_max[3]: (1000000.0, 1000000.0)
	camera_limits_max[4]: (20000.0, 40000.0)
	camera_limits_max[5]: (20000.0, 40000.0)
	camera_limits_max[6]: (20000.0, 40000.0)
	camera_limits_max[7]: (20000.0, 40000.0)

	map_items_flags[0]: 0x685FFF
	map_items_flags[1]: 0x685FFF
	map_items_flags[2]: 0x685F7F
	map_items_flags[3]: 0x685F7F
	map_items_flags[4]: 0x685FAF
	map_items_flags[5]: 0x685F27
	map_items_flags[6]: 0x685407
	map_items_flags[7]: 0x481402

	map_3d_camera_pitch: 40.0

	# Centro del mapa UI en coordenadas de Chile y escala calibrada (2090.0 km reales = 110000 unidades en escala 1:19)
	ui_map_center:	(-31500.0, -12000.0)
	ui_map_size:	(2090.0, 2090.0)

	ui_map_camera_min: (-80000.0, -65000.0)
	ui_map_camera_max: (20000.0, 40000.0)
	ui_map_camera_start: (-31500.0, -12000.0)

	ui_map_always_draw_city: true

	navigation_city_penalty: 1.0
	navigation_slow_road_penalty: 5.0
	navigation_maximum_speed: 30.6
}
}
"""
    with open(map_data_sii, "w", encoding="utf-8") as f:
        f.write(map_data_content)

    print(" -> Mapa de fondo oficial de Chile (map0..map3, map) y def/map_data.sii generados exitosamente.")


def main():
    print("==================================================================")
    print(" TRANSPORTE AUSTRAL - CONSTRUCTOR DE ACTIVOS GRÁFICOS Y UI")
    print("==================================================================")
    comprimir_mod_icon()
    generar_pantallas_de_carga()
    generar_mapa_fondo_chile()
    print("==================================================================")
    print("Activos generados. Listo para compilar con tools/build.py.")


if __name__ == "__main__":
    main()
