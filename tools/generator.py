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
                "nombre": "Arica (Av. Comandante San Martín - Morro)",
                "x": -118200, "z": 85000,
                "icon": "arica",
                "empresas": ["copec", "tpa_arica", "corpesca", "starken"]
            },
            {
                "id": "putre",
                "nombre": "Putre (Paso Chungará - Ruta 11-CH)",
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
                "nombre": "Iquique (Av. Arturo Prat - Costanera)",
                "x": -118100, "z": 92000,
                "icon": "iquique",
                "empresas": ["copec", "zofri", "camanchaca", "shell_cl"]
            },
            {
                "id": "pozo_almonte",
                "nombre": "Pozo Almonte (Panamericana - Salitreras)",
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
                "nombre": "Antofagasta (Av. Pérez Zujovic - Costanera)",
                "x": -117800, "z": 105000,
                "icon": "antofagasta",
                "empresas": ["copec", "finning_cat", "puerto_antof", "falabella", "starken"]
            },
            {
                "id": "calama",
                "nombre": "Calama (Av. Granaderos - Chuquicamata)",
                "x": -115400, "z": 101000,
                "icon": "calama",
                "empresas": ["codelco", "copec", "shell_cl"]
            },
            {
                "id": "san_pedro",
                "nombre": "San Pedro de Atacama (Caracoles - Valle de la Luna)",
                "x": -113800, "z": 102500,
                "icon": "san_pedro",
                "empresas": ["copec", "turismo_atacama"]
            },
            {
                "id": "mejillones",
                "nombre": "Mejillones (Av. Fertilizantes - Puerto)",
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
                "nombre": "Copiapó (Av. Copayapu - Los Carrera)",
                "x": -116900, "z": 118000,
                "icon": "copiapo",
                "empresas": ["copec", "cmp_minera", "agrosuper", "shell_cl"]
            },
            {
                "id": "caldera",
                "nombre": "Caldera (Costanera - Bahía Inglesa)",
                "x": -118200, "z": 116500,
                "icon": "caldera",
                "empresas": ["copec", "pesquera_atacama"]
            },
            {
                "id": "vallenar",
                "nombre": "Vallenar (Av. Brasil - Valle del Huasco)",
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
                "nombre": "La Serena (Av. Francisco de Aguirre - El Faro)",
                "x": -117200, "z": 135000,
                "icon": "la_serena",
                "empresas": ["copec", "falabella", "cencosud", "shell_cl"]
            },
            {
                "id": "coquimbo",
                "nombre": "Coquimbo (Av. Costanera - Puerto)",
                "x": -117350, "z": 136200,
                "icon": "coquimbo",
                "empresas": ["puerto_coq", "copec", "tottus_cl"]
            },
            {
                "id": "ovalle",
                "nombre": "Ovalle (Av. Ariztía - Valle del Limarí)",
                "x": -116100, "z": 140000,
                "icon": "ovalle",
                "empresas": ["copec", "pisco_capel"]
            },
            {
                "id": "los_vilos",
                "nombre": "Los Vilos (Costanera Salvador Allende)",
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
                "nombre": "Valparaíso (Av. España - Errázuriz)",
                "x": -117100, "z": 158000,
                "icon": "valparaiso",
                "empresas": ["tps_valpo", "copec", "chilexpress", "falabella"]
            },
            {
                "id": "vina_del_mar",
                "nombre": "Viña del Mar (Av. Libertad - 1 Norte)",
                "x": -116900, "z": 157200,
                "icon": "vina_del_mar",
                "empresas": ["cencosud", "copec", "shell_cl"]
            },
            {
                "id": "san_antonio",
                "nombre": "San Antonio (Av. Barros Luco - Puerto STI)",
                "x": -117200, "z": 162000,
                "icon": "san_antonio",
                "empresas": ["sti_san_ant", "copec", "starken", "petrobras_cl"]
            },
            {
                "id": "los_andes",
                "nombre": "Los Andes (Av. Santa Teresa - Paso Los Libertadores)",
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
                "nombre": "Santiago (Alameda - Autopista Central)",
                "x": -115800, "z": 160000,
                "icon": "santiago",
                "empresas": ["falabella", "cencosud", "ccu", "chilexpress", "copec", "shell_cl"]
            },
            {
                "id": "san_bernardo",
                "nombre": "San Bernardo (Av. Portales - Eje Sur)",
                "x": -115700, "z": 162500,
                "icon": "san_bernardo",
                "empresas": ["sodimac_log", "starken", "copec", "agrosuper"]
            },
            {
                "id": "quilicura",
                "nombre": "Quilicura (Américo Vespucio - Panamericana Norte)",
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
                "nombre": "Rancagua (Av. O'Higgins - Carretera El Cobre)",
                "x": -115500, "z": 165500,
                "icon": "rancagua",
                "empresas": ["codelco", "agrosuper", "copec", "shell_cl"]
            },
            {
                "id": "san_fernando",
                "nombre": "San Fernando (Av. Manuel Rodríguez)",
                "x": -115300, "z": 169000,
                "icon": "san_fernando",
                "empresas": ["concha_toro", "copec", "fruticola_cl"]
            },
            {
                "id": "santa_cruz",
                "nombre": "Santa Cruz (Av. Errázuriz - Valle de Colchagua)",
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
                "nombre": "Talca (Av. San Miguel - 2 Sur)",
                "x": -115200, "z": 175000,
                "icon": "talca",
                "empresas": ["pf_alimentos", "copec", "iansa", "shell_cl"]
            },
            {
                "id": "curico",
                "nombre": "Curicó (Av. Manso de Velasco - Alameda)",
                "x": -115100, "z": 172000,
                "icon": "curico",
                "empresas": ["vina_sanpedro", "copec", "fruticola_cl"]
            },
            {
                "id": "linares",
                "nombre": "Linares (Av. Aníbal León Bustos)",
                "x": -115300, "z": 178000,
                "icon": "linares",
                "empresas": ["iansa", "copec"]
            },
            {
                "id": "constitucion",
                "nombre": "Constitución (Costanera Río Maule)",
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
                "nombre": "Chillán (Av. O'Higgins - Av. Brasil)",
                "x": -115000, "z": 183000,
                "icon": "chillan",
                "empresas": ["cecinas_chillan", "copec", "arauco", "shell_cl"]
            },
            {
                "id": "san_carlos",
                "nombre": "San Carlos (Av. Arturo Prat - Violeta Parra)",
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
                "nombre": "Concepción (Av. O'Higgins - Paicaví)",
                "x": -116800, "z": 185000,
                "icon": "concepcion",
                "empresas": ["arauco", "svti_talcahuano", "copec", "falabella", "shell_cl"]
            },
            {
                "id": "talcahuano",
                "nombre": "Talcahuano (Autopista - Puerto San Vicente)",
                "x": -117000, "z": 184200,
                "icon": "talcahuano",
                "empresas": ["huachipato", "camanchaca", "petrobras_cl"]
            },
            {
                "id": "los_angeles",
                "nombre": "Los Ángeles (Av. Alemania - Ricardo Vicuña)",
                "x": -115200, "z": 188000,
                "icon": "los_angeles",
                "empresas": ["cmpc", "arauco", "copec", "starken"]
            },
            {
                "id": "coronel",
                "nombre": "Coronel (Ruta 160 - Puerto Coronel)",
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
                "nombre": "Temuco (Av. Alemania - Caupolicán)",
                "x": -115400, "z": 194000,
                "icon": "temuco",
                "empresas": ["rosen_chile", "copec", "frigorifico_tem", "shell_cl"]
            },
            {
                "id": "villarrica",
                "nombre": "Villarrica (Av. Pedro de Valdivia - Costanera)",
                "x": -115100, "z": 197000,
                "icon": "villarrica",
                "empresas": ["copec", "maderas_sur"]
            },
            {
                "id": "angol",
                "nombre": "Angol (Av. O'Higgins - Cordillera de Nahuelbuta)",
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
                "nombre": "Valdivia (Costanera Prat - Ramón Picarte)",
                "x": -116500, "z": 201000,
                "icon": "valdivia",
                "empresas": ["kunstmann", "copec", "asenav", "shell_cl"]
            },
            {
                "id": "la_union",
                "nombre": "La Unión (Av. Arturo Prat - Planta Colun)",
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
                "nombre": "Puerto Montt (Diego Portales - Angelmó)",
                "x": -116100, "z": 210000,
                "icon": "puerto_montt",
                "empresas": ["aquachile", "copec", "somarco_ferries", "shell_cl", "starken"]
            },
            {
                "id": "osorno",
                "nombre": "Osorno (Av. Mackenna - Errázuriz)",
                "x": -116200, "z": 206500,
                "icon": "osorno",
                "empresas": ["colun", "frigorifico_osorno", "copec"]
            },
            {
                "id": "castro",
                "nombre": "Castro (Palafitos Gamboa - San Martín)",
                "x": -116800, "z": 214500,
                "icon": "castro",
                "empresas": ["aquachile", "copec", "naviera_chiloe"]
            },
            {
                "id": "quellon",
                "nombre": "Quellón (Hito Cero Panamericana)",
                "x": -116700, "z": 218500,
                "icon": "quellon",
                "empresas": ["salmones_quellon", "copec"]
            },
            {
                "id": "chaiten",
                "nombre": "Chaitén (Costanera - Carretera Austral)",
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
                "nombre": "Coyhaique (Baquedano - Carretera Austral)",
                "x": -114800, "z": 228000,
                "icon": "coyhaique",
                "empresas": ["copec", "ganadera_aysen", "starken"]
            },
            {
                "id": "puerto_aysen",
                "nombre": "Puerto Aysén (Puente Presidente Ibáñez)",
                "x": -115600, "z": 226500,
                "icon": "puerto_aysen",
                "empresas": ["friosur", "copec", "navimag"]
            },
            {
                "id": "cochrane",
                "nombre": "Cochrane (Av. San Valentín - Río Baker)",
                "x": -114200, "z": 236000,
                "icon": "cochrane",
                "empresas": ["terpel", "copec"]
            },
            {
                "id": "v_ohiggins",
                "nombre": "Villa O'Higgins (Fin Carretera Austral)",
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
                "nombre": "Punta Arenas (Costanera del Estrecho - Av. España)",
                "x": -111500, "z": 265000,
                "icon": "punta_arenas",
                "empresas": ["enap_magallanes", "copec", "tabsa_ferries", "shell_cl"]
            },
            {
                "id": "pto_natales",
                "nombre": "Puerto Natales (Costanera Pedro Montt)",
                "x": -113200, "z": 258000,
                "icon": "pto_natales",
                "empresas": ["australis_seafood", "copec", "frigorifico_sur"]
            },
            {
                "id": "porvenir",
                "nombre": "Porvenir (Costanera Chiloé - Tierra del Fuego)",
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
        "rubro": "Red de Estaciones de Servicio Copec, Pronto Copec y Punto Copec",
        "cargas_in": ["petroleo_ref", "combust_cl", "lubricantes_copec", "diesel", "petrol", "abarrotes"],
        "cargas_out": ["combust_cl", "lubricantes_copec"]
    },
    "shell_cl": {
        "nombre": "Shell Enex Chile",
        "rubro": "Red de Estaciones de Servicio Shell y Tiendas Upa! / Upita",
        "cargas_in": ["petroleo_ref", "combust_cl", "diesel", "petrol", "bebidas", "snacks"],
        "cargas_out": ["combust_cl", "lubricantes_shell"]
    },
    "petrobras": {
        "nombre": "Petrobras Chile - Esmax",
        "rubro": "Red de Estaciones de Servicio Petrobras y Tiendas Spacio 1",
        "cargas_in": ["combust_cl", "diesel", "petrol", "lubricantes_petro"],
        "cargas_out": ["combust_cl"]
    },
    "petrobras_cl": {
        "nombre": "Petrobras Chile - Esmax",
        "rubro": "Red de Estaciones de Servicio Petrobras y Tiendas Spacio 1",
        "cargas_in": ["combust_cl", "diesel", "petrol", "lubricantes_petro"],
        "cargas_out": ["combust_cl"]
    },
    "aramco": {
        "nombre": "Aramco Chile",
        "rubro": "Red Global de Combustibles y Estaciones de Servicio Aramco",
        "cargas_in": ["combust_cl", "diesel", "petrol"],
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


# Mapeo oficial de las 16 Regiones de Chile con coordenadas exactas alineadas a los garajes en los sectores
CONFIG_REGIONES = {
    "XV": {"id": "cl_xv", "num": 101, "nombre": "Región de Arica y Parinacota", "pos": (-38999, 0, -54871), "code": "AP"},
    "I": {"id": "cl_i", "num": 102, "nombre": "Región de Tarapacá", "pos": (-44882, 0, -46900), "code": "TA"},
    "II": {"id": "cl_ii", "num": 103, "nombre": "Región de Antofagasta", "pos": (-39807, 0, -38549), "code": "AN"},
    "III": {"id": "cl_iii", "num": 104, "nombre": "Región de Atacama", "pos": (-36466, 0, -26835), "code": "AT"},
    "IV": {"id": "cl_iv", "num": 105, "nombre": "Región de Coquimbo", "pos": (-36768, 0, -16268), "code": "CO"},
    "V": {"id": "cl_v", "num": 106, "nombre": "Región de Valparaíso", "pos": (-31578, 0, -14044), "code": "VA"},
    "RM": {"id": "cl_rm", "num": 107, "nombre": "Región Metropolitana", "pos": (-30174, 0, -4751), "code": "RM"},
    "VI": {"id": "cl_vi", "num": 108, "nombre": "Región de O'Higgins", "pos": (-26395, 0, -2170), "code": "OH"},
    "VII": {"id": "cl_vii", "num": 109, "nombre": "Región del Maule", "pos": (-16450, 0, 3310), "code": "MA"},
    "XVI": {"id": "cl_xvi", "num": 110, "nombre": "Región de Ñuble", "pos": (-16230, 0, 7437), "code": "NB"},
    "VIII": {"id": "cl_viii", "num": 111, "nombre": "Región del Biobío", "pos": (-11085, 0, 11548), "code": "BI"},
    "IX": {"id": "cl_ix", "num": 112, "nombre": "Región de La Araucanía", "pos": (-9769, 0, 18357), "code": "AR"},
    "XIV": {"id": "cl_xiv", "num": 113, "nombre": "Región de Los Ríos", "pos": (-12794, 0, 20153), "code": "LR"},
    "X": {"id": "cl_x", "num": 114, "nombre": "Región de Los Lagos", "pos": (-17861, 0, 24140), "code": "LL"},
    "XI": {"id": "cl_xi", "num": 115, "nombre": "Región de Aysén", "pos": (-22265, 0, 25768), "code": "AI"},
    "XII": {"id": "cl_xii", "num": 116, "nombre": "Región de Magallanes", "pos": (-13182, 0, 31278), "code": "MG"},
}

CIUDAD_BRANDS = {
    "arica": "scania",
    "iquique": "volvo",
    "antofagasta": "man",
    "copiapo": "mercedes",
    "la_serena": "renault",
    "valparaiso": "daf",
    "santiago": "iveco",
    "rancagua": "scania",
    "talca": "volvo",
    "chillan": "man",
    "concepcion": "mercedes",
    "temuco": "renault",
    "valdivia": "daf",
    "puerto_montt": "iveco",
    "coyhaique": "scania",
    "punta_arenas": "volvo",
}


def generar_ciudades():
    """Genera los archivos .sui para cada ciudad vinculada a su región administrativa"""
    city_dir = DEF_DIR / "city"
    city_dir.mkdir(parents=True, exist_ok=True)

    master_includes = []

    for reg_code, reg_data in REGIONES_CHILE.items():
        reg_cfg = CONFIG_REGIONES.get(reg_code, {"id": "chile", "nombre": reg_data["nombre"]})
        country_id_str = reg_cfg["id"]

        for ciudad in reg_data["ciudades"]:
            cid = ciudad["id"]
            master_includes.append(f'@include "city/{cid}.sui"')

            sui_path = city_dir / f"{cid}.sui"
            brand_str = f'\n    vehicle_brands[]: "{CIUDAD_BRANDS[cid]}"' if cid in CIUDAD_BRANDS else ""
            content = f"""city_data : city.{cid}
{{
    city_name: "{ciudad['nombre']}"
    city_name_localized: "{ciudad['nombre']}"
    country: {country_id_str}{brand_str}

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
    # Posición estimada X/Z: ({ciudad['x']}, {ciudad['z']})
}}
"""
            with open(sui_path, "w", encoding="utf-8") as f:
                f.write(content)

    # Master city.sii (Reemplaza a nivel juego para mapa standalone)
    master_path = DEF_DIR / "city.sii"
    master_content = "SiiNunit\n{\n" + "\n".join(master_includes) + "\n}\n"
    with open(master_path, "w", encoding="utf-8") as f:
        f.write(master_content)

    # Eliminar viejo city.chile.sii si existe
    old_master = DEF_DIR / "city.chile.sii"
    if old_master.exists():
        old_master.unlink()

    print(f"-> {len(master_includes)} ciudades generadas en def/city/ asignadas a sus 16 regiones")


def generar_empresas():
    """Genera las definiciones de empresas en def/company/ y def/company.sii con sucursales e in/out de cargas"""
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

        # 1. Generar carpetas in/ y out/ para cargas de transporte
        in_dir = company_dir / comp_id / "in"
        in_dir.mkdir(parents=True, exist_ok=True)
        for cargo_in in comp_data.get("cargas_in", []):
            cargo_sii = in_dir / f"{cargo_in}.sii"
            cargo_sii.write_text(f'SiiNunit\n{{\ncargo_def : .{cargo_in} {{\n cargo: "cargo.{cargo_in}"\n}}\n}}\n', encoding="utf-8")

        out_dir = company_dir / comp_id / "out"
        out_dir.mkdir(parents=True, exist_ok=True)
        for cargo_out in comp_data.get("cargas_out", []):
            cargo_sii = out_dir / f"{cargo_out}.sii"
            cargo_sii.write_text(f'SiiNunit\n{{\ncargo_def : .{cargo_out} {{\n cargo: "cargo.{cargo_out}"\n}}\n}}\n', encoding="utf-8")

        # 2. Generar sucursales activas en editor/ para las comunas y estaciones de servicio
        editor_dir = company_dir / comp_id / "editor"
        editor_dir.mkdir(parents=True, exist_ok=True)

        for reg_code, reg_info in REGIONES_CHILE.items():
            for ciudad in reg_info["ciudades"]:
                cid = ciudad["id"]
                es_copec = (comp_id == "copec")
                es_shell = (comp_id == "shell_cl" and (cid in ["arica", "iquique", "antofagasta", "calama", "copiapo", "la_serena", "los_vilos", "vina_del_mar", "santiago", "rancagua", "talca", "chillan", "concepcion", "temuco", "valdivia", "puerto_montt", "punta_arenas"]))
                es_petro = (comp_id in ("petrobras", "petrobras_cl") and (cid in ["antofagasta", "mejillones", "san_antonio", "santiago", "quilicura", "talcahuano", "concepcion"]))
                es_aramco = (comp_id == "aramco" and (cid in ["arica", "antofagasta", "la_serena", "valparaiso", "santiago", "rancagua", "talca", "chillan", "concepcion", "temuco", "puerto_montt"]))
                en_lista = comp_id in ciudad.get("empresas", [])

                if es_copec or es_shell or es_petro or es_aramco or en_lista:
                    ed_sii = editor_dir / f"{cid}.sii"
                    ed_sii.write_text(f'SiiNunit\n{{\ncompany_def : .{cid} {{\n city: {cid}\n prefab: d_cust_1w1\n}}\n}}\n', encoding="utf-8")

    # Incluir también empresas base para compatibilidad con prefabs importados
    base_company_sii = BASE_DIR / "scratch" / "def" / "def" / "company.sii"
    if base_company_sii.exists():
        with open(base_company_sii, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                line_s = line.strip()
                if line_s.startswith("@include") and line_s not in master_includes:
                    master_includes.append(line_s)

    master_path = DEF_DIR / "company.sii"
    master_content = "SiiNunit\n{\n" + "\n".join(master_includes) + "\n}\n"
    with open(master_path, "w", encoding="utf-8") as f:
        f.write(master_content)

    old_master = DEF_DIR / "company.chile.sii"
    if old_master.exists():
        old_master.unlink()

    print(f"-> {len(master_includes)} empresas registradas en def/company.sii con sucursales e in/out de cargas")


def generar_cargas():
    """Genera las definiciones de cargas chilenas en def/cargo/ y def/cargo.sii"""
    cargo_dir = DEF_DIR / "cargo"
    cargo_dir.mkdir(parents=True, exist_ok=True)

    master_includes = []

    for cargo_id, cdata in CARGAS_CHILENAS.items():
        master_includes.append(f'@include "cargo/{cargo_id}.sui"')

        sui_path = cargo_dir / f"{cargo_id}.sui"
        valiosa_flag = "true" if cdata["valiosa"] else "false"

        # Compatibilidad de remolques según tipo de carga
        if cdata["grupo"] == "adr_liquid" or cdata["grupo"] == "liquid":
            body_types_str = "    body_types[]: fueltank\n    body_types[]: foodtank"
        elif cdata["grupo"] == "refrigerated":
            body_types_str = "    body_types[]: refrigerated\n    body_types[]: insulated\n    body_types[]: dryvan"
        elif cdata["grupo"] == "bulk":
            body_types_str = "    body_types[]: flatbed\n    body_types[]: dryvan\n    body_types[]: curtainside"
        else:
            body_types_str = "    body_types[]: curtainside\n    body_types[]: dryvan\n    body_types[]: container"

        content = f"""cargo_data : cargo.{cargo_id}
{{
    name: "{cdata['nombre']}"
    fragility: {cdata['fragilidad']}
    valuable: {valiosa_flag}
    group[]: {cdata['grupo']}
    mass: {cdata['masa']}.0
    unit_reward_per_km: 0.35
    unit_load_time: 40
{body_types_str}
}}
"""
        with open(sui_path, "w", encoding="utf-8") as f:
            f.write(content)

    # Incluir también cargas del juego base para abastecer los comercios importados
    base_cargo_sii = BASE_DIR / "scratch" / "def" / "def" / "cargo.sii"
    if base_cargo_sii.exists():
        with open(base_cargo_sii, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                line_s = line.strip()
                if line_s.startswith("@include") and line_s not in master_includes:
                    master_includes.append(line_s)

    master_path = DEF_DIR / "cargo.sii"
    master_content = "SiiNunit\n{\n" + "\n".join(master_includes) + "\n}\n"
    with open(master_path, "w", encoding="utf-8") as f:
        f.write(master_content)

    old_master = DEF_DIR / "cargo.chile.sii"
    if old_master.exists():
        old_master.unlink()

    print(f"-> {len(master_includes)} cargas registradas en def/cargo.sii (chilenas y catálogo base)")


def generar_pais():
    """Genera def/country.sii y las 16 regiones de Chile en def/country/ (mapa standalone puro)"""
    country_dir = DEF_DIR / "country"
    country_dir.mkdir(parents=True, exist_ok=True)

    master_includes = [
        '@include "country/chile.sui"',
        '@include "country/chile/license_plates.sui"'
    ]

    # 1. País principal Chile (sin etiqueta de texto visible para evitar superposición con Región Metropolitana)
    chile_sui_path = country_dir / "chile.sui"
    chile_content = """country_data : country.data.chile
{
    country_id: 100
    name: ""
    name_localized: ""
    country_code: "CL"
    iso_country_code: chl

    pos: (-28000, 0, -12000)

    fuel_price: 1.15

    lights_mandatory: true
    left_hand_traffic: false
    driving_tired_offence: true

    time_zone: -180 # UTC-3 (Hora Continental)
    time_zone_name: "CLT"

    mass_limit_per_axle_count[]: 18000
    mass_limit_per_axle_count[]: 26000
    mass_limit_per_axle_count[]: 38000
    mass_limit_per_axle_count[]: 44000
    mass_limit_per_axle_count[]: 45000
}
"""
    with open(chile_sui_path, "w", encoding="utf-8") as f:
        f.write(chile_content)

    # 2. Las 16 Regiones de Chile como entidades territoriales en el mapa
    for reg_code, rinfo in CONFIG_REGIONES.items():
        reg_id = rinfo["id"]
        reg_sui_path = country_dir / f"{reg_id}.sui"
        master_includes.append(f'@include "country/{reg_id}.sui"')

        reg_content = f"""country_data : country.data.{reg_id}
{{
    country_id: {rinfo["num"]}
    name: "{rinfo["nombre"]}"
    name_localized: "{rinfo["nombre"]}"
    country_code: "{rinfo["code"]}"
    iso_country_code: chl

    pos: ({rinfo["pos"][0]}, {rinfo["pos"][1]}, {rinfo["pos"][2]})

    fuel_price: 1.15

    lights_mandatory: true
    left_hand_traffic: false
    driving_tired_offence: true

    time_zone: -180
    time_zone_name: "CLT"

    mass_limit_per_axle_count[]: 18000
    mass_limit_per_axle_count[]: 26000
    mass_limit_per_axle_count[]: 38000
    mass_limit_per_axle_count[]: 44000
    mass_limit_per_axle_count[]: 45000
}}
"""
        with open(reg_sui_path, "w", encoding="utf-8") as f:
            f.write(reg_content)

    # Master country.sii
    master_path = DEF_DIR / "country.sii"
    master_content = "SiiNunit\n{\n" + "\n".join(master_includes) + "\n}\n"
    with open(master_path, "w", encoding="utf-8") as f:
        f.write(master_content)

    old_master = DEF_DIR / "country.chile.sii"
    if old_master.exists():
        old_master.unlink()

    print("-> 16 Regiones de Chile generadas en def/country/ y def/country.sii con coordenadas geográficas")


def desactivar_dlcs_europa():
    """Neutraliza ciudades y países de DLCs europeos (Iberia, Escandinavia, Halloween, etc.)"""
    dlc_files = [
        DEF_DIR / "country.halloween.sii",
        DEF_DIR / "city.halloween.sii",
        DEF_DIR / "city.iberia.sii",
        DEF_DIR / "city.balkan_e.sii",
        DEF_DIR / "city.balkan_w.sii",
        DEF_DIR / "city.balt.sii",
        DEF_DIR / "city.it.sii",
        DEF_DIR / "city.fr.sii",
        DEF_DIR / "city.east.sii",
        DEF_DIR / "city.north.sii",
    ]
    empty_content = "SiiNunit\n{\n}\n"
    for dlc_f in dlc_files:
        with open(dlc_f, "w", encoding="utf-8") as f:
            f.write(empty_content)
    print("-> 10 módulos de DLCs europeos neutralizados (garantiza mapa 100% chileno sin Brackenreach)")


def generar_estaciones_servicio():
    """Genera definiciones de las estaciones de servicio más icónicas de Chile (Copec, Shell, Petrobras, Aramco)"""
    world_dir = DEF_DIR / "world"
    world_dir.mkdir(parents=True, exist_ok=True)

    gas_content = """SiiNunit
{
# ==============================================================================
# RED OFICIAL DE ESTACIONES DE SERVICIO EN CARRETERAS Y RUTAS DE CHILE
# ==============================================================================

# Copec - Red Líder de Chile (Tiendas Pronto en Autopistas y Punto en Ciudades)
gasoline_station : gas.copec
{
    name: "Copec Pronto"
    fuel_price: 1.05
}

gasoline_station : gas.copec_pronto
{
    name: "Copec Pronto"
    fuel_price: 1.05
}

gasoline_station : gas.copec_punto
{
    name: "Copec Punto"
    fuel_price: 1.05
}

# Shell Enex Chile - Tiendas Upa! / Upita
gasoline_station : gas.shell_cl
{
    name: "Shell Upa!"
    fuel_price: 1.06
}

gasoline_station : gas.shell_upa
{
    name: "Shell Upa!"
    fuel_price: 1.06
}

# Petrobras Chile (Esmax) - Tiendas Spacio 1
gasoline_station : gas.petrobras
{
    name: "Petrobras Spacio 1"
    fuel_price: 1.04
}

gasoline_station : gas.petrobras_spacio
{
    name: "Petrobras Spacio 1"
    fuel_price: 1.04
}

# Aramco Chile - Presencia Nacional
gasoline_station : gas.aramco
{
    name: "Aramco Chile"
    fuel_price: 1.05
}

# Fallbacks retrocompatibles para prefabs de gasolineras importadas
gasoline_station : gas.primel
{
    name: "Copec Pronto"
    fuel_price: 1.05
}

gasoline_station : gas.bts
{
    name: "Copec Punto"
    fuel_price: 1.05
}

gasoline_station : gas.pegi
{
    name: "Shell Upa!"
    fuel_price: 1.06
}

gasoline_station : gas.tqg
{
    name: "Shell Chile"
    fuel_price: 1.06
}

gasoline_station : gas.nada
{
    name: "Petrobras Spacio 1"
    fuel_price: 1.04
}

gasoline_station : gas.apus
{
    name: "Aramco Chile"
    fuel_price: 1.05
}
}
"""
    (world_dir / "gasoline_station.sii").write_text(gas_content, encoding="utf-8")
    (world_dir / "gasoline_station.chile.sii").write_text(gas_content, encoding="utf-8")
    print("-> Red Copec, Shell, Petrobras y Aramco registrada en def/world/gasoline_station*.sii")


def generar_locales():
    """Genera diccionarios de localización en locale/*/locale.sii para ciudades, avenidas y gasolineras"""
    idiomas = ["es_es", "es_la", "en_us"]
    loc_lines = []

    for reg_code, reg_info in REGIONES_CHILE.items():
        for ciudad in reg_info["ciudades"]:
            cid = ciudad["id"]
            cname = ciudad["nombre"]
            loc_lines.append(f'    key[]: "{cid}"\n    val[]: "{cname}"')

    loc_content = "SiiNunit\n{\nlocalization_db : .localization\n{\n" + "\n".join(loc_lines) + "\n}\n}\n"

    for lang in idiomas:
        ldir = BASE_DIR / "locale" / lang
        ldir.mkdir(parents=True, exist_ok=True)
        (ldir / "locale.sii").write_text(loc_content, encoding="utf-8")

    print(f"-> Localización de 52 ciudades y avenidas generada en {len(idiomas)} idiomas (locale/)")


def main():
    print("================================================================")
    print(" TRANSPORTE AUSTRAL - GENERADOR DE DEFINICIONES DE CHILE (ETS2)")
    print("================================================================")
    generar_pais()
    generar_ciudades()
    generar_empresas()
    generar_cargas()
    generar_estaciones_servicio()
    generar_locales()
    desactivar_dlcs_europa()
    print("================================================================")
    print("Todas las definiciones se han generado correctamente.")


if __name__ == "__main__":
    main()

