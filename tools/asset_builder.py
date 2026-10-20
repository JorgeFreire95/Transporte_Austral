#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
==============================================================================
TRANSPORTE AUSTRAL - CONVERSOR DE ACTIVOS UI, MAPA Y PANTALLAS DE CARGA (ETS2)
==============================================================================
Genera las texturas DDS, descriptores TOBJ binarios, materiales MAT y definiciones
SII para:
1. Pantallas de carga personalizadas usando mod_icon.png.
2. Mapa de fondo de Chile en la interfaz UI (selección de ciudad y mapa M).
"""

import os
import struct
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

BASE_DIR = Path(__file__).resolve().parent.parent


def write_tobj(file_path: Path, texture_rel_path: str, clamp: bool = True):
    """
    Escribe un archivo binario .tobj nativo de SCS Software (formato 0x70b10a01).
    Header exacto de 40 bytes + string UTF-8 precedido por longitud de 8 bytes (uint64 little-endian).
    """
    file_path.parent.mkdir(parents=True, exist_ok=True)

    # Normalizar separadores de ruta a '/'
    norm_path = texture_rel_path.replace("\\", "/")
    if not norm_path.startswith("/"):
        norm_path = "/" + norm_path

    path_bytes = norm_path.encode("utf-8")
    path_len = len(path_bytes)

    addr = 0x01 if clamp else 0x00
    # Header de 40 bytes verificado de assets nativos de ETS2:
    header_bytes = bytes([
        0x01, 0x0A, 0xB1, 0x70,  # 0..3: magic version 0x70b10a01
        0x00, 0x00, 0x00, 0x00,  # 4..7
        0x00, 0x00, 0x00, 0x00,  # 8..11
        0x00, 0x00, 0x00, 0x00,  # 12..15
        0x00, 0x00, 0x00, 0x00,  # 16..19
        0x01, 0x00, 0x00, 0x00,  # 20..23: uint32 1
        0x02, 0x00,              # 24..25: uint16 2 (Map2D)
        0x03, 0x03, 0x03, 0x00,  # 26..29: filters (mag, min, mip, bias)
        addr, addr,              # 30..31: clamp/repeat (addr_u, addr_v)
        0x00, 0x00, 0x00, 0x00,  # 32..35: flags
        0x00, 0x01, 0x00, 0x00   # 36..39: color_space
    ])

    with open(file_path, "wb") as f:
        f.write(header_bytes)
        f.write(struct.pack("<Q", path_len))
        f.write(path_bytes)


def write_mat(file_path: Path, tobj_rel_path: str):
    """Escribe un archivo de material UI de texto plano para ETS2."""
    file_path.parent.mkdir(parents=True, exist_ok=True)
    norm_path = tobj_rel_path.replace("\\", "/")
    content = f"""material : "ui"
{{
    texture : "{norm_path}"
    texture_name : "texture"
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
    # Tamaño recomendado para bar_pics: 1920x680 o 1920x1080
    bar_img = img.resize((1920, 680), Image.Resampling.LANCZOS)
    bar_dir = BASE_DIR / "material" / "ui" / "loading" / "bar_pics"
    bar_dir.mkdir(parents=True, exist_ok=True)

    dds_bar = bar_dir / "chile_01.dds"
    bar_img.save(dds_bar, format="DDS")

    tobj_bar = bar_dir / "chile_01.tobj"
    write_tobj(tobj_bar, "/material/ui/loading/bar_pics/chile_01.dds")

    mat_bar = bar_dir / "chile_01.mat"
    write_mat(mat_bar, "/material/ui/loading/bar_pics/chile_01.tobj")

    # Definición .sii para bar_pics
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
        full_img.save(dds_full, format="DDS")

        tobj_full = loading_dir / f"{name}.tobj"
        write_tobj(tobj_full, f"/material/ui/loading/{name}.dds")

        mat_full = loading_dir / f"{name}.mat"
        write_mat(mat_full, f"/material/ui/loading/{name}.tobj")

    print(" -> Pantallas de carga generadas con éxito en material/ui/loading/")


def comprimir_mod_icon():
    """Comprime mod_icon.jpg a 512x512 JPEG calidad 85 para cumplir con el límite estricto de 128 KB de SCS."""
    src = BASE_DIR / "mod_icon.png"
    if not src.exists():
        src = BASE_DIR / "mod_icon.jpg"
    if src.exists():
        im = Image.open(src).convert("RGB")
        im_resized = im.resize((512, 512), Image.Resampling.LANCZOS)
        dst = BASE_DIR / "mod_icon.jpg"
        im_resized.save(dst, format="JPEG", quality=85)
        print(f" -> Icono del mod optimizado: {dst.stat().st_size} bytes (límite SCS: 131072 bytes)")


def generar_mapa_fondo_chile():
    """Genera la textura de mapa de fondo de Chile en alta resolución (4096x4096) dividida en 4 cuadrantes (map0..map3) y map.dds para el UI."""
    print("[2/2] Generando mapa de fondo de Chile para la interfaz UI con 16 regiones coloreadas...")

    # Crear imagen de fondo estilizada de Chile y Océano Pacífico (4096x4096)
    w, h = 4096, 4096
    # Coordenadas mundiales cubiertas por la textura (ui_map_size = 70000x110000 centrado en -28000, -12000)
    x_min, x_max = -63000.0, 7000.0
    z_min, z_max = -67000.0, 43000.0

    def world_to_px(wx, wz):
        px = int((wx - x_min) / (x_max - x_min) * w)
        pz = int((wz - z_min) / (z_max - z_min) * h)
        return (px, pz)

    # Color base: Azul marino profundo cartográfico moderno
    map_img = Image.new("RGBA", (w, h), (18, 24, 38, 255))
    draw = ImageDraw.Draw(map_img)

    # Cuadrícula cartográfica sutil
    for x in range(0, w, 256):
        draw.line([(x, 0), (x, h)], fill=(28, 38, 58, 120), width=1)
    for y in range(0, h, 256):
        draw.line([(0, y), (w, y)], fill=(28, 38, 58, 120), width=1)

    # 17 Divisores limítrofes continuos para generar la franja esbelta y sin escalonamientos de Chile
    dividers = [
        ((-45000, -59000), (-32000, -59000)),  # 0: Límite Norte Arica (Perú)
        ((-49000, -51000), (-34000, -51000)),  # 1: Arica / Tarapacá
        ((-48000, -43000), (-34000, -43000)),  # 2: Tarapacá / Antofagasta
        ((-44000, -33000), (-32000, -33000)),  # 3: Antofagasta / Atacama
        ((-42000, -21500), (-30000, -21500)),  # 4: Atacama / Coquimbo
        ((-40000, -15200), (-28000, -15200)),  # 5: Coquimbo / Valparaíso
        ((-37000,  -9500), (-25000,  -9500)),  # 6: Valparaíso / RM
        ((-33000,  -3500), (-22000,  -3500)),  # 7: RM / O'Higgins
        ((-28000,    500), (-15000,    500)),  # 8: O'Higgins / Maule
        ((-23000,   5400), (-10000,   5400)),  # 9: Maule / Ñuble
        ((-20000,   9500), ( -7000,   9500)),  # 10: Ñuble / Biobío
        ((-17000,  15000), ( -4000,  15000)),  # 11: Biobío / La Araucanía
        ((-18000,  19200), ( -5000,  19200)),  # 12: La Araucanía / Los Ríos
        ((-21000,  22100), ( -7000,  22100)),  # 13: Los Ríos / Los Lagos
        ((-26000,  25000), (-12000,  25000)),  # 14: Los Lagos / Aysén
        ((-27000,  28500), (-13000,  28500)),  # 15: Aysén / Magallanes
        ((-21000,  36000), ( -6000,  36000)),  # 16: Cabo de Hornos (Límite Sur)
    ]

    # Paleta de 16 colores idéntica a la infografía oficial regional de Chile
    colors = [
        (140, 45, 71),   # XV Región de Arica y Parinacota (#8C2D47)
        (230, 96, 77),   # I Región de Tarapacá (#E6604D)
        (245, 166, 56),  # II Región de Antofagasta (#F5A638)
        (242, 200, 75),  # III Región de Atacama (#F2C84B)
        (215, 223, 101), # IV Región de Coquimbo (#D7DF65)
        (145, 191, 72),  # V Región de Valparaíso (#91BF48)
        (156, 43, 89),   # RM Región Metropolitana de Santiago (#9C2B59)
        (240, 162, 60),  # VI Región de O'Higgins (#F0A23C)
        (155, 198, 112), # VII Región del Maule (#9BC670)
        (148, 43, 67),   # XVI Región de Ñuble (#942B43)
        (236, 165, 106), # VIII Región del Biobío (#ECA56A)
        (227, 232, 138), # IX Región de La Araucanía (#E3E88A)
        (128, 187, 73),  # XIV Región de Los Ríos (#80BB49)
        (132, 186, 80),  # X Región de Los Lagos (#84BA50)
        (139, 46, 87),   # XI Región de Aysén (#8B2E57)
        (134, 35, 67),   # XII Región de Magallanes (#862343)
    ]

    reg_names = [
        "XV Región de Arica y Parinacota",
        "I Región de Tarapacá",
        "II Región de Antofagasta",
        "III Región de Atacama",
        "IV Región de Coquimbo",
        "V Región de Valparaíso",
        "RM Región Metropolitana de Santiago",
        "VI Región del Libertador Bernardo O'Higgins",
        "VII Región del Maule",
        "XVI Región de Ñuble",
        "VIII Región del Bío- Bío",
        "IX Región de La Araucanía",
        "XIV Región de Los Ríos",
        "X Región de Los Lagos",
        "XI Región de Aysén del General Ibáñez del Campo",
        "XII Región de Magallanes y Antártica Chilena"
    ]

    cap_pos = [
        (-38999, -54871), (-44882, -46900), (-39807, -38549), (-36466, -26835),
        (-36768, -16268), (-31578, -14044), (-30174,  -4751), (-26395,  -2170),
        (-16450,   3310), (-16230,   7437), (-11085,  11548), ( -9769,  18357),
        (-12794,  20153), (-17861,  24140), (-22265,  25768), (-13182,  31278)
    ]

    # 1. Dibujar resplandor costero tenue y sombra
    for i in range(16):
        top_w, top_e = dividers[i]
        bot_w, bot_e = dividers[i+1]
        px_poly = [world_to_px(*pt) for pt in [top_w, top_e, bot_e, bot_w]]
        c = colors[i]
        shadow_poly = [(p[0]+4, p[1]+4) for p in px_poly]
        draw.polygon(shadow_poly, fill=(10, 14, 22, 160))
        draw.polygon(px_poly, fill=(c[0]//3, c[1]//3, c[2]//3, 100), outline=(c[0]//2, c[1]//2, c[2]//2, 140))

    # 2. Dibujar polígonos de las 16 regiones con contorno blanco nítido
    for i in range(16):
        top_w, top_e = dividers[i]
        bot_w, bot_e = dividers[i+1]
        px_poly = [world_to_px(*pt) for pt in [top_w, top_e, bot_e, bot_w]]
        c = colors[i]
        draw.polygon(px_poly, fill=(*c, 255), outline=(255, 255, 255, 240), width=4)

    # Tipografía del sistema para textos cartográficos
    try:
        font = ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", 32)
        font_bold = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 46)
        font_sub = ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", 24)
    except:
        font = ImageFont.load_default()
        font_bold = font
        font_sub = font

    # Título oficial de Chile en la esquina superior derecha
    draw.text((2550, 150), "REPÚBLICA DE CHILE", font=font_bold, fill=(245, 248, 255, 255))
    draw.text((2550, 215), "TRANSPORTE AUSTRAL - RED VIAL 1:19", font=font_sub, fill=(245, 166, 56, 255))
    draw.text((2550, 250), "16 Regiones Político-Administrativas Conectadas", font=font_sub, fill=(160, 185, 215, 220))

    # Océano Pacífico (lado izquierdo)
    draw.text((200, 2000), "OCÉANO PACÍFICO", font=font_bold, fill=(35, 55, 85, 180))

    # Territorio Chileno Antártico (recuadro inferior izquierdo)
    abox = [(200, 3250), (1050, 3950)]
    draw.rectangle(abox, fill=(15, 20, 32, 230), outline=(80, 110, 150, 200), width=2)
    draw.text((220, 3270), "TERRITORIO CHILENO ANTÁRTICO", font=font_sub, fill=(220, 230, 245, 220))
    draw.polygon([(400, 3850), (600, 3380), (800, 3850)], fill=(134, 35, 67, 255), outline=(255, 255, 255, 220), width=2)

    # 3. Dibujar círculos blancos y líneas guía a los títulos de las 16 regiones
    y_start = 450
    y_end = 3680
    y_step = (y_end - y_start) / 15.0

    for i in range(16):
        cx, cz = cap_pos[i]
        px, pz = world_to_px(cx, cz)
        target_y = int(y_start + i * y_step)

        # Círculo blanco selector con núcleo del color regional
        r = 18
        draw.ellipse([(px-r, pz-r), (px+r, pz+r)], fill=(255, 255, 255, 255), outline=(60, 60, 60, 255), width=3)
        draw.ellipse([(px-6, pz-6), (px+6, pz+6)], fill=(colors[i]), outline=None)

        # Línea guía estilizada hacia la derecha
        lx1 = px + r + 10
        lx2 = max(lx1 + 60, 2750)
        lx3 = 3050
        lx_end = 3100
        draw.line([(lx1, pz), (lx2, pz), (lx3, target_y), (lx_end, target_y)], fill=(180, 195, 220, 220), width=2)
        draw.ellipse([(lx_end-4, target_y-4), (lx_end+4, target_y+4)], fill=(255, 255, 255, 255))

        # Texto de la región con sombra sutil
        draw.text((lx_end + 18, target_y - 20), reg_names[i], font=font, fill=(10, 14, 22, 220))
        draw.text((lx_end + 16, target_y - 22), reg_names[i], font=font, fill=(245, 248, 255, 255))

    map_ui_dir = BASE_DIR / "material" / "ui" / "map"
    map_ui_dir.mkdir(parents=True, exist_ok=True)

    # 4. Generar y guardar las 4 texturas de cuadrante (map0..map3) de 2048x2048 cada una
    # Cuadrante 0: NW (0..2048, 0..2048)
    # Cuadrante 1: NE (2048..4096, 0..2048)
    # Cuadrante 2: SW (0..2048, 2048..4096)
    # Cuadrante 3: SE (2048..4096, 2048..4096)
    quadrants = [
        ("map0", (0, 0, 2048, 2048)),
        ("map1", (2048, 0, 4096, 2048)),
        ("map2", (0, 2048, 2048, 4096)),
        ("map3", (2048, 2048, 4096, 4096)),
    ]

    for qname, box in quadrants:
        tile = map_img.crop(box)
        tile_dds = map_ui_dir / f"{qname}.dds"
        tile.save(tile_dds, format="DDS")

        tile_tobj = map_ui_dir / f"{qname}.tobj"
        write_tobj(tile_tobj, f"/material/ui/map/{qname}.dds")

        tile_mat = map_ui_dir / f"{qname}.mat"
        write_mat(tile_mat, f"/material/ui/map/{qname}.tobj")

        # Aliases con guion bajo (map_0..map_3) por compatibilidad
        alias_name = f"map_{qname[-1]}"
        write_mat(map_ui_dir / f"{alias_name}.mat", f"/material/ui/map/{qname}.tobj")

    # 5. Generar textura general de resumen (map.dds) de 2048x2048
    overview_img = map_img.resize((2048, 2048), Image.Resampling.LANCZOS)
    dds_map = map_ui_dir / "map.dds"
    overview_img.save(dds_map, format="DDS")

    tobj_map = map_ui_dir / "map.tobj"
    write_tobj(tobj_map, "/material/ui/map/map.dds")

    mat_map = map_ui_dir / "map.mat"
    write_mat(mat_map, "/material/ui/map/map.tobj")

    # 6. Escribir def/map_data.sii calibrado exactamente a las coordenadas de Chile
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
	zoom_uplift[5]: 5000.0
	zoom_uplift[6]: 20000.0
	zoom_uplift[7]: 75000.0

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
	icon_size[2]: (10.0, 10.0)
	icon_size[3]: (8.0, 8.0)
	icon_size[4]: (15.0, 15.0)
	icon_size[5]: (12.0, 12.0)
	icon_size[6]: (10.0, 10.0)
	icon_size[7]: (10.0, 10.0)

	city_icon_size[0]: (13.0, 13.0)
	city_icon_size[1]: (10.0, 10.0)
	city_icon_size[2]: (10.0, 10.0)
	city_icon_size[3]: (8.0, 8.0)
	city_icon_size[4]: (15.0, 15.0)
	city_icon_size[5]: (12.0, 12.0)
	city_icon_size[6]: (10.0, 10.0)
	city_icon_size[7]: (15.0, 15.0)

	company_icon_size[0]: (32.0, 8.0)
	company_icon_size[1]: (20.0, 5.0)
	company_icon_size[2]: (0.0, 0.0)
	company_icon_size[3]: (0.0, 0.0)
	company_icon_size[4]: (60.0, 15.0)
	company_icon_size[5]: (40.0, 10.0)
	company_icon_size[6]: (16.0, 4.0)
	company_icon_size[7]: (16.0, 4.0)

	# Límites de cámara en coordenadas de Chile
	camera_limits_min[0]: (-65000.0, -70000.0)
	camera_limits_min[1]: (-65000.0, -70000.0)
	camera_limits_min[2]: (-65000.0, -70000.0)
	camera_limits_min[3]: (-65000.0, -70000.0)
	camera_limits_min[4]: (-65000.0, -70000.0)
	camera_limits_min[5]: (-65000.0, -70000.0)
	camera_limits_min[6]: (-65000.0, -70000.0)
	camera_limits_min[7]: (-65000.0, -70000.0)

	camera_limits_max[0]: (15000.0, 48000.0)
	camera_limits_max[1]: (15000.0, 48000.0)
	camera_limits_max[2]: (15000.0, 48000.0)
	camera_limits_max[3]: (15000.0, 48000.0)
	camera_limits_max[4]: (15000.0, 48000.0)
	camera_limits_max[5]: (15000.0, 48000.0)
	camera_limits_max[6]: (15000.0, 48000.0)
	camera_limits_max[7]: (15000.0, 48000.0)

	map_items_flags[0]: 0x0F685FFF
	map_items_flags[1]: 0x0F685FFF
	map_items_flags[2]: 0x0F685FFF
	map_items_flags[3]: 0x0F685FFF
	map_items_flags[4]: 0x0F685FAF
	map_items_flags[5]: 0x0F685FAF
	map_items_flags[6]: 0x0F685487
	map_items_flags[7]: 0x0C481402

	map_3d_camera_pitch: 40.0

	# Centro del mapa UI en coordenadas de Chile
	ui_map_center:	(-28000.0, -12000.0)
	ui_map_size:	(70000.0, 110000.0)

	ui_map_camera_min: (-65000.0, -70000.0)
	ui_map_camera_max: (15000.0, 48000.0)
	ui_map_camera_start: (-28000.0, -12000.0)

	ui_map_always_draw_city: true

	navigation_city_penalty: 1.0
	navigation_slow_road_penalty: 5.0
	navigation_maximum_speed: 30.6
}
}
"""
    with open(map_data_sii, "w", encoding="utf-8") as f:
        f.write(map_data_content)

    print(" -> Mapa de fondo (map0..map3, map) y def/map_data.sii generados exitosamente.")


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

