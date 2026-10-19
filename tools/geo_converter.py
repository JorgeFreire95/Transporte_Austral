#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
==============================================================================
TRANSPORTE AUSTRAL - CONVERSOR GEOGRÁFICO A COORDENADAS ETS2 (CHILE)
==============================================================================
Convierte coordenadas GPS reales (Latitud, Longitud WGS84) de Chile a:
1. Coordenadas del motor Prism3D de Euro Truck Simulator 2 (X, Y, Z).
2. Identificador de sector del SCS Map Editor (ej: sec-0030+0045.base).
3. Soporta escala estándar SCS (1:19) y escala 1:3 para mapas detallados.
"""

import math
import sys

# Parámetros de proyección para Chile
# Centro de referencia: Santiago de Chile (-33.4489, -70.6693)
REF_LAT = -33.4489
REF_LON = -70.6693

# Radio medio de la Tierra en metros
EARTH_RADIUS = 6371000.0

# Tamaño de un sector en el motor Prism3D (en unidades de juego, aprox. 4000 unidades)
SECTOR_SIZE = 4000.0

# Escalas comunes en ETS2
ESCALA_MAPA_ETS2 = 19.0  # 1:19 (Escala Europa / Continente)
ESCALA_STANDALONE = 3.0  # 1:3 (Escala 1:3 para mayor detalle de comunas)

# Base de datos de coordenadas reales de puntos clave en Chile
PUNTOS_CHILE_GPS = {
    # Norte Grande
    "Arica (El Morro)": (-18.4783, -70.3126),
    "Putre (Paso Chungará)": (-18.1964, -69.5594),
    "Iquique (Cerro Dragón)": (-20.2133, -70.1503),
    "Pozo Almonte (Humberstone)": (-20.2589, -69.7942),
    "Antofagasta (La Portada)": (-23.6509, -70.3975),
    "Calama (Chuquicamata)": (-22.4544, -68.9294),
    "San Pedro de Atacama": (-22.9087, -68.1997),
    "Mejillones": (-23.1044, -70.4503),

    # Norte Chico
    "Copiapó": (-27.3668, -70.3323),
    "Bahía Inglesa": (-27.1083, -70.8667),
    "Vallenar": (-28.5756, -70.7581),
    "La Serena (El Faro)": (-29.9027, -71.2519),
    "Coquimbo (Cruz Tercer Milenio)": (-29.9533, -71.3436),
    "Ovalle": (-30.5983, -71.2003),
    "Los Vilos": (-31.9133, -71.5147),

    # Zona Central
    "Valparaíso (Puerto)": (-33.0472, -71.6127),
    "Viña del Mar (Reloj de Flores)": (-33.0245, -71.5518),
    "San Antonio (STI)": (-33.5933, -71.6167),
    "Los Andes (Paso Los Libertadores)": (-32.8339, -70.5983),
    "Santiago (Costanera Center)": (-33.4172, -70.6067),
    "San Bernardo (Hub Logístico Sur)": (-33.5922, -70.7044),
    "Rancagua (El Teniente)": (-34.1708, -70.7444),
    "San Fernando": (-34.5842, -70.9889),
    "Talca": (-35.4264, -71.6554),
    "Constitución": (-35.3333, -72.4167),
    "Curicó": (-34.9856, -71.2394),
    "Chillán (Mercado Central)": (-36.6067, -72.1033),

    # Zona Sur
    "Concepción (Puente Biobío)": (-36.8270, -73.0503),
    "Talcahuano (Huáscar)": (-36.7167, -73.1167),
    "Los Ángeles": (-37.4697, -72.3536),
    "Temuco (Cerro Ñielol)": (-38.7359, -72.5904),
    "Villarrica (Lago)": (-39.2789, -72.2272),
    "Valdivia (Río Calle-Calle)": (-39.8142, -73.2459),
    "La Unión (Colun)": (-40.2933, -73.0817),
    "Osorno": (-40.5739, -73.1344),
    "Puerto Montt (Hito Carretera Austral)": (-41.4693, -72.9424),
    "Ancud (Chiloé)": (-41.8683, -73.8267),
    "Castro (Palafitos Gamboa)": (-42.4828, -73.7731),
    "Quellón (Hito Cero Panamericana)": (-43.1167, -73.6167),
    "Chaitén": (-42.9167, -72.7000),

    # Zona Austral (Patagonia)
    "Coyhaique": (-45.5712, -72.0685),
    "Puerto Aysén": (-45.4056, -72.6944),
    "Puerto Chacabuco": (-45.4667, -72.8167),
    "Cochrane": (-47.2547, -72.5694),
    "Villa O'Higgins (Fin Ruta 7)": (-48.4667, -72.5667),
    "Puerto Natales (Torres del Paine)": (-51.7269, -72.5069),
    "Punta Arenas (Estrecho Magallanes)": (-53.1638, -70.9171),
    "Porvenir (Tierra del Fuego)": (-53.2958, -70.3683)
}


def gps_to_ets2(lat: float, lon: float, scale: float = ESCALA_MAPA_ETS2):
    """
    Convierte Lat/Lon (WGS84) a coordenadas SCS (X, Z) centradas en Santiago.
    - X representa el eje Este-Oeste (Longitud).
    - Z representa el eje Norte-Sur (Latitud invertida: Sur es Z positivo en ETS2).
    """
    # Diferencia en radianes
    d_lat = math.radians(lat - REF_LAT)
    d_lon = math.radians(lon - REF_LON)

    # Distancia en metros usando proyección equidistante cilíndrica local
    lat_rad = math.radians((lat + REF_LAT) / 2.0)
    delta_x_metros = EARTH_RADIUS * d_lon * math.cos(lat_rad)
    delta_z_metros = -EARTH_RADIUS * d_lat  # Hacia el norte es latitud creciente, pero en ETS2 norte es -Z

    # Aplicar factor de escala del juego
    game_x = delta_x_metros / scale
    game_z = delta_z_metros / scale

    # Calcular número de sector (cada sector mide SECTOR_SIZE unidades de juego)
    sector_x = int(math.floor(game_x / SECTOR_SIZE))
    sector_z = int(math.floor(game_z / SECTOR_SIZE))

    sector_name = f"sec{sector_x:+05d}{sector_z:+05d}.base"

    return round(game_x, 2), round(game_z, 2), sector_name


def demo():
    print("=" * 80)
    print(" TRANSPORTE AUSTRAL - CONVERSIÓN DE PUNTOS ICÓNICOS DE CHILE A ETS2")
    print("=" * 80)
    print(f"{'Punto / Lugar Icónico':<38} | {'Coord. ETS2 (X, Z)':<20} | {'Sector SCS (.base)':<18}")
    print("-" * 80)

    for nombre, (lat, lon) in PUNTOS_CHILE_GPS.items():
        gx, gz, sec = gps_to_ets2(lat, lon, scale=ESCALA_MAPA_ETS2)
        coord_str = f"({gx:.0f}, {gz:.0f})"
        print(f"{nombre:<38} | {coord_str:<20} | {sec:<18}")

    print("=" * 80)
    print("Nota: En el SCS Map Editor, presione 'F5' o teclee 'c_goto <X> 100 <Z>'")
    print("en la consola del juego para teletransportar la cámara a cualquier ciudad.")


if __name__ == "__main__":
    if len(sys.argv) == 3:
        try:
            in_lat = float(sys.argv[1])
            in_lon = float(sys.argv[2])
            x, z, s = gps_to_ets2(in_lat, in_lon)
            print(f"Lat: {in_lat}, Lon: {in_lon} -> ETS2 X: {x}, Z: {z} -> Sector: {s}")
        except ValueError:
            print("Uso: python geo_converter.py <latitud> <longitud>")
    else:
        demo()
