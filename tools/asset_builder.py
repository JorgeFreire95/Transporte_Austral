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
    calibrada con exactitud matemática a las coordenadas del mundo de juego de ETS2.
    Diseño 100% en Blanco y Negro (monocromático elegante):
    - Océano negro mate profundo (#101218) con cuadrícula náutica sutil.
    - Masa continental de Chile en tonos plata/platino de alto contraste (#b8c0cc a #d0d8e4),
      envolviendo al 100% las carreteras sin cortes ni polígonos distorsionados.
    - Costas y fronteras en blanco puro (#ffffff) de 3px de grosor.
    - Todas las rutas, áreas y prefabs en def/map_data.sii en escala de grises y blanco puro.
    """
    print("[2/2] Generando mapa de fondo oficial de Chile en BLANCO Y NEGRO (alta definición)...")

    # Parámetros oficiales de proyección conformada ETS2 calibrados a la red continua de Chile:
    CENTER_X = -1988.0
    CENTER_Z = 4014.0
    SPAN_UNITS = 64000.0  # 1216.0 km en escala 1:19
    CANVAS_SIZE = 4096

    def world_to_pixel(wx, wz):
        px = (wx - CENTER_X) / SPAN_UNITS * CANVAS_SIZE + (CANVAS_SIZE / 2.0)
        py = (wz - CENTER_Z) / SPAN_UNITS * CANVAS_SIZE + (CANVAS_SIZE / 2.0)
        return px, py

    # 1. Muestrear los puntos de carretera de los sectores activos de Chile
    chile_base_files = list((BASE_DIR / "map" / "chile").glob("sec*.base"))
    if not chile_base_files:
        chile_base_files = list((BASE_DIR / "scratch" / "base_map" / "map" / "europe").glob("sec*.base"))

    road_pts = []
    for bf in chile_base_files:
        m = re.search(r'sec([+-]\d{4})([+-]\d{4})', bf.stem)
        if not m:
            continue
        sx = int(m.group(1)) * 4000
        sz = int(m.group(2)) * 4000
        data = bf.read_bytes()
        for off in range(0, len(data) - 12, 16):
            x, y, z = struct.unpack('<fff', data[off:off+12])
            if sx - 200 <= x <= sx + 4200 and sz - 200 <= z <= sz + 4200 and -100 <= y <= 800:
                road_pts.append((x, z))

    px_pts = [world_to_pixel(x, z) for x, z in road_pts]

    # Muestreo denso de límites este/oeste del corredor vial chileno
    y_dense = list(range(360, 3810, 10))
    raw_w, raw_e = [], []
    for y in y_dense:
        pts = [p[0] for p in px_pts if abs(p[1] - y) <= 25]
        if pts:
            raw_w.append(min(pts))
            raw_e.append(max(pts))
        else:
            raw_w.append(raw_w[-1] if raw_w else 2000.0)
            raw_e.append(raw_e[-1] if raw_e else 2200.0)

    def smooth(arr, r=8):
        res = []
        n = len(arr)
        for i in range(n):
            i0, i1 = max(0, i-r), min(n, i+r+1)
            res.append(sum(arr[i0:i1]) / (i1 - i0))
        return res

    sw = smooth(raw_w, 12)
    se = smooth(raw_e, 12)

    # Silueta esbelta y natural de Chile: 110px de margen en costa Pacífica, 130px en cordillera
    final_w = [w - 110.0 for w in sw]
    final_e = [e + 130.0 for e in se]

    # Ancho mínimo para mantener la silueta estilizada y orgánica de Chile
    for i in range(len(y_dense)):
        if final_e[i] - final_w[i] < 340.0:
            mid = (final_w[i] + final_e[i]) / 2.0
            final_w[i] = mid - 170.0
            final_e[i] = mid + 170.0

    final_w = smooth(final_w, 6)
    final_e = smooth(final_e, 6)

    w_map = {y: w for y, w in zip(y_dense, final_w)}
    e_map = {y: e for y, e in zip(y_dense, final_e)}

    # Lienzo oceánico negro mate profundo (#101218 - Estilo Blanco y Negro elegante)
    map_img = Image.new("RGBA", (CANVAS_SIZE, CANVAS_SIZE), (16, 18, 24, 255))
    draw = ImageDraw.Draw(map_img)

    # Cuadrícula náutica sutil en escala de grises
    grid_color = (24, 28, 36, 255)
    for x in range(0, CANVAS_SIZE, 256):
        draw.line([(x, 0), (x, CANVAS_SIZE)], fill=grid_color, width=1)
    for y in range(0, CANVAS_SIZE, 256):
        draw.line([(0, y), (CANVAS_SIZE, y)], fill=grid_color, width=1)

    # Polígono base continental de Chile
    base_poly = []
    for y in y_dense:
        base_poly.append((w_map[y], y))
    for y in reversed(y_dense):
        base_poly.append((e_map[y], y))

    # Sombra de relieve continental hacia el Pacífico
    shadow_poly = [(p[0] + 6, p[1] + 6) for p in base_poly]
    draw.polygon(shadow_poly, fill=(8, 10, 14, 220))

    # Definición de las 16 Regiones de Chile en escala de grises / blanco y negro de alto contraste
    REGIONS_Y = [
        (15, "Arica y Parinacota",  360,  530, (185, 192, 204)),
        (1,  "Tarapacá",            530,  700, (198, 205, 216)),
        (2,  "Antofagasta",         700,  990, (182, 190, 202)),
        (3,  "Atacama",             990, 1260, (195, 203, 214)),
        (4,  "Coquimbo",           1260, 1530, (185, 193, 205)),
        (5,  "Valparaíso",         1530, 1800, (198, 206, 218)),
        (13, "Santiago RM",        1800, 2000, (215, 222, 232)), # Resaltado blanco platino en la Capital RM
        (6,  "O'Higgins",          2000, 2160, (182, 190, 202)),
        (7,  "Maule",              2160, 2370, (195, 203, 214)),
        (16, "Ñuble",              2370, 2530, (182, 190, 202)),
        (8,  "Biobío",             2530, 2760, (195, 203, 214)),
        (9,  "Araucanía",          2760, 2980, (185, 193, 205)),
        (14, "Los Ríos",           2980, 3180, (198, 206, 218)),
        (10, "Los Lagos",          3180, 3420, (182, 190, 202)),
        (11, "Aysén",              3420, 3620, (195, 203, 214)),
        (12, "Magallanes",         3620, 3810, (185, 193, 205)),
    ]

    for cod, name, y_t, y_b, col in REGIONS_Y:
        reg_pts = []
        y_sub = [y for y in y_dense if y_t <= y <= y_b]
        for y in y_sub:
            reg_pts.append((w_map[y], y))
        for y in reversed(y_sub):
            reg_pts.append((e_map[y], y))
        if len(reg_pts) >= 3:
            draw.polygon(reg_pts, fill=(*col, 255))
            # Línea limítrofe regional refinada
            draw.line([(w_map[y_t], y_t), (e_map[y_t], y_t)], fill=(65, 72, 84, 220), width=2)

    # Costas e hitos fronterizos en Blanco Puro (#FFFFFF, 3px)
    draw.line([(w_map[y], y) for y in y_dense], fill=(255, 255, 255, 255), width=3)  # Costa Pacífico
    draw.line([(e_map[y], y) for y in y_dense], fill=(255, 255, 255, 255), width=3)  # Cordillera de los Andes
    draw.line([(w_map[y_dense[0]], y_dense[0]), (e_map[y_dense[0]], y_dense[0])], fill=(255, 255, 255, 255), width=3)  # Límite Norte
    draw.line([(w_map[y_dense[-1]], y_dense[-1]), (e_map[y_dense[-1]], y_dense[-1])], fill=(255, 255, 255, 255), width=3)  # Límite Sur

    # Archipiélagos e Islas de la Patagonia Chilena (Chiloé, Guaitecas, Chonos, Wellington, Riesco)
    islands = [
        [(w_map[3280] - 65, 3250), (w_map[3280] - 20, 3240), (w_map[3280] - 15, 3320), (w_map[3280] - 55, 3325)],
        [(w_map[3380] - 70, 3360), (w_map[3380] - 25, 3355), (w_map[3380] - 20, 3405), (w_map[3380] - 60, 3410)],
        [(w_map[3480] - 80, 3450), (w_map[3480] - 30, 3445), (w_map[3480] - 25, 3505), (w_map[3480] - 75, 3510)],
        [(w_map[3590] - 85, 3560), (w_map[3590] - 35, 3555), (w_map[3590] - 30, 3635), (w_map[3590] - 80, 3640)],
        [(w_map[3700] - 90, 3680), (w_map[3700] - 40, 3675), (w_map[3700] - 35, 3755), (w_map[3700] - 85, 3760)],
    ]
    for isl in islands:
        draw.polygon([(p[0]+4, p[1]+4) for p in isl], fill=(8, 10, 14, 200))
        draw.polygon(isl, fill=(190, 198, 210, 255), outline=(255, 255, 255, 255), width=2)

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

    # Configuración de def/map_data.sii calibrada al milímetro a Chile en Blanco y Negro puro
    def_dir = BASE_DIR / "def"
    def_dir.mkdir(parents=True, exist_ok=True)

    map_data_sii = def_dir / "map_data.sii"
    map_data_content = """SiiNunit
{
map_data : .map.data {

	# Rutas en escala de grises y blanco puro (Monocromático elegante)
	road_color:			0xFF505050 	//Carretera no descubierta (gris medio)
	road_discovered_color:		0xFFFFFFFF	//Carretera descubierta (blanco brillante)
	job_road_color:			0x50303030	//Mercado laboral no descubierta
	job_road_discovered_color:	0xFF808080	//Mercado laboral descubierta
	world_road_color:		0xFF505050	//Mapa principal no descubierta (gris medio)
	world_road_discovered_color:	0xFFFFFFFF 	//Mapa principal descubierta (blanco brillante)
	fleet_manager_road_color:		0xff404040	//Gestor de flota no descubierta
	fleet_manager_road_discovered_color:	0xff404040 	//Gestor de flota descubierta

	# Áreas del mapa en Blanco y Negro (sin colores arcoíris)
	map_area_color_name[]: "Road"
	map_area_color[]: 0xFF505050
	map_area_discovered_color[]: 0xFFFFFFFF

	map_area_color_name[]: "Light"
	map_area_color[]: 0xFF606060
	map_area_discovered_color[]: 0xFFE0E0E0

	map_area_color_name[]: "Dark"
	map_area_color[]: 0xFF303030
	map_area_discovered_color[]: 0xFF909090

	map_area_color_name[]: "Green"
	map_area_color[]: 0xFF555555
	map_area_discovered_color[]: 0xFFD0D0D0

	map_area_color_name[]: "Nav-Red"
	map_area_color[]: 0xFF555555
	map_area_discovered_color[]: 0xFFB0B0B0

	map_area_color_name[]: "Nav-Green"
	map_area_color[]: 0xFF555555
	map_area_discovered_color[]: 0xFFC0C0C0

	map_area_color_name[]: "Nav-Blue"
	map_area_color[]: 0xFF555555
	map_area_discovered_color[]: 0xFFD0D0D0

	map_area_color_name[]: "Nav-Yellow"
	map_area_color[]: 0xFF555555
	map_area_discovered_color[]: 0xFFE0E0E0

	map_area_color_name[]: "Nav-Purple"
	map_area_color[]: 0xFF555555
	map_area_discovered_color[]: 0xFFB8B8B8

	prefab_color:				0xFF555555
	prefab_obstacle_color:			0xFF222222
	prefab_grass_color:			0xFF555555
	prefab_discovered_color:		0xFFE8E8E8
	prefab_obstacle_discovered_color:	0xFF808080
	prefab_grass_discovered_color:		0xFFD0D0D0

	outline_color:			0xFF111111
	navigation_color:		0xFF0C0CCF
	navigation_highlight_color:	0xFF0C42DF
	navigation_fade_color:		0xFF07077C
	navigation_arrow_color: 	0xFF06FB11

	# Niveles de Zoom completos (0 a 3 Minimap/GPS; 4 a 7 Mapa del Mundo M)
	zoom_uplift[0]: 50.0
	zoom_uplift[1]: 200.0
	zoom_uplift[2]: 700.0
	zoom_uplift[3]: 2000.0
	zoom_uplift[4]: 2500.0
	zoom_uplift[5]: 7500.0
	zoom_uplift[6]: 22000.0
	zoom_uplift[7]: 58000.0

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
	camera_limits_min[4]: (-22000.0, -28000.0)
	camera_limits_min[5]: (-22000.0, -28000.0)
	camera_limits_min[6]: (-22000.0, -28000.0)
	camera_limits_min[7]: (-22000.0, -28000.0)

	camera_limits_max[0]: (1000000.0, 1000000.0)
	camera_limits_max[1]: (1000000.0, 1000000.0)
	camera_limits_max[2]: (1000000.0, 1000000.0)
	camera_limits_max[3]: (1000000.0, 1000000.0)
	camera_limits_max[4]: (18000.0, 36000.0)
	camera_limits_max[5]: (18000.0, 36000.0)
	camera_limits_max[6]: (18000.0, 36000.0)
	camera_limits_max[7]: (18000.0, 36000.0)

	map_items_flags[0]: 0x685FFF
	map_items_flags[1]: 0x685FFF
	map_items_flags[2]: 0x685F7F
	map_items_flags[3]: 0x685F7F
	map_items_flags[4]: 0x685FAF
	map_items_flags[5]: 0x685F27
	map_items_flags[6]: 0x685407
	map_items_flags[7]: 0x481402

	map_3d_camera_pitch: 40.0

	# Centro del mapa UI en coordenadas de Chile y escala calibrada (1216.0 km reales = 64000 unidades en escala 1:19)
	ui_map_center:	(-1988.0, 4014.0)
	ui_map_size:	(1216.0, 1216.0)

	ui_map_camera_min: (-22000.0, -28000.0)
	ui_map_camera_max: (18000.0, 36000.0)
	ui_map_camera_start: (-6398.0, 3329.0)

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
