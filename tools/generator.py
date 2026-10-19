#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
==============================================================================
TRANSPORTE AUSTRAL - GENERADOR DE DEFINICIONES ETS2 (CHILE MAP MOD)
==============================================================================
Script en Python para generar automáticamente las definiciones de ciudades,
empresas, cargas, gasolineras y reglas de tráfico de Chile para Euro Truck Simulator 2.

Soporta las 16 regiones de Chile con sus comunas icónicas, empresas chilenas
y estaciones de servicio (Copec, Shell, Petrobras).
"""

import os
import sys
from pathlib import Path

# Directorio raíz del proyecto
BASE_DIR = Path(__file__).resolve().parent.parent
DEF_DIR = BASE_DIR / "def"

# ==============================================================================
# BASE DE DATOS: 16 REGIONES DE CHILE Y COMUNAS
# ==============================================================================
REGIONES_CHILE = {
    "XV": {
        "nombre": "Región de Arica y Parinacota",
        "ciudades": [
            {
                "id": "arica",
                "nombre": "Arica",
                "x": -118200, "z": 85000,
                "icon": "arica",
                "empresas": ["copec", "tpa_arica", "corpesca", "starken"]
            },
            {
                "id": "putre",
                "nombre": "Putre",
                "x": -116400, "z": 83200,
                "icon": "putre",
                "empresas": ["copec", "aduana_cl"]
            }
        ]
    },
    "I": {
        "nombre": "Región de Tarapacá",
        "ciudades": [
            {
                "id": "iquique",
                "nombre": "Iquique",
                "x": -118100, "z": 92000,
                "icon": "iquique",
                "empresas": ["copec", "zofri", "camanchaca", "shell_cl"]
            },
            {
                "id": "pozo_almonte",
                "nombre": "Pozo Almonte",
                "x": -116900, "z": 93500,
                "icon": "pozo_almonte",
                "empresas": ["copec", "sqm_minera"]
            }
        ]
    },
    "II": {
        "nombre": "Región de Antofagasta",
        "ciudades": [
            {
                "id": "antofagasta",
                "nombre": "Antofagasta",
                "x": -117800, "z": 105000,
                "icon": "antofagasta",
                "empresas": ["copec", "finning_cat", "puerto_antof", "falabella", "starken"]
            },
            {
                "id": "calama",
                "nombre": "Calama",
                "x": -115400, "z": 101000,
                "icon": "calama",
                "empresas": ["codelco", "copec", "shell_cl"]
            },
            {
                "id": "san_pedro",
                "nombre": "San Pedro de Atacama",
                "x": -113800, "z": 102500,
                "icon": "san_pedro",
                "empresas": ["copec", "turismo_atacama"]
            },
            {
                "id": "mejillones",
                "nombre": "Mejillones",
                "x": -118150, "z": 103200,
                "icon": "mejillones",
                "empresas": ["puerto_mej", "petrobras_cl"]
            }
        ]
    },
    "III": {
        "nombre": "Región de Atacama",
        "ciudades": [
            {
                "id": "copiapo",
                "nombre": "Copiapó",
                "x": -116900, "z": 118000,
                "icon": "copiapo",
                "empresas": ["copec", "cmp_minera", "agrosuper", "shell_cl"]
            },
            {
                "id": "caldera",
                "nombre": "Caldera",
                "x": -118200, "z": 116500,
                "icon": "caldera",
                "empresas": ["copec", "pesquera_atacama"]
            },
            {
                "id": "vallenar",
                "nombre": "Vallenar",
                "x": -116400, "z": 124000,
                "icon": "vallenar",
                "empresas": ["copec", "agro_huasco"]
            }
        ]
    },
    "IV": {
        "nombre": "Región de Coquimbo",
        "ciudades": [
            {
                "id": "la_serena",
                "nombre": "La Serena",
                "x": -117200, "z": 135000,
                "icon": "la_serena",
                "empresas": ["copec", "falabella", "cencosud", "shell_cl"]
            },
            {
                "id": "coquimbo",
                "nombre": "Coquimbo",
                "x": -117350, "z": 136200,
                "icon": "coquimbo",
                "empresas": ["puerto_coq", "copec", "tottus_cl"]
            },
            {
                "id": "ovalle",
                "nombre": "Ovalle",
                "x": -116100, "z": 140000,
                "icon": "ovalle",
                "empresas": ["copec", "pisco_capel"]
            },
            {
                "id": "los_vilos",
                "nombre": "Los Vilos",
                "x": -117000, "z": 148500,
                "icon": "los_vilos",
                "empresas": ["copec", "shell_cl"]
            }
        ]
    },
    "V": {
        "nombre": "Región de Valparaíso",
        "ciudades": [
            {
                "id": "valparaiso",
                "nombre": "Valparaíso",
                "x": -117100, "z": 158000,
                "icon": "valparaiso",
                "empresas": ["tps_valpo", "copec", "chilexpress", "falabella"]
            },
            {
                "id": "vina_del_mar",
                "nombre": "Viña del Mar",
                "x": -116900, "z": 157200,
                "icon": "vina_del_mar",
                "empresas": ["cencosud", "copec", "shell_cl"]
            },
            {
                "id": "san_antonio",
                "nombre": "San Antonio",
                "x": -117200, "z": 162000,
                "icon": "san_antonio",
                "empresas": ["sti_san_ant", "copec", "starken", "petrobras_cl"]
            },
            {
                "id": "los_andes",
                "nombre": "Los Andes",
                "x": -114800, "z": 156500,
                "icon": "los_andes",
                "empresas": ["codelco", "copec", "aduana_loslib"]
            }
        ]
    },
    "RM": {
        "nombre": "Región Metropolitana de Santiago",
        "ciudades": [
            {
                "id": "santiago",
                "nombre": "Santiago",
                "x": -115800, "z": 160000,
                "icon": "santiago",
                "empresas": ["falabella", "cencosud", "ccu", "chilexpress", "copec", "shell_cl"]
            },
            {
                "id": "san_bernardo",
                "nombre": "San Bernardo",
                "x": -115700, "z": 162500,
                "icon": "san_bernardo",
                "empresas": ["sodimac_log", "starken", "copec", "agrosuper"]
            },
            {
                "id": "quilicura",
                "nombre": "Quilicura",
                "x": -115900, "z": 158500,
                "icon": "quilicura",
                "empresas": ["ccu", "falabella", "petrobras_cl"]
            }
        ]
    },
    "VI": {
        "nombre": "Región del Libertador General Bernardo O'Higgins",
        "ciudades": [
            {
                "id": "rancagua",
                "nombre": "Rancagua",
                "x": -115500, "z": 165500,
                "icon": "rancagua",
                "empresas": ["codelco", "agrosuper", "copec", "shell_cl"]
            },
            {
                "id": "san_fernando",
                "nombre": "San Fernando",
                "x": -115300, "z": 169000,
                "icon": "san_fernando",
                "empresas": ["concha_toro", "copec", "fruticola_cl"]
            },
            {
                "id": "santa_cruz",
                "nombre": "Santa Cruz",
                "x": -116400, "z": 170500,
                "icon": "santa_cruz",
                "empresas": ["concha_toro", "copec"]
            }
        ]
    },
    "VII": {
        "nombre": "Región del Maule",
        "ciudades": [
            {
                "id": "talca",
                "nombre": "Talca",
                "x": -115200, "z": 175000,
                "icon": "talca",
                "empresas": ["pf_alimentos", "copec", "iansa", "shell_cl"]
            },
            {
                "id": "curico",
                "nombre": "Curicó",
                "x": -115100, "z": 172000,
                "icon": "curico",
                "empresas": ["vina_sanpedro", "copec", "fruticola_cl"]
            },
            {
                "id": "linares",
                "nombre": "Linares",
                "x": -115300, "z": 178000,
                "icon": "linares",
                "empresas": ["iansa", "copec"]
            },
            {
                "id": "constitucion",
                "nombre": "Constitución",
                "x": -117200, "z": 174800,
                "icon": "constitucion",
                "empresas": ["arauco", "copec"]
            }
        ]
    },
    "XVI": {
        "nombre": "Región de Ñuble",
        "ciudades": [
            {
                "id": "chillan",
                "nombre": "Chillán",
                "x": -115000, "z": 183000,
                "icon": "chillan",
                "empresas": ["cecinas_chillan", "copec", "arauco", "shell_cl"]
            },
            {
                "id": "san_carlos",
                "nombre": "San Carlos",
                "x": -114900, "z": 181200,
                "icon": "san_carlos",
                "empresas": ["molino_sc", "copec"]
            }
        ]
    },
    "VIII": {
        "nombre": "Región del Biobío",
        "ciudades": [
            {
                "id": "concepcion",
                "nombre": "Concepción",
                "x": -116800, "z": 185000,
                "icon": "concepcion",
                "empresas": ["arauco", "svti_talcahuano", "copec", "falabella", "shell_cl"]
            },
            {
                "id": "talcahuano",
                "nombre": "Talcahuano",
                "x": -117000, "z": 184200,
                "icon": "talcahuano",
                "empresas": ["huachipato", "camanchaca", "petrobras_cl"]
            },
            {
                "id": "los_angeles",
                "nombre": "Los Ángeles",
                "x": -115200, "z": 188000,
                "icon": "los_angeles",
                "empresas": ["cmpc", "arauco", "copec", "starken"]
            },
            {
                "id": "coronel",
                "nombre": "Coronel",
                "x": -116900, "z": 186800,
                "icon": "coronel",
                "empresas": ["puerto_coronel", "pesquera_coronel"]
            }
        ]
    },
    "IX": {
        "nombre": "Región de La Araucanía",
        "ciudades": [
            {
                "id": "temuco",
                "nombre": "Temuco",
                "x": -115400, "z": 194000,
                "icon": "temuco",
                "empresas": ["rosen_chile", "copec", "frigorifico_tem", "shell_cl"]
            },
            {
                "id": "villarrica",
                "nombre": "Villarrica",
                "x": -115100, "z": 197000,
                "icon": "villarrica",
                "empresas": ["copec", "maderas_sur"]
            },
            {
                "id": "angol",
                "nombre": "Angol",
                "x": -115800, "z": 190500,
                "icon": "angol",
                "empresas": ["cmpc", "copec"]
            }
        ]
    },
    "XIV": {
        "nombre": "Región de Los Ríos",
        "ciudades": [
            {
                "id": "valdivia",
                "nombre": "Valdivia",
                "x": -116500, "z": 201000,
                "icon": "valdivia",
                "empresas": ["kunstmann", "copec", "asenav", "shell_cl"]
            },
            {
                "id": "la_union",
                "nombre": "La Unión",
                "x": -116200, "z": 204500,
                "icon": "la_union",
                "empresas": ["colun", "copec", "arauco"]
            }
        ]
    },
    "X": {
        "nombre": "Región de Los Lagos",
        "ciudades": [
            {
                "id": "puerto_montt",
                "nombre": "Puerto Montt",
                "x": -116100, "z": 210000,
                "icon": "puerto_montt",
                "empresas": ["aquachile", "copec", "somarco_ferries", "shell_cl", "starken"]
            },
            {
                "id": "osorno",
                "nombre": "Osorno",
                "x": -116200, "z": 206500,
                "icon": "osorno",
                "empresas": ["colun", "frigorifico_osorno", "copec"]
            },
            {
                "id": "castro",
                "nombre": "Castro",
                "x": -116800, "z": 214500,
                "icon": "castro",
                "empresas": ["aquachile", "copec", "naviera_chiloe"]
            },
            {
                "id": "quellon",
                "nombre": "Quellón",
                "x": -116700, "z": 218500,
                "icon": "quellon",
                "empresas": ["salmones_quellon", "copec"]
            },
            {
                "id": "chaiten",
                "nombre": "Chaitén",
                "x": -115500, "z": 216000,
                "icon": "chaiten",
                "empresas": ["copec", "barcazas_austral"]
            }
        ]
    },
    "XI": {
        "nombre": "Región de Aysén del Gral. Carlos Ibáñez del Campo",
        "ciudades": [
            {
                "id": "coyhaique",
                "nombre": "Coyhaique",
                "x": -114800, "z": 228000,
                "icon": "coyhaique",
                "empresas": ["copec", "ganadera_aysen", "starken"]
            },
            {
                "id": "puerto_aysen",
                "nombre": "Puerto Aysén",
                "x": -115600, "z": 226500,
                "icon": "puerto_aysen",
                "empresas": ["friosur", "copec", "navimag"]
            },
            {
                "id": "cochrane",
                "nombre": "Cochrane",
                "x": -114200, "z": 236000,
                "icon": "cochrane",
                "empresas": ["terpel", "copec"]
            },
            {
                "id": "v_ohiggins",
                "nombre": "Villa O'Higgins",
                "x": -113800, "z": 242000,
                "icon": "v_ohiggins",
                "empresas": ["copec", "logistica_austral"]
            }
        ]
    },
    "XII": {
        "nombre": "Región de Magallanes y de la Antártica Chilena",
        "ciudades": [
            {
                "id": "punta_arenas",
                "nombre": "Punta Arenas",
                "x": -111500, "z": 265000,
                "icon": "punta_arenas",
                "empresas": ["enap_magallanes", "copec", "tabsa_ferries", "shell_cl"]
            },
            {
                "id": "pto_natales",
                "nombre": "Puerto Natales",
                "x": -113200, "z": 258000,
                "icon": "pto_natales",
                "empresas": ["australis_seafood", "copec", "frigorifico_sur"]
            },
            {
                "id": "porvenir",
                "nombre": "Porvenir",
                "x": -111100, "z": 267000,
                "icon": "porvenir",
                "empresas": ["nova_austral", "copec"]
            }
        ]
    }
}

# ==============================================================================
# BASE DE DATOS: EMPRESAS CHILENAS Y ESTACIONES DE SERVICIO
# ==============================================================================
EMPRESAS_CHILENAS = {
    "copec": {
        "nombre": "Copec - Combustibles y Lubricantes",
        "rubro": "Combustibles, Tiendas Pronto Copec y Punto Copec",
        "cargas_in": ["petroleo_ref", "combust_cl", "lubricantes_copec", "abarrotes"],
        "cargas_out": ["combust_cl", "lubricantes_copec"]
    },
    "shell_cl": {
        "nombre": "Shell Enex Chile",
        "rubro": "Combustibles y Tiendas Upa! / Upita",
        "cargas_in": ["petroleo_ref", "combust_cl", "bebidas", "snacks"],
        "cargas_out": ["combust_cl", "lubricantes_shell"]
    },
    "petrobras_cl": {
        "nombre": "Petrobras Chile - Esmax",
        "rubro": "Combustibles y Tiendas Spacio 1",
        "cargas_in": ["combust_cl", "lubricantes_petro"],
        "cargas_out": ["combust_cl"]
    },
    "codelco": {
        "nombre": "Codelco Chile",
        "rubro": "Minería Estatal del Cobre (Chuquicamata, El Teniente, Andina)",
        "cargas_in": ["maquinaria_pesada", "explosivos_min", "acido_sulfurico", "repuestos_cat"],
        "cargas_out": ["catod_cobre", "concentrado_cobre", "anodos_cobre"]
    },
    "arauco": {
        "nombre": "Arauco Celulosa y Maderas",
        "rubro": "Complejo Forestal y Celulosa (MAPA, Constitución)",
        "cargas_in": ["troncos_pino", "quimicos_blanqueo", "repuestos_ind"],
        "cargas_out": ["cel_fardo", "madera_aserrada", "tableros_mdf"]
    },
    "cmpc": {
        "nombre": "Empresas CMPC",
        "rubro": "Forestal Mininco y Papeles del Pacífico",
        "cargas_in": ["troncos_eucalipto", "bobinas_papel", "combust_cl"],
        "cargas_out": ["cel_fardo", "papel_kraft", "madera_aserrada"]
    },
    "agrosuper": {
        "nombre": "Agrosuper Chile",
        "rubro": "Alimentos (Super Pollo, Super Cerdo, La Crianza, Sopraval)",
        "cargas_in": ["granos_maiz", "alimento_animal", "envases_empaque"],
        "cargas_out": ["carnes_frescas", "cecinas_envasadas", "congelados_cl"]
    },
    "falabella": {
        "nombre": "Falabella Logística & Retail",
        "rubro": "Centro de Distribución Nacional San Bernardo y Tiendas",
        "cargas_in": ["electronica", "ropa_confeccion", "muebles_hogar"],
        "cargas_out": ["paqueteria_retail", "electrodomesticos", "muebles_hogar"]
    },
    "cencosud": {
        "nombre": "Cencosud (Jumbo / Easy / Santa Isabel)",
        "rubro": "Supermercados y Mejoramiento del Hogar",
        "cargas_in": ["abarrotes", "carnes_frescas", "materiales_construccion"],
        "cargas_out": ["alimentos_retail", "herramientas_easy"]
    },
    "ccu": {
        "nombre": "CCU - Compañía de Cervecerías Unidas",
        "rubro": "Bebidas, Cervezas (Cristal, Royal) y Aguas (Cachantún)",
        "cargas_in": ["cebada_malta", "botellas_vidrio", "azucar_industrial"],
        "cargas_out": ["cervezas_ccu", "bebidas_gaseosas", "aguas_minerales"]
    },
    "colun": {
        "nombre": "Colun - La Magia del Sur",
        "rubro": "Cooperativa Agrícola y Lechera de La Unión",
        "cargas_in": ["leche_cruda", "envases_tetra", "sal_industrial"],
        "cargas_out": ["leche_sur", "quesos_colun", "mantequilla_sur", "yogurt_colun"]
    },
    "aquachile": {
        "nombre": "AquaChile Salmones",
        "rubro": "Acuicultura y Exportación de Salmón",
        "cargas_in": ["alimento_peces", "cajas_poliestireno", "hielo_escamas"],
        "cargas_out": ["salm_fresco", "salmon_congelado", "filetes_salmon"]
    },
    "concha_toro": {
        "nombre": "Viña Concha y Toro",
        "rubro": "Viñedos y Exportación de Vinos (Casillero del Diablo)",
        "cargas_in": ["uva_vinifera", "botellas_vino", "corchos_roble", "barricas_roble"],
        "cargas_out": ["vino_reserva", "vino_exportacion"]
    },
    "starken": {
        "nombre": "Starken Encomiendas y Logística",
        "rubro": "Transporte de carga express y encomiendas en todo Chile",
        "cargas_in": ["encomiendas", "paquetes_express"],
        "cargas_out": ["encomiendas", "carga_consolidada"]
    },
    "chilexpress": {
        "nombre": "Chilexpress Courier",
        "rubro": "Logística urgente y paquetería e-commerce nacional",
        "cargas_in": ["paqueteria_courier", "documentos_val"],
        "cargas_out": ["paquetes_express", "cargas_aereas_terrestres"]
    },
    "tpa_arica": {
        "nombre": "Terminal Puerto Arica (TPA)",
        "rubro": "Puerto multipropósito y conexión internacional con Bolivia",
        "cargas_in": ["minerales_export", "contenedores_import"],
        "cargas_out": ["contenedores_import", "carga_general"]
    },
    "sti_san_ant": {
        "nombre": "San Antonio Terminal Internacional (STI)",
        "rubro": "Mayor puerto de transferencia de contenedores de Chile",
        "cargas_in": ["fruta_export", "vino_reserva", "cobre_export"],
        "cargas_out": ["contenedores_import", "vehiculos_nuevos", "maquinaria"]
    },
    "kunstmann": {
        "nombre": "Cervecería Kunstmann (Valdivia)",
        "rubro": "Cerveza artesanal de Valdivia (Torobayo)",
        "cargas_in": ["lupulo_valdivia", "cebada_malta", "botellas_vidrio"],
        "cargas_out": ["cerveza_kunstmann", "barriles_cerveza"]
    }
}

# ==============================================================================
# BASE DE DATOS: CARGAS CHILENAS TÍPICAS
# ==============================================================================
CARGAS_CHILENAS = {
    "catod_cobre": {
        "nombre": "Cátodos de Cobre de Alta Pureza",
        "nombre_loc": "@@catod_cobre@@",
        "masa": 24000,
        "fragilidad": 0.2,
        "valiosa": True,
        "grupo": "machinery"
    },
    "cel_fardo": {
        "nombre": "Fardos de Celulosa Kraft Arauco/CMPC",
        "nombre_loc": "@@cel_fardo@@",
        "masa": 22500,
        "fragilidad": 0.1,
        "valiosa": False,
        "grupo": "bulk"
    },
    "salm_fresco": {
        "nombre": "Salmón Atlántico Fresco en Hielo",
        "nombre_loc": "@@salm_fresco@@",
        "masa": 19000,
        "fragilidad": 0.8,
        "valiosa": True,
        "grupo": "refrigerated"
    },
    "vino_reserva": {
        "nombre": "Vino Chileno Reserva Embotellado",
        "nombre_loc": "@@vino_reserva@@",
        "masa": 18500,
        "fragilidad": 0.7,
        "valiosa": True,
        "grupo": "containers"
    },
    "leche_sur": {
        "nombre": "Leche Fresca en Cisterna Colun",
        "nombre_loc": "@@leche_sur@@",
        "masa": 25000,
        "fragilidad": 0.3,
        "valiosa": False,
        "grupo": "liquid"
    },
    "combust_cl": {
        "nombre": "Gasolinas 93/97 y Diésel Copec",
        "nombre_loc": "@@combust_cl@@",
        "masa": 26000,
        "fragilidad": 0.9,
        "valiosa": True,
        "grupo": "adr_liquid"
    },
    "palta_hass": {
        "nombre": "Paltas Hass Chilenas de Exportación",
        "nombre_loc": "@@palta_hass@@",
        "masa": 17500,
        "fragilidad": 0.6,
        "valiosa": True,
        "grupo": "refrigerated"
    },
    "encomiendas": {
        "nombre": "Cargas Express y Encomiendas Nacionales",
        "nombre_loc": "@@encomiendas@@",
        "masa": 12000,
        "fragilidad": 0.5,
        "valiosa": False,
        "grupo": "containers"
    }
}


def generar_ciudades():
    """Genera los archivos .sui para cada ciudad y el master city.chile.sii"""
    city_dir = DEF_DIR / "city"
    city_dir.mkdir(parents=True, exist_ok=True)

    master_includes = []

    for reg_code, reg_data in REGIONES_CHILE.items():
        for ciudad in reg_data["ciudades"]:
            cid = ciudad["id"]
            master_includes.append(f'@include "city/{cid}.sui"')

            sui_path = city_dir / f"{cid}.sui"
            content = f"""city_data : city.{cid}
{{
    city_name: "{ciudad['nombre']}"
    city_name_localized: "@@{cid}@@"
    country: chile

    map_x_offsets[]: 0
    map_x_offsets[]: 0
    map_x_offsets[]: 0
    map_x_offsets[]: -10
    map_x_offsets[]: 0
    map_x_offsets[]: 0
    map_x_offsets[]: -20
    map_x_offsets[]: -15

    map_y_offsets[]: 0
    map_y_offsets[]: 0
    map_y_offsets[]: 25
    map_y_offsets[]: -10
    map_y_offsets[]: -5
    map_y_offsets[]: -15
    map_y_offsets[]: -15
    map_y_offsets[]: -15

    # Coordenadas en mapa SCS (escala 1:19)
    # Región: {reg_data['nombre']} ({reg_code})
    # Posición estimada X/Z
    vehicle_brands[]: "scania"
    vehicle_brands[]: "volvo"
}}
"""
            with open(sui_path, "w", encoding="utf-8") as f:
                f.write(content)

    # Master city.chile.sii
    master_path = DEF_DIR / "city.chile.sii"
    master_content = "SiiNunit\n{\n" + "\n".join(master_includes) + "\n}\n"
    with open(master_path, "w", encoding="utf-8") as f:
        f.write(master_content)

    print(f"-> {len(master_includes)} ciudades generadas en def/city/ y def/city.chile.sii")


def generar_empresas():
    """Genera las definiciones de empresas en def/company/ y def/company.chile.sii"""
    company_dir = DEF_DIR / "company"
    company_dir.mkdir(parents=True, exist_ok=True)

    master_includes = []

    for comp_id, comp_data in EMPRESAS_CHILENAS.items():
        master_includes.append(f'@include "company/{comp_id}.sui"')

        sui_path = company_dir / f"{comp_id}.sui"
        content = f"""company_permanent : company.permanent.{comp_id}
{{
    name: "{comp_data['nombre']}"
    sort_name: "{comp_id.upper()}"
    trailer_look: "{comp_id}"
}}
"""
        with open(sui_path, "w", encoding="utf-8") as f:
            f.write(content)

    master_path = DEF_DIR / "company.chile.sii"
    master_content = "SiiNunit\n{\n" + "\n".join(master_includes) + "\n}\n"
    with open(master_path, "w", encoding="utf-8") as f:
        f.write(master_content)

    print(f"-> {len(master_includes)} empresas chilenas generadas en def/company/ y def/company.chile.sii")


def generar_cargas():
    """Genera las definiciones de cargas chilenas en def/cargo/ y def/cargo.chile.sii"""
    cargo_dir = DEF_DIR / "cargo"
    cargo_dir.mkdir(parents=True, exist_ok=True)

    master_includes = []

    for cargo_id, cdata in CARGAS_CHILENAS.items():
        master_includes.append(f'@include "cargo/{cargo_id}.sui"')

        sui_path = cargo_dir / f"{cargo_id}.sui"
        valiosa_flag = "true" if cdata["valiosa"] else "false"
        content = f"""cargo_data : cargo.{cargo_id}
{{
    name: "{cdata['nombre']}"
    name_localized: "{cdata['nombre_loc']}"
    fragility: {cdata['fragilidad']}
    valuable: {valiosa_flag}
    group[]: {cdata['grupo']}
    mass: {cdata['masa']}.0
    unit_reward_per_km: 0.35
    unit_load_time: 40
    body_types[]: _curtain_s
    body_types[]: _dryvan_s
    body_types[]: _insulated_s
}}
"""
        with open(sui_path, "w", encoding="utf-8") as f:
            f.write(content)

    master_path = DEF_DIR / "cargo.chile.sii"
    master_content = "SiiNunit\n{\n" + "\n".join(master_includes) + "\n}\n"
    with open(master_path, "w", encoding="utf-8") as f:
        f.write(master_content)

    print(f"-> {len(master_includes)} cargas chilenas generadas en def/cargo/ y def/cargo.chile.sii")


def generar_estaciones_servicio():
    """Genera mapeos de estaciones de servicio chilenas (Copec, Shell, Petrobras)"""
    world_dir = DEF_DIR / "world"
    world_dir.mkdir(parents=True, exist_ok=True)

    gas_path = world_dir / "gasoline_station.chile.sii"
    content = """SiiNunit
{
# Estaciones de Servicio Oficiales en Rutas y Carreteras de Chile
# Red Copec (Pronto / Punto), Shell Enex (Upa!), Petrobras (Spacio 1)

gasoline_station : gas.copec_pronto
{
    name: "Copec Pronto"
    fuel_price: 1.15
}

gasoline_station : gas.copec_punto
{
    name: "Copec Punto"
    fuel_price: 1.15
}

gasoline_station : gas.shell_upa
{
    name: "Shell Upa!"
    fuel_price: 1.16
}

gasoline_station : gas.petrobras_spacio
{
    name: "Petrobras Spacio 1"
    fuel_price: 1.14
}
}
"""
    with open(gas_path, "w", encoding="utf-8") as f:
        f.write(content)

    print("-> Estaciones de servicio generadas en def/world/gasoline_station.chile.sii")


def main():
    print("================================================================")
    print(" TRANSPORTE AUSTRAL - GENERADOR DE DEFINICIONES DE CHILE (ETS2)")
    print("================================================================")
    generar_ciudades()
    generar_empresas()
    generar_cargas()
    generar_estaciones_servicio()
    print("================================================================")
    print("Todas las definiciones se han generado correctamente.")


if __name__ == "__main__":
    main()
