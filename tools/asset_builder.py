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


def generar_mapa_fondo_chile():
    """Genera la textura de mapa de fondo de Chile para el UI y el archivo def/map_data.sii"""
    print("[2/2] Generando mapa de fondo de Chile para la interfaz UI...")

    # Crear imagen de fondo estilizada de Chile y Océano Pacífico (2048x2048)
    w, h = 2048, 2048
    # Coordenadas mundiales cubiertas por la textura (ui_map_size = 150000x250000 centrado en -116500, 172500)
    x_min, x_max = -191500.0, -41500.0
    z_min, z_max = 47500.0, 297500.0

    def world_to_px(wx, wz):
        px = int((wx - x_min) / (x_max - x_min) * w)
        pz = int((wz - z_min) / (z_max - z_min) * h)
        return (px, pz)

    # Color base: Azul marino profundo moderno cartográfico
    map_img = Image.new("RGBA", (w, h), (14, 22, 38, 255))
    draw = ImageDraw.Draw(map_img)

    # Cuadrícula cartográfica sutil
    for x in range(0, w, 128):
        draw.line([(x, 0), (x, h)], fill=(24, 38, 60, 100), width=1)
    for y in range(0, h, 128):
        draw.line([(0, y), (w, y)], fill=(24, 38, 60, 100), width=1)

    # Puntos geográficos reales convertidos a coordenadas de textura
    # Territorio continental de Chile y relieve cordillerano
    chile_coords_world = [
        # Norte Grande (Límite con Perú - Arica)
        (-118200, 83000), (-116000, 83000), (-115000, 92000),
        # Antofagasta / Atacama cordillera
        (-113500, 101000), (-113000, 115000), (-114000, 130000),
        # Zona Central cordillera (San José de Maipo - Maule)
        (-114500, 148000), (-115000, 160000), (-115500, 172000),
        # Zona Sur cordillera (Araucanía - Los Lagos)
        (-115800, 185000), (-115500, 198000),
        # Patagonia Cordillera (Aysén / Campo de Hielo)
        (-115000, 215000), (-114500, 235000), (-114000, 250000),
        # Magallanes / Tierra del Fuego oriental
        (-112000, 260000), (-112500, 270000), (-114000, 272000),
        # Cabo de Hornos / Borde Sur
        (-115000, 275000), (-116500, 268000),
        # Magallanes costa occidental / Canales Patagónicos
        (-117500, 255000), (-117800, 240000), (-118200, 225000),
        # Golfo de Penas / Chiloé
        (-118500, 210000), (-118800, 202000), (-118500, 195000),
        # Costa Sur (Valdivia - Concepción)
        (-118200, 185000), (-118400, 170000),
        # Costa Central (San Antonio - Valparaíso - Coquimbo)
        (-117800, 155000), (-117600, 145000), (-117500, 130000),
        # Costa Norte Chico y Norte Grande (Copiapó - Antofagasta - Iquique - Arica)
        (-117300, 118000), (-118000, 105000), (-118300, 92000), (-118300, 85000)
    ]

    chile_poly_px = [world_to_px(wx, wz) for wx, wz in chile_coords_world]

    # Resplandor costero tenue
    for offset in range(8, 0, -2):
        draw.polygon(chile_poly_px, fill=(20, 45, 60, 60), outline=(28, 65, 85, 120))

    # Territorio continental (Relieve geográfico verde/oliva andino)
    draw.polygon(chile_poly_px, fill=(45, 68, 52, 255), outline=(85, 130, 95, 255))

    # Océano Pacífico (Anotación cartográfica estilizada)
    px_pac, pz_pac = world_to_px(-155000, 160000)
    draw.text((px_pac, pz_pac), "OCÉANO PACÍFICO", fill=(45, 75, 110, 200))

    # Título País y Mod
    px_title, pz_title = world_to_px(-100000, 145000)
    draw.text((px_title, pz_title), "REPÚBLICA DE CHILE", fill=(200, 215, 230, 230))
    draw.text((px_title, pz_title + 25), "TRANSPORTE AUSTRAL", fill=(225, 90, 70, 250))
    draw.text((px_title, pz_title + 45), "Mapa Independiente ETS2", fill=(130, 155, 175, 200))

    map_ui_dir = BASE_DIR / "material" / "ui" / "map"
    map_ui_dir.mkdir(parents=True, exist_ok=True)

    # Guardar map.dds
    dds_map = map_ui_dir / "map.dds"
    map_img.save(dds_map, format="DDS")

    # Guardar map.tobj
    tobj_map = map_ui_dir / "map.tobj"
    write_tobj(tobj_map, "/material/ui/map/map.dds")

    # Guardar map.mat
    mat_map = map_ui_dir / "map.mat"
    write_mat(mat_map, "/material/ui/map/map.tobj")

    # Escribir def/map_data.sii completo con todas las 8 capas de zoom y límites en Chile
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
	camera_limits_min[0]: (-500000.0, -100000.0)
	camera_limits_min[1]: (-500000.0, -100000.0)
	camera_limits_min[2]: (-500000.0, -100000.0)
	camera_limits_min[3]: (-500000.0, -100000.0)
	camera_limits_min[4]: (-300000.0, 0.0)
	camera_limits_min[5]: (-250000.0, 20000.0)
	camera_limits_min[6]: (-250000.0, 30000.0)
	camera_limits_min[7]: (-250000.0, 30000.0)

	camera_limits_max[0]: (200000.0, 400000.0)
	camera_limits_max[1]: (200000.0, 400000.0)
	camera_limits_max[2]: (200000.0, 400000.0)
	camera_limits_max[3]: (200000.0, 400000.0)
	camera_limits_max[4]: (50000.0, 350000.0)
	camera_limits_max[5]: (30000.0, 340000.0)
	camera_limits_max[6]: (20000.0, 320000.0)
	camera_limits_max[7]: (20000.0, 320000.0)

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
	ui_map_center:	(-116500.0, 172500.0)
	ui_map_size:	(150000.0, 250000.0)

	ui_map_camera_min: (-250000.0, 30000.0)
	ui_map_camera_max: (20000.0, 320000.0)
	ui_map_camera_start: (-116500.0, 172500.0)

	ui_map_always_draw_city: true

	navigation_city_penalty: 1.0
	navigation_slow_road_penalty: 5.0
	navigation_maximum_speed: 30.6
}
}
"""
    with open(map_data_sii, "w", encoding="utf-8") as f:
        f.write(map_data_content)

    print(" -> Mapa de fondo y def/map_data.sii generados exitosamente.")


def main():
    print("==================================================================")
    print(" TRANSPORTE AUSTRAL - CONSTRUCTOR DE ACTIVOS GRÁFICOS Y UI")
    print("==================================================================")
    generar_pantallas_de_carga()
    generar_mapa_fondo_chile()
    print("==================================================================")
    print("Activos generados. Listo para compilar con tools/build.py.")


if __name__ == "__main__":
    main()
