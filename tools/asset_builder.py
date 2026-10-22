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
    dividida en 4 cuadrantes (map0..map3) y map.dds en BLANCO Y NEGRO,
    utilizando la geometría geográfica real de las 16 regiones de Chile (GeoJSON),
    proyectada suavemente para que cada ciudad/sede caiga exactamente dentro de su
    territorio regional con bordes blancos nítidos y sin distorsión de tubo.
    """
    print("[2/2] Generando mapa de fondo geográfico auténtico de Chile (GeoJSON) en blanco y negro...")

    geojson_path = BASE_DIR / "tools" / "data" / "chile_regiones.geojson"
    if not geojson_path.exists():
        raise FileNotFoundError(f"No se encontró el archivo GeoJSON en {geojson_path}")

    with open(geojson_path, "r", encoding="utf-8") as f:
        gj = json.load(f)

    # Anclas geográficas precisas y suaves para un trazado limpio y natural de Chile:
    ANCHORS = [
        (-17.50, -69.50, 1585.0, 1340.0),  # Extremo Norte (Visviri)
        (-18.48, -70.32, 1585.0, 1376.4),  # XV Arica
        (-20.22, -70.14, 1590.0, 1418.3),  # I Iquique
        (-23.65, -70.40, 1610.0, 1650.2),  # II Antofagasta
        (-27.37, -70.33, 1625.0, 1671.5),  # III Copiapó
        (-29.90, -71.25, 1635.0, 1801.2),  # IV La Serena
        (-33.05, -71.62, 1655.0, 1868.6),  # V Valparaíso
        (-33.45, -70.67, 1665.0, 1924.9),  # RM Santiago
        (-34.17, -70.74, 1690.0, 1980.2),  # VI Rancagua
        (-35.43, -71.66, 1750.0, 2050.4),  # VII Talca
        (-36.61, -72.10, 1810.0, 2091.9),  # XVI Chillán
        (-36.83, -73.05, 1870.0, 2203.5),  # VIII Concepción
        (-38.74, -72.60, 1930.0, 2305.9),  # IX Temuco
        (-39.81, -73.25, 1960.0, 2380.3),  # XIV Valdivia
        (-41.47, -72.94, 1990.0, 2429.5),  # X Puerto Montt
        (-45.57, -72.07, 2020.0, 2500.2),  # XI Coyhaique
        (-53.16, -70.91, 2050.0, 2574.8),  # XII Punta Arenas
        (-56.00, -68.00, 2080.0, 2680.0),  # Cabo de Hornos
    ]

    POS_LATS = [-c[0] for c in ANCHORS]
    LONS = [c[1] for c in ANCHORS]
    PXS = [c[2] for c in ANCHORS]
    PYS = [c[3] for c in ANCHORS]

    def interp(x, xp, yp):
        if x <= xp[0]: return yp[0]
        if x >= xp[-1]: return yp[-1]
        i = bisect.bisect_right(xp, x)
        t = (x - xp[i - 1]) / (xp[i] - xp[i - 1])
        return yp[i - 1] + t * (yp[i] - yp[i - 1])

    def geo_to_screen(lon, lat):
        plat = -lat
        c_px = interp(plat, POS_LATS, PXS)
        c_py = interp(plat, POS_LATS, PYS)
        c_lon = interp(plat, POS_LATS, LONS)

        # Proyección natural del ancho continental
        lon_diff = max(-3.5, min(3.5, lon - c_lon))
        px = c_px + lon_diff * 95.0
        py = c_py
        return px, py

    # Paleta monocromática elegante (escala de grises equilibrada con bordes blancos nítidos)
    BW_SHADES = {
        15: (45, 48, 55),    # XV Arica
        1:  (70, 75, 85),    # I Tarapacá
        2:  (90, 95, 105),   # II Antofagasta
        3:  (50, 54, 62),    # III Atacama
        4:  (75, 80, 90),    # IV Coquimbo
        5:  (100, 105, 115), # V Valparaíso
        13: (45, 48, 55),    # RM Santiago
        6:  (72, 77, 86),    # VI O'Higgins
        7:  (55, 60, 68),    # VII Maule
        16: (85, 90, 100),   # XVI Ñuble
        8:  (60, 65, 75),    # VIII Biobío
        9:  (90, 96, 106),   # IX Araucanía
        14: (50, 54, 62),    # XIV Los Ríos
        10: (78, 83, 92),    # X Los Lagos
        11: (60, 65, 74),    # XI Aysén
        12: (92, 98, 108),   # XII Magallanes
    }

    map_img = Image.new("RGBA", (4096, 4096), (0, 0, 0, 0))
    draw = ImageDraw.Draw(map_img)

    for feat in gj['features']:
        cod = int(feat['properties']['codregion'])
        color = BW_SHADES.get(cod, (70, 75, 85))
        geom = feat['geometry']
        rings = []

        min_len = 40 if cod in [11, 12] else 4

        if geom['type'] == 'Polygon':
            for ring in geom['coordinates']:
                if len(ring) >= min_len:
                    pts = [geo_to_screen(p[0], p[1]) for p in ring if p[0] > -76.0]
                    if len(pts) >= 3:
                        rings.append(pts)
        elif geom['type'] == 'MultiPolygon':
            for poly in geom['coordinates']:
                for ring in poly:
                    if len(ring) >= min_len:
                        pts = [geo_to_screen(p[0], p[1]) for p in ring if p[0] > -76.0]
                        if len(pts) >= 3:
                            rings.append(pts)

        for ring in rings:
            draw.polygon(ring, fill=(*color, 255), outline=(255, 255, 255, 255), width=2)

    # Recuadro inferior izquierdo: Territorio Chileno Antártico
    abox = [(1450, 2680), (1850, 2980)]
    draw.rectangle(abox, fill=(30, 33, 40, 240), outline=(220, 225, 235, 255), width=2)
    try:
        font_sm = ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", 20)
    except Exception:
        font_sm = ImageFont.load_default()

    draw.text((1465, 2695), "TERRITORIO CHILENO ANTÁRTICO", font=font_sm, fill=(240, 240, 245, 255))
    ant_poly = [(1530, 2950), (1550, 2810), (1610, 2750), (1660, 2840), (1600, 2950)]
    draw.polygon(ant_poly, fill=(80, 85, 95, 255), outline=(255, 255, 255, 255), width=2)

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

    # Configuración de def/map_data.sii centrada en la espina de Chile
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

	# Niveles de Zoom completos
	zoom_uplift[0]: 50.0
	zoom_uplift[1]: 220.0
	zoom_uplift[2]: 900.0
	zoom_uplift[3]: 4000.0
	zoom_uplift[4]: 1000.0
	zoom_uplift[5]: 5000.0
	zoom_uplift[6]: 18500.0
	zoom_uplift[7]: 70000.0

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

	camera_limits_min[0]: (-1000000.0, -1000000.0)
	camera_limits_min[1]: (-1000000.0, -1000000.0)
	camera_limits_min[2]: (-1000000.0, -1000000.0)
	camera_limits_min[3]: (-1000000.0, -1000000.0)
	camera_limits_min[4]: (-95000.0, -140000.0)
	camera_limits_min[5]: (-95000.0, -140000.0)
	camera_limits_min[6]: (-95000.0, -140000.0)
	camera_limits_min[7]: (-95000.0, -150000.0)

	camera_limits_max[0]: (1000000.0, 1000000.0)
	camera_limits_max[1]: (1000000.0, 1000000.0)
	camera_limits_max[2]: (1000000.0, 1000000.0)
	camera_limits_max[3]: (1000000.0, 1000000.0)
	camera_limits_max[4]: (80000.0, 90000.0)
	camera_limits_max[5]: (80000.0, 90000.0)
	camera_limits_max[6]: (80000.0, 90000.0)
	camera_limits_max[7]: (80000.0, 90000.0)

	map_items_flags[0]: 0x685FFF
	map_items_flags[1]: 0x685FFF
	map_items_flags[2]: 0x685F7F
	map_items_flags[3]: 0x685F7F
	map_items_flags[4]: 0x685FAF
	map_items_flags[5]: 0x685F27
	map_items_flags[6]: 0x685407
	map_items_flags[7]: 0x481402

	map_3d_camera_pitch: 40.0

	# Centro del mapa UI y dimensiones de proyección estándar ETS2
	ui_map_center:	(-13500.0, -4950.0)
	ui_map_size:	(5308.2, 5200.0)

	ui_map_camera_min: (-95000.0, -150000.0)
	ui_map_camera_max: (80000.0, 90000.0)
	ui_map_camera_start: (-32000.0, -18000.0)

	ui_map_always_draw_city: true

	navigation_city_penalty: 1.0
	navigation_slow_road_penalty: 5.0
	navigation_maximum_speed: 30.6
}
}
"""
    with open(map_data_sii, "w", encoding="utf-8") as f:
        f.write(map_data_content)

    print(" -> Mapa de fondo blanco y negro (map0..map3, map) y def/map_data.sii generados exitosamente.")


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
