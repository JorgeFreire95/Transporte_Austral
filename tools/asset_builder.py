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


def write_tobj(file_path: Path, texture_rel_path: str):
    """
    Escribe un archivo binario .tobj de SCS Software (formato 0x70b10a01).
    texture_rel_path: Ruta virtual en el juego (ej: "/material/ui/loading/bar_pics/chile_01.dds")
    """
    file_path.parent.mkdir(parents=True, exist_ok=True)

    supported_version = 0x70b10a01
    unknown0 = 0
    unknown1 = 0
    unknown2 = 0
    unknown3 = 0
    unknown4 = 1  # ushort
    bias = 0      # byte
    unknown5 = 0  # byte
    tobj_type = 2 # Map2D = 2
    unknown6 = 0  # byte
    mag_filter = 3 # Default = 3
    min_filter = 3 # Default = 3
    mip_filter = 3 # Default = 3
    unknown7 = 0  # byte
    addr_u = 1    # Clamp = 1
    addr_v = 1    # Clamp = 1
    addr_w = 1    # Clamp = 1
    compress = 1  # byte
    unknown8 = 0  # byte
    anisotropic = 1 # byte
    unknown9 = 0  # byte
    unknown10 = 1 # byte
    color_space = 0 # Srgb = 0
    unknown11 = 0 # byte

    # Normalizar separadores de ruta a '/'
    norm_path = texture_rel_path.replace("\\", "/")
    if not norm_path.startswith("/"):
        norm_path = "/" + norm_path

    path_bytes = norm_path.encode("utf-8")
    path_len = len(path_bytes)

    # Header 40 bytes + string pascal (8 bytes len + bytes)
    header_bytes = struct.pack(
        "<IIIIHBBBBBBBBBBBBBBBBBBB",
        supported_version,
        unknown0, unknown1, unknown2, unknown3,
        unknown4,
        bias,
        unknown5,
        tobj_type,
        unknown6,
        mag_filter,
        min_filter,
        mip_filter,
        unknown7,
        addr_u,
        addr_v,
        addr_w,
        compress,
        unknown8,
        anisotropic,
        unknown9,
        unknown10,
        color_space,
        unknown11
    )

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

    # Crear imagen de fondo estilizada de Chile y Océano Pacífico (2048x4096 o 2048x2048)
    # Fondo azul marino océano, silueta estilizada de Chile con relieve y coordenadas
    w, h = 2048, 2048
    map_img = Image.new("RGBA", (w, h), (18, 28, 45, 255)) # Azul océano oscuro moderno
    draw = ImageDraw.Draw(map_img)

    # Dibujar líneas de cuadrícula cartográfica (latitud / longitud tenue)
    for x in range(0, w, 128):
        draw.line([(x, 0), (x, h)], fill=(28, 42, 65, 120), width=1)
    for y in range(0, h, 128):
        draw.line([(0, y), (w, y)], fill=(28, 42, 65, 120), width=1)

    # Dibujar silueta estilizada de Chile
    # Chile es una franja angosta de norte a sur
    chile_puntos = [
        # Norte (Arica - Antofagasta)
        (1020, 100), (1050, 120), (1080, 220), (1060, 400),
        # Norte Chico (Atacama - Coquimbo)
        (1040, 600), (1010, 800), (990, 950),
        # Zona Central (Valparaíso - Santiago - Maule)
        (980, 1050), (1020, 1150), (1000, 1250),
        # Zona Sur (Biobío - Araucanía - Los Lagos - Chiloé)
        (960, 1350), (970, 1450), (950, 1550), (930, 1620),
        # Patagonia / Aysén / Magallanes
        (960, 1720), (940, 1800), (1020, 1920), (1000, 1960),
        # Borde oriental cordillerano
        (1070, 1900), (1010, 1750), (1020, 1600), (1030, 1450),
        (1060, 1250), (1060, 1050), (1070, 850), (1110, 600),
        (1130, 350), (1100, 150)
    ]

    # Relleno del territorio de Chile (Tierra / Relieve andino verdoso-marrón)
    draw.polygon(chile_puntos, fill=(55, 75, 55, 255), outline=(90, 130, 90, 255))

    # Océano Pacífico (texto estilizado)
    draw.text((300, 1000), "OCÉANO PACÍFICO", fill=(45, 70, 105, 180))
    draw.text((1200, 1000), "REPÚBLICA DE CHILE", fill=(180, 190, 200, 220))
    draw.text((1200, 1030), "TRANSPORTE AUSTRAL", fill=(220, 80, 60, 240))

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

    # Configuración de def/map_data.sii para centrar y dimensionar el mapa sobre Chile
    def_dir = BASE_DIR / "def"
    def_dir.mkdir(parents=True, exist_ok=True)

    map_data_sii = def_dir / "map_data.sii"
    map_data_content = """SiiNunit
{
map_data : .map.data {
    # Paleta de colores de caminos en la interfaz
    road_color: 0xFF555555
    road_discovered_color: 0xFF00D7FF
    job_road_color: 0xFF00FF88
    world_road_color: 0xFF444444

    # Centro de la vista de mapa UI enfocado en la Zona Central de Chile (Santiago)
    ui_map_center: (-2000.0, 20000.0)
    ui_map_size: (120000.0, 250000.0)

    # Límites de cámara de paneo en todos los niveles de zoom (evita que se desplace a Europa)
    camera_limits_min[0]: (-250000.0, -150000.0)
    camera_limits_max[0]: (250000.0, 300000.0)
    camera_limits_min[1]: (-250000.0, -150000.0)
    camera_limits_max[1]: (250000.0, 300000.0)
    camera_limits_min[2]: (-250000.0, -150000.0)
    camera_limits_max[2]: (250000.0, 300000.0)
    camera_limits_min[3]: (-250000.0, -150000.0)
    camera_limits_max[3]: (250000.0, 300000.0)
    camera_limits_min[4]: (-250000.0, -150000.0)
    camera_limits_max[4]: (250000.0, 300000.0)
    camera_limits_min[5]: (-250000.0, -150000.0)
    camera_limits_max[5]: (250000.0, 300000.0)
    camera_limits_min[6]: (-250000.0, -150000.0)
    camera_limits_max[6]: (250000.0, 300000.0)
    camera_limits_min[7]: (-250000.0, -150000.0)
    camera_limits_max[7]: (250000.0, 300000.0)

    # Coordenadas de zoom
    ui_map_camera_min: 15.0
    ui_map_camera_max: 200.0
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
