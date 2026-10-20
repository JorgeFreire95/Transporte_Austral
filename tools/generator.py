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
import shutil
from pathlib import Path

# Directorio raíz del proyecto
BASE_DIR = Path(__file__).resolve().parent.parent
DEF_DIR = BASE_DIR / "def"

# ==============================================================================
# BASE DE DATOS: 16 REGIONES DE CHILE Y SUS 52 COMUNAS
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
                "empresas": ["copec", "tpa_arica", "embonor", "unimarc", "lider", "starken", "chilexpress"]
            },
            {
                "id": "putre",
                "nombre": "Putre (Paso Chungará - Ruta 11-CH)",
                "x": -116400, "z": 83200,
                "icon": "putre",
                "empresas": ["copec", "tpa_arica"]
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
                "empresas": ["copec", "shell_cl", "sqm", "unimarc", "lider", "embonor", "starken"]
            },
            {
                "id": "pozo_almonte",
                "nombre": "Pozo Almonte (Panamericana - Salitreras)",
                "x": -116900, "z": 93500,
                "icon": "pozo_almonte",
                "empresas": ["copec", "sqm"]
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
                "empresas": ["copec", "shell_cl", "escondida", "sqm", "codelco", "lider", "sodimac", "falabella", "andina", "starken", "bluex"]
            },
            {
                "id": "calama",
                "nombre": "Calama (Av. Granaderos - Chuquicamata)",
                "x": -115400, "z": 101000,
                "icon": "calama",
                "empresas": ["codelco", "copec", "shell_cl", "sodimac", "unimarc", "lider", "sqm"]
            },
            {
                "id": "san_pedro",
                "nombre": "San Pedro de Atacama (Caracoles - Valle de la Luna)",
                "x": -113800, "z": 102500,
                "icon": "san_pedro",
                "empresas": ["copec", "sqm"]
            },
            {
                "id": "mejillones",
                "nombre": "Mejillones (Av. Fertilizantes - Puerto)",
                "x": -118150, "z": 103200,
                "icon": "mejillones",
                "empresas": ["petrobras_cl", "sqm", "escondida", "enap"]
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
                "empresas": ["copec", "shell_cl", "cap_acero", "sodimac", "lider", "cencosud"]
            },
            {
                "id": "caldera",
                "nombre": "Caldera (Costanera - Bahía Inglesa)",
                "x": -118200, "z": 116500,
                "icon": "caldera",
                "empresas": ["copec", "cap_acero"]
            },
            {
                "id": "vallenar",
                "nombre": "Vallenar (Av. Brasil - Valle del Huasco)",
                "x": -116400, "z": 124000,
                "icon": "vallenar",
                "empresas": ["copec", "cap_acero", "unimarc"]
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
                "empresas": ["copec", "shell_cl", "cencosud", "falabella", "lider", "sodimac", "unimarc", "starken"]
            },
            {
                "id": "coquimbo",
                "nombre": "Coquimbo (Av. Costanera - Puerto)",
                "x": -117350, "z": 136200,
                "icon": "coquimbo",
                "empresas": ["copec", "cencosud", "unimarc", "sodimac"]
            },
            {
                "id": "ovalle",
                "nombre": "Ovalle (Av. Ariztía - Valle del Limarí)",
                "x": -116100, "z": 140000,
                "icon": "ovalle",
                "empresas": ["copec", "concha_toro", "unimarc"]
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
                "empresas": ["copec", "tps_valp", "falabella", "lider", "starken", "chilexpress", "correos_cl"]
            },
            {
                "id": "vina_del_mar",
                "nombre": "Viña del Mar (Av. Libertad - 1 Norte)",
                "x": -116900, "z": 157200,
                "icon": "vina_del_mar",
                "empresas": ["copec", "shell_cl", "enap", "cencosud", "lider", "sodimac", "embonor", "ripley"]
            },
            {
                "id": "san_antonio",
                "nombre": "San Antonio (Av. Barros Luco - Puerto STI)",
                "x": -117200, "z": 162000,
                "icon": "san_antonio",
                "empresas": ["copec", "sti_san_ant", "melon", "andina", "lider", "sodimac", "petrobras_cl"]
            },
            {
                "id": "los_andes",
                "nombre": "Los Andes (Av. Santa Teresa - Paso Los Libertadores)",
                "x": -114800, "z": 156500,
                "icon": "los_andes",
                "empresas": ["codelco", "copec", "dole_cl", "melon", "unimarc", "sodimac"]
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
                "empresas": ["copec", "shell_cl", "petrobras", "aramco", "falabella", "lider", "cencosud", "sodimac", "andina", "ccu", "starken", "chilexpress", "correos_cl", "bluex", "unimarc", "ripley"]
            },
            {
                "id": "san_bernardo",
                "nombre": "San Bernardo (Av. Portales - Eje Sur)",
                "x": -115700, "z": 162500,
                "icon": "san_bernardo",
                "empresas": ["carozzi", "falabella", "soprole", "molymet", "sodimac", "lider", "copec", "agrosuper"]
            },
            {
                "id": "quilicura",
                "nombre": "Quilicura (Américo Vespucio - Panamericana Norte)",
                "x": -115900, "z": 158500,
                "icon": "quilicura",
                "empresas": ["ideal_cl", "bluex", "falabella", "sodimac", "lider", "polpaico", "copec", "petrobras_cl"]
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
                "empresas": ["codelco", "agrosuper", "copec", "shell_cl", "cencosud", "lider", "sodimac", "dole_cl"]
            },
            {
                "id": "san_fernando",
                "nombre": "San Fernando (Av. Manuel Rodríguez)",
                "x": -115300, "z": 169000,
                "icon": "san_fernando",
                "empresas": ["copec", "concha_toro", "dole_cl", "unimarc"]
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
                "empresas": ["copec", "shell_cl", "aramco", "cbb_cemento", "lider", "sodimac", "cencosud", "embonor", "starken"]
            },
            {
                "id": "curico",
                "nombre": "Curicó (Av. Manso de Velasco - Alameda)",
                "x": -115100, "z": 172000,
                "icon": "curico",
                "empresas": ["copec", "concha_toro", "cbb_cemento", "dole_cl", "carozzi", "lider"]
            },
            {
                "id": "linares",
                "nombre": "Linares (Av. Aníbal León Bustos)",
                "x": -115300, "z": 178000,
                "icon": "linares",
                "empresas": ["copec", "watts", "iansa", "unimarc"]
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
                "empresas": ["copec", "iansa", "lider", "sodimac", "unimarc", "starken", "arauco", "shell_cl"]
            },
            {
                "id": "san_carlos",
                "nombre": "San Carlos (Av. Arturo Prat - Violeta Parra)",
                "x": -114900, "z": 181200,
                "icon": "san_carlos",
                "empresas": ["copec", "iansa"]
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
                "empresas": ["copec", "shell_cl", "petrobras", "cbb_cemento", "cap_acero", "enap", "arauco", "lider", "sodimac", "cencosud", "falabella", "embonor", "starken", "bluex"]
            },
            {
                "id": "talcahuano",
                "nombre": "Talcahuano (Autopista - Puerto San Vicente)",
                "x": -117000, "z": 184200,
                "icon": "talcahuano",
                "empresas": ["copec", "petrobras", "cap_acero", "enap", "cbb_cemento"]
            },
            {
                "id": "los_angeles",
                "nombre": "Los Ángeles (Av. Alemania - Ricardo Vicuña)",
                "x": -115200, "z": 188000,
                "icon": "los_angeles",
                "empresas": ["copec", "cmpc", "arauco", "iansa", "lider", "sodimac"]
            },
            {
                "id": "coronel",
                "nombre": "Coronel (Ruta 160 - Puerto Coronel)",
                "x": -116900, "z": 186800,
                "icon": "coronel",
                "empresas": ["copec", "pto_coronel", "polpaico", "arauco", "unimarc"]
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
                "empresas": ["copec", "shell_cl", "aramco", "colun", "soprole", "lider", "sodimac", "cencosud", "embonor", "starken"]
            },
            {
                "id": "villarrica",
                "nombre": "Villarrica (Av. Pedro de Valdivia - Costanera)",
                "x": -115100, "z": 197000,
                "icon": "villarrica",
                "empresas": ["copec", "unimarc"]
            },
            {
                "id": "angol",
                "nombre": "Angol (Av. O'Higgins - Cordillera de Nahuelbuta)",
                "x": -115800, "z": 190500,
                "icon": "angol",
                "empresas": ["cmpc", "copec", "unimarc"]
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
                "empresas": ["copec", "kunstmann", "colun", "lider", "sodimac", "starken", "shell_cl"]
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
                "empresas": ["copec", "shell_cl", "aquachile", "colun", "soprole", "lider", "sodimac", "cencosud", "melon", "tabsa", "starken", "bluex"]
            },
            {
                "id": "osorno",
                "nombre": "Osorno (Av. Mackenna - Errázuriz)",
                "x": -116200, "z": 206500,
                "icon": "osorno",
                "empresas": ["copec", "colun", "soprole", "watts", "lider", "sodimac"]
            },
            {
                "id": "castro",
                "nombre": "Castro (Palafitos Gamboa - San Martín)",
                "x": -116800, "z": 214500,
                "icon": "castro",
                "empresas": ["copec", "aquachile", "unimarc", "lider"]
            },
            {
                "id": "quellon",
                "nombre": "Quellón (Hito Cero Panamericana)",
                "x": -116700, "z": 218500,
                "icon": "quellon",
                "empresas": ["aquachile", "copec"]
            },
            {
                "id": "chaiten",
                "nombre": "Chaitén (Costanera - Carretera Austral)",
                "x": -115500, "z": 216000,
                "icon": "chaiten",
                "empresas": ["copec", "tabsa"]
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
                "empresas": ["copec", "aquachile", "unimarc", "starken"]
            },
            {
                "id": "puerto_aysen",
                "nombre": "Puerto Aysén (Puente Presidente Ibáñez)",
                "x": -115600, "z": 226500,
                "icon": "puerto_aysen",
                "empresas": ["aquachile", "copec"]
            },
            {
                "id": "cochrane",
                "nombre": "Cochrane (Av. San Valentín - Río Baker)",
                "x": -114200, "z": 236000,
                "icon": "cochrane",
                "empresas": ["copec"]
            },
            {
                "id": "v_ohiggins",
                "nombre": "Villa O'Higgins (Fin Carretera Austral)",
                "x": -113800, "z": 242000,
                "icon": "v_ohiggins",
                "empresas": ["copec"]
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
                "empresas": ["copec", "shell_cl", "enap", "simunovic", "austral_pza", "tabsa", "unimarc", "lider", "sodimac", "starken"]
            },
            {
                "id": "pto_natales",
                "nombre": "Puerto Natales (Costanera Pedro Montt)",
                "x": -113200, "z": 258000,
                "icon": "pto_natales",
                "empresas": ["copec", "tabsa", "unimarc"]
            },
            {
                "id": "porvenir",
                "nombre": "Porvenir (Costanera Chiloé - Tierra del Fuego)",
                "x": -111100, "z": 267000,
                "icon": "porvenir",
                "empresas": ["copec", "tabsa", "simunovic"]
            }
        ]
    }
}

# ==============================================================================
# BASE DE DATOS: 47 EMPRESAS CHILENAS Y ESTACIONES DE SERVICIO
# ==============================================================================
EMPRESAS_CHILENAS = {
    # 1. Red de Combustibles y Estaciones de Servicio
    "copec": {
        "nombre": "Copec - Combustibles y Lubricantes",
        "rubro": "Red de Estaciones de Servicio Copec, Pronto Copec y Punto Copec",
        "cargas_in": ["petrol_ref", "combust_cl", "lubric_cl", "diesel", "petrol", "beverages"],
        "cargas_out": ["combust_cl", "lubric_cl", "diesel", "petrol", "empty_barr"]
    },
    "shell_cl": {
        "nombre": "Shell Enex Chile",
        "rubro": "Red de Estaciones de Servicio Shell y Tiendas Upa! / Upita",
        "cargas_in": ["petrol_ref", "combust_cl", "diesel", "petrol", "lubric_cl", "beverages"],
        "cargas_out": ["combust_cl", "lubric_cl", "diesel", "petrol"]
    },
    "petrobras": {
        "nombre": "Petrobras Chile - Esmax",
        "rubro": "Red de Estaciones de Servicio Petrobras y Tiendas Spacio 1",
        "cargas_in": ["combust_cl", "diesel", "petrol", "lubric_cl", "beverages"],
        "cargas_out": ["combust_cl", "lubric_cl", "diesel", "petrol"]
    },
    "petrobras_cl": {
        "nombre": "Petrobras Chile - Esmax",
        "rubro": "Red de Estaciones de Servicio Petrobras y Tiendas Spacio 1",
        "cargas_in": ["combust_cl", "diesel", "petrol", "lubric_cl", "beverages"],
        "cargas_out": ["combust_cl", "lubric_cl", "diesel", "petrol"]
    },
    "aramco": {
        "nombre": "Aramco Chile",
        "rubro": "Red Global de Combustibles y Estaciones de Servicio Aramco",
        "cargas_in": ["combust_cl", "diesel", "petrol", "lubric_cl", "beverages"],
        "cargas_out": ["combust_cl", "lubric_cl", "diesel", "petrol"]
    },
    "enap": {
        "nombre": "ENAP - Empresa Nacional del Petróleo",
        "rubro": "Refinerías Concón, Biobío y extracción Magallanes",
        "cargas_in": ["petrol_ref", "combust_cl", "chemicals"],
        "cargas_out": ["combust_cl", "petrol_ref", "diesel", "petrol"]
    },

    # 2. Minería, Siderurgia y Química
    "codelco": {
        "nombre": "Codelco Chile - Minería del Cobre",
        "rubro": "División Chuquicamata, El Teniente, Andina y Salvador",
        "cargas_in": ["maq_pesada", "acid_sulf", "cables", "tires"],
        "cargas_out": ["catod_cobre", "conc_cobre"]
    },
    "escondida": {
        "nombre": "Minera Escondida - BHP",
        "rubro": "Mayor yacimiento y producción de cobre a rajo abierto del mundo",
        "cargas_in": ["maq_pesada", "acid_sulf", "tires", "cables"],
        "cargas_out": ["conc_cobre", "catod_cobre"]
    },
    "sqm": {
        "nombre": "SQM - Sociedad Química y Minera de Chile",
        "rubro": "Líder mundial en Litio, Yodo, Nitratos y Nutrición Vegetal",
        "cargas_in": ["chemicals", "maq_pesada", "acid_sulf"],
        "cargas_out": ["fertilizer", "chemicals"]
    },
    "cap_acero": {
        "nombre": "CAP Acero - Compañía Siderúrgica Huachipato y Minería",
        "rubro": "Siderurgia, barras de molienda y minería de hierro CMP",
        "cargas_in": ["chemicals", "cables"],
        "cargas_out": ["metal_beams", "metal_pipes", "re_bars"]
    },
    "molymet": {
        "nombre": "Molymet - Molibdenos y Metales",
        "rubro": "Mayor procesador de concentrados de molibdeno y renio del mundo",
        "cargas_in": ["conc_cobre", "acid_sulf", "chemicals"],
        "cargas_out": ["chemicals", "catod_cobre"]
    },

    # 3. Forestal, Celulosa y Papel
    "arauco": {
        "nombre": "Arauco Celulosa y Maderas",
        "rubro": "Complejo Forestal y Celulosa (MAPA, Constitución, Horcones)",
        "cargas_in": ["tronc_pino", "chemicals"],
        "cargas_out": ["cel_fardo", "mad_aserr"]
    },
    "cmpc": {
        "nombre": "Empresas CMPC",
        "rubro": "Forestal Mininco, Celulosa Pacífico y Papeles del Sur",
        "cargas_in": ["tronc_pino", "combust_cl"],
        "cargas_out": ["cel_fardo", "mad_aserr"]
    },

    # 4. Alimentos, Carnes, Lácteos y Pastas
    "agrosuper": {
        "nombre": "Agrosuper Chile",
        "rubro": "Alimentos (Super Pollo, Super Cerdo, La Crianza, Sopraval)",
        "cargas_in": ["wheat", "barley"],
        "cargas_out": ["carne_fresc", "pork_meat", "beef_meat"]
    },
    "soprole": {
        "nombre": "Soprole - Sano y Rico a Diario",
        "rubro": "Líder lácteo nacional en leche, yogures, mantequillas y postres",
        "cargas_in": ["milk", "sugar", "packaging"],
        "cargas_out": ["leche_sur", "quesos_col", "milk"]
    },
    "colun": {
        "nombre": "Colun - La Magia del Sur",
        "rubro": "Cooperativa Agrícola y Lechera de La Unión (Los Ríos y Los Lagos)",
        "cargas_in": ["milk", "salt"],
        "cargas_out": ["leche_sur", "quesos_col", "milk"]
    },
    "carozzi": {
        "nombre": "Carozzi Alimentos",
        "rubro": "Complejo alimenticio Nos (Pastas Carozzi, Galletas Costa, Ambrosoli)",
        "cargas_in": ["wheat", "barley", "sugar"],
        "cargas_out": ["food", "encomiendas"]
    },
    "iansa": {
        "nombre": "Empresas Iansa",
        "rubro": "Azúcar de remolacha, endulzantes, pastas de tomate y nutrición animal",
        "cargas_in": ["wheat", "barley", "sugar"],
        "cargas_out": ["sugar", "food"]
    },
    "ideal_cl": {
        "nombre": "Panadería Ideal - Grupo Bimbo Chile",
        "rubro": "Producción y distribución de panes de molde, tortillas y bollería",
        "cargas_in": ["wheat", "sugar", "milk"],
        "cargas_out": ["food", "encomiendas"]
    },
    "watts": {
        "nombre": "Watt's Alimentos - Loncoleche",
        "rubro": "Jugos Watt's, mermeladas, margarinas Calo y aceites Chef",
        "cargas_in": ["milk", "sugar", "apples", "oranges"],
        "cargas_out": ["food", "beverages"]
    },
    "simunovic": {
        "nombre": "Frigorífico Simunovic (Punta Arenas)",
        "rubro": "Carnes patagónicas de exportación y cordero magallánico",
        "cargas_in": ["salt", "packaging"],
        "cargas_out": ["carne_fresc", "meat"]
    },
    "dole_cl": {
        "nombre": "Dole Chile Frutícola",
        "rubro": "Exportación de frutas frescas (uvas, manzanas, cerezas, arándanos)",
        "cargas_in": ["packaging", "fertilizer"],
        "cargas_out": ["palta_hass", "apples", "grapes"]
    },
    "aquachile": {
        "nombre": "AquaChile Salmones",
        "rubro": "Líder en acuicultura y exportación de salmón del sur austral",
        "cargas_in": ["food", "packaging"],
        "cargas_out": ["salm_fresco", "fish"]
    },

    # 5. Bebidas, Cervezas y Viñedos
    "ccu": {
        "nombre": "CCU - Compañía de Cervecerías Unidas",
        "rubro": "Cervezas (Cristal, Royal, Escudo), Aguas (Cachantún) y Gaseosas (Bilz, Pap)",
        "cargas_in": ["sugar", "beverages", "bottles"],
        "cargas_out": ["cervez_ccu", "beverages"]
    },
    "andina": {
        "nombre": "Coca-Cola Andina",
        "rubro": "Embotelladora líder de bebidas gaseosas, jugos y aguas minerales",
        "cargas_in": ["sugar", "bottles", "packaging"],
        "cargas_out": ["beverages", "empty_barr"]
    },
    "embonor": {
        "nombre": "Coca-Cola Embonor",
        "rubro": "Embotelladora y distribuidora de bebidas en el norte y sur de Chile",
        "cargas_in": ["sugar", "bottles", "packaging"],
        "cargas_out": ["beverages", "empty_barr"]
    },
    "concha_toro": {
        "nombre": "Viña Concha y Toro",
        "rubro": "Viñedos y exportación de vinos (Casillero del Diablo, Don Melchor)",
        "cargas_in": ["bottles", "grapes"],
        "cargas_out": ["vino_res", "beverages"]
    },
    "kunstmann": {
        "nombre": "Cervecería Kunstmann (Valdivia)",
        "rubro": "Cerveza artesanal de Valdivia (Torobayo, Bock, Gran Torobayo)",
        "cargas_in": ["barley", "bottles"],
        "cargas_out": ["cervez_ccu", "beverages"]
    },
    "austral_pza": {
        "nombre": "Cervecería Austral (Punta Arenas)",
        "rubro": "La cerveza más austral del mundo elaborada con aguas de la Patagonia",
        "cargas_in": ["barley", "bottles", "sugar"],
        "cargas_out": ["cervez_ccu", "beverages"]
    },

    # 6. Retail, Supermercados y Mejoramiento del Hogar
    "lider": {
        "nombre": "Lider - Walmart Chile",
        "rubro": "Cadena de supermercados e hipermercados líder y centro Lo Aguirre",
        "cargas_in": ["food", "carne_fresc", "beverages", "milk", "leche_sur", "encomiendas"],
        "cargas_out": ["encomiendas", "food", "empty_barr"]
    },
    "cencosud": {
        "nombre": "Cencosud (Jumbo / Easy / Santa Isabel)",
        "rubro": "Supermercados Jumbo, Santa Isabel y mejoramiento del hogar Easy",
        "cargas_in": ["food", "carne_fresc", "beverages"],
        "cargas_out": ["encomiendas", "food", "palta_hass"]
    },
    "unimarc": {
        "nombre": "Unimarc - SMU",
        "rubro": "Supermercado de la familia chilena con presencia de Arica a Magallanes",
        "cargas_in": ["food", "carne_fresc", "beverages", "milk"],
        "cargas_out": ["encomiendas", "food"]
    },
    "falabella": {
        "nombre": "Falabella Logística & Retail",
        "rubro": "Grandes tiendas por departamento y Centro Logístico San Bernardo",
        "cargas_in": ["electronics", "clothes", "furniture"],
        "cargas_out": ["encomiendas", "paquet_exp", "furniture"]
    },
    "ripley": {
        "nombre": "Ripley Retail y Logística",
        "rubro": "Tiendas por departamento y Centro de Distribución Pudahuel",
        "cargas_in": ["electronics", "clothes", "furniture"],
        "cargas_out": ["encomiendas", "paquet_exp", "furniture"]
    },
    "sodimac": {
        "nombre": "Homecenter Sodimac / Constructor",
        "rubro": "Mayorista de materiales de construcción, ferretería y hogar",
        "cargas_in": ["cement", "mad_aserr", "cel_fardo", "cables", "metal_pipes"],
        "cargas_out": ["encomiendas", "furniture"]
    },

    # 7. Cemento y Construcción
    "melon": {
        "nombre": "Cemento Melón",
        "rubro": "Producción histórica de cemento La Calera, San Antonio y hormigones",
        "cargas_in": ["chemicals", "sand"],
        "cargas_out": ["cement", "bricks"]
    },
    "cbb_cemento": {
        "nombre": "Cementos Bío Bío - CBB",
        "rubro": "Fabricación de cemento, cal y hormigón en Talcahuano, Curicó y Teno",
        "cargas_in": ["chemicals", "sand"],
        "cargas_out": ["cement", "precast_strs"]
    },
    "polpaico": {
        "nombre": "Cementos Polpaico",
        "rubro": "Plantas de cemento Cerro Blanco Tiltil y molienda Coronel",
        "cargas_in": ["sand", "chemicals"],
        "cargas_out": ["cement", "bricks"]
    },

    # 8. Courier, Encomiendas y Logística Nacional
    "starken": {
        "nombre": "Starken Encomiendas y Logística",
        "rubro": "Transporte de carga express, paquetes y encomiendas en todo Chile",
        "cargas_in": ["encomiendas", "paquet_exp"],
        "cargas_out": ["encomiendas", "paquet_exp"]
    },
    "chilexpress": {
        "nombre": "Chilexpress Courier",
        "rubro": "Logística urgente, paquetería e-commerce y courier nacional",
        "cargas_in": ["paquet_exp", "encomiendas"],
        "cargas_out": ["paquet_exp", "encomiendas"]
    },
    "correos_cl": {
        "nombre": "CorreosChile",
        "rubro": "Empresa de Correos de Chile y Centro Tecnológico Postal",
        "cargas_in": ["encomiendas", "paquet_exp"],
        "cargas_out": ["encomiendas", "paquet_exp"]
    },
    "bluex": {
        "nombre": "Blue Express",
        "rubro": "Distribución y logística express para e-commerce en todo Chile",
        "cargas_in": ["encomiendas", "paquet_exp"],
        "cargas_out": ["encomiendas", "paquet_exp"]
    },

    # 9. Puertos, Terminales y Conectividad Austral
    "tpa_arica": {
        "nombre": "Terminal Puerto Arica (TPA)",
        "rubro": "Puerto multipropósito y conexión internacional del norte grande",
        "cargas_in": ["catod_cobre", "conc_cobre", "palta_hass"],
        "cargas_out": ["machinery", "fertilizer", "chemicals"]
    },
    "sti_san_ant": {
        "nombre": "San Antonio Terminal Internacional (STI)",
        "rubro": "Mayor terminal marítimo y transferencia de contenedores de Chile",
        "cargas_in": ["vino_res", "catod_cobre", "palta_hass", "salm_fresco"],
        "cargas_out": ["cars", "machinery", "electronics"]
    },
    "tps_valp": {
        "nombre": "TPS Valparaíso - Terminal Pacífico Sur",
        "rubro": "Terminal portuario histórico de Valparaíso y fruta de exportación",
        "cargas_in": ["vino_res", "catod_cobre", "palta_hass", "apples"],
        "cargas_out": ["cars", "machinery", "electronics"]
    },
    "pto_coronel": {
        "nombre": "Puerto Coronel",
        "rubro": "Mayor puerto de carga forestal, madera y celulosa del Biobío",
        "cargas_in": ["cel_fardo", "mad_aserr", "tronc_pino"],
        "cargas_out": ["machinery", "fertilizer", "chemicals"]
    },
    "tabsa": {
        "nombre": "TABSA - Transbordadora Austral Broom",
        "rubro": "Conectividad marítima y transbordadores de camiones en Magallanes",
        "cargas_in": ["food", "combust_cl", "encomiendas"],
        "cargas_out": ["food", "combust_cl", "encomiendas"]
    }
}

# ==============================================================================
# REBRANDING INTEGRAL: EMPRESAS DEL JUEGO BASE -> MARCAS CHILENAS CORRESPONDIENTES
# Sustituye permanentemente los nombres europeos en los prefabs del mapa
# ==============================================================================
REBRAND_BASE_COMPANIES = {
    # Red de Combustibles y Estaciones de Servicio
    "primel":          {"nombre": "Copec Pronto", "sort": "COPEC", "trailer": "copec"},
    "bts":             {"nombre": "Copec Punto", "sort": "COPEC", "trailer": "copec"},
    "pegi":            {"nombre": "Shell Upa!", "sort": "SHELL", "trailer": "shell_cl"},
    "tqg":             {"nombre": "Shell Chile", "sort": "SHELL", "trailer": "shell_cl"},
    "nada":            {"nombre": "Petrobras Spacio 1", "sort": "PETROBRAS", "trailer": "petrobras"},
    "apus":            {"nombre": "Aramco Chile", "sort": "ARAMCO", "trailer": "aramco"},
    "itcc":            {"nombre": "ENAP Refinerías", "sort": "ENAP", "trailer": "enap"},
    "itcc_scrap":      {"nombre": "ENAP Maestranza", "sort": "ENAP", "trailer": "enap"},
    "ns_oil":          {"nombre": "ENAP Magallanes", "sort": "ENAP", "trailer": "enap"},

    # Retail, Supermercados y Centros de Distribución
    "eurogoodies":     {"nombre": "Lider - Walmart Chile", "sort": "LIDER", "trailer": "lider"},
    "eurogoodies_grv": {"nombre": "Lider Centro Distribución", "sort": "LIDER", "trailer": "lider"},
    "kaarfor":         {"nombre": "Cencosud (Jumbo / Easy)", "sort": "CENCOSUD", "trailer": "cencosud"},
    "kaarfor_grv":     {"nombre": "Cencosud Centro de Acopio", "sort": "CENCOSUD", "trailer": "cencosud"},
    "sellplan":        {"nombre": "Unimarc Supermercados", "sort": "UNIMARC", "trailer": "unimarc"},
    "sellplan_grv":    {"nombre": "Unimarc Abastecimiento", "sort": "UNIMARC", "trailer": "unimarc"},
    "ika_bohag":       {"nombre": "Falabella Retail", "sort": "FALABELLA", "trailer": "falabella"},
    "sanbuilders":     {"nombre": "Homecenter Sodimac", "sort": "SODIMAC", "trailer": "sodimac"},
    "sanbuilders_grv": {"nombre": "Sodimac Constructor", "sort": "SODIMAC", "trailer": "sodimac"},
    "sanbuild_hal":    {"nombre": "Sodimac Ferretería", "sort": "SODIMAC", "trailer": "sodimac"},
    "sanbuild_hms":    {"nombre": "Sodimac Maderas", "sort": "SODIMAC", "trailer": "sodimac"},
    "sanbuild_win":    {"nombre": "Sodimac Materiales", "sort": "SODIMAC", "trailer": "sodimac"},
    "eumefa":          {"nombre": "Sodimac Homecenter", "sort": "SODIMAC", "trailer": "sodimac"},
    "renar":           {"nombre": "Cencosud Logística", "sort": "CENCOSUD", "trailer": "cencosud"},
    "renat":           {"nombre": "Lider Logística", "sort": "LIDER", "trailer": "lider"},

    # Courier, Logística y Encomiendas Express
    "lkwlog":          {"nombre": "Starken Encomiendas", "sort": "STARKEN", "trailer": "starken"},
    "tradeaux_grv":    {"nombre": "Starken Carga Pesada", "sort": "STARKEN", "trailer": "starken"},
    "gnt":             {"nombre": "Starken Centro de Acopio", "sort": "STARKEN", "trailer": "starken"},
    "posped":          {"nombre": "Chilexpress Courier", "sort": "CHILEXPRESS", "trailer": "chilexpress"},
    "posped_grv":      {"nombre": "Chilexpress Logística", "sort": "CHILEXPRESS", "trailer": "chilexpress"},
    "tradeaux":        {"nombre": "Chilexpress Express", "sort": "CHILEXPRESS", "trailer": "chilexpress"},
    "rt_log":          {"nombre": "Chilexpress Hub", "sort": "CHILEXPRESS", "trailer": "chilexpress"},
    "transinet":       {"nombre": "Blue Express", "sort": "BLUEX", "trailer": "bluex"},
    "transinet_grv":   {"nombre": "Blue Express Hub", "sort": "BLUEX", "trailer": "bluex"},
    "cargotras":       {"nombre": "Blue Express Carga", "sort": "BLUEX", "trailer": "bluex"},

    # Bebidas, Cervezas y Embotelladoras
    "shuttle":         {"nombre": "Coca-Cola Andina", "sort": "ANDINA", "trailer": "andina"},
    "nbfc":            {"nombre": "Coca-Cola Embonor", "sort": "EMBONOR", "trailer": "embonor"},
    "stokes":          {"nombre": "CCU Cervezas y Bebidas", "sort": "CCU", "trailer": "ccu"},
    "polar":           {"nombre": "Cervecería Austral Patagonia", "sort": "AUSTRAL", "trailer": "austral_pza"},
    "scout":           {"nombre": "Viña Concha y Toro", "sort": "CONCHA_TORO", "trailer": "concha_toro"},

    # Alimentos, Carnes, Lácteos y Frutas
    "euroacres":       {"nombre": "Agrosuper Chile", "sort": "AGROSUPER", "trailer": "agrosuper"},
    "euroacres_grv":   {"nombre": "Agrosuper Faenadora", "sort": "AGROSUPER", "trailer": "agrosuper"},
    "trameri":         {"nombre": "Colun - La Magia del Sur", "sort": "COLUN", "trailer": "colun"},
    "trameri_grv":     {"nombre": "Colun Planta Lechera", "sort": "COLUN", "trailer": "colun"},
    "fcp":             {"nombre": "Soprole Lácteos", "sort": "SOPROLE", "trailer": "soprole"},
    "fcp_grv":         {"nombre": "Soprole Acopio Sur", "sort": "SOPROLE", "trailer": "soprole"},
    "bcp":             {"nombre": "Carozzi Alimentos", "sort": "CAROZZI", "trailer": "carozzi"},
    "bcp_grv":         {"nombre": "Carozzi Molienda", "sort": "CAROZZI", "trailer": "carozzi"},
    "dfh":             {"nombre": "Empresas Iansa", "sort": "IANSA", "trailer": "iansa"},
    "bhv":             {"nombre": "Frigorífico Simunovic Patagonia", "sort": "SIMUNOVIC", "trailer": "simunovic"},
    "polar_fish":      {"nombre": "AquaChile Salmones del Sur", "sort": "AQUACHILE", "trailer": "aquachile"},
    "globe_eur":       {"nombre": "Dole Chile Frutícola", "sort": "DOLE", "trailer": "dole_cl"},
    "fallow":          {"nombre": "Panadería Ideal Bimbo", "sort": "IDEAL", "trailer": "ideal_cl"},
    "drekkar":         {"nombre": "Watt's Alimentos", "sort": "WATTS", "trailer": "watts"},
    "agronord":        {"nombre": "Watt's Loncoleche", "sort": "WATTS", "trailer": "watts"},

    # Minería, Siderurgia y Química
    "quarry":          {"nombre": "Codelco Minería del Cobre", "sort": "CODELCO", "trailer": "codelco"},
    "quarry_grv":      {"nombre": "Codelco Chancado", "sort": "CODELCO", "trailer": "codelco"},
    "steinbr_str":     {"nombre": "Minera Escondida (BHP)", "sort": "ESCONDIDA", "trailer": "escondida"},
    "wgcc":            {"nombre": "SQM Salar de Atacama", "sort": "SQM", "trailer": "sqm"},
    "kathode":         {"nombre": "CAP Acero Huachipato", "sort": "CAP", "trailer": "cap_acero"},
    "ns_chem":         {"nombre": "Molymet Molibdenos y Metales", "sort": "MOLYMET", "trailer": "molymet"},

    # Forestal y Madera
    "tree_et":         {"nombre": "Arauco Celulosa y Maderas", "sort": "ARAUCO", "trailer": "arauco"},
    "tree_et_log":     {"nombre": "Arauco Aserraderos", "sort": "ARAUCO", "trailer": "arauco"},
    "tree_et_grv":     {"nombre": "Arauco Bosques", "sort": "ARAUCO", "trailer": "arauco"},
    "scs_paper":       {"nombre": "CMPC Celulosa y Papeles", "sort": "CMPC", "trailer": "cmpc"},
    "viljo_paper":     {"nombre": "CMPC Forestal Mininco", "sort": "CMPC", "trailer": "cmpc"},

    # Cemento y Construcción
    "sanbuild_cem":    {"nombre": "Cemento Melón", "sort": "MELON", "trailer": "melon"},
    "sanbuild_bas":    {"nombre": "Cementos Bío Bío (CBB)", "sort": "CBB", "trailer": "cbb_cemento"},
    "brawen":          {"nombre": "Melón Hormigones", "sort": "MELON", "trailer": "melon"},
    "batisse":         {"nombre": "Cementos Polpaico", "sort": "POLPAICO", "trailer": "polpaico"},
    "batisse_hs":      {"nombre": "Cementos Polpaico Planta", "sort": "POLPAICO", "trailer": "polpaico"},

    # Puertos y Conectividad Marítima
    "euroflow":        {"nombre": "Puerto San Antonio (STI)", "sort": "STI", "trailer": "sti_san_ant"},
    "cont_port":       {"nombre": "Puerto Valparaíso (TPS)", "sort": "TPS", "trailer": "tps_valp"},
    "subse":           {"nombre": "Puerto Valparaíso Terminal", "sort": "TPS", "trailer": "tps_valp"},
    "cont_port_it":    {"nombre": "Puerto Coronel", "sort": "CORONEL", "trailer": "pto_coronel"},
    "marina":          {"nombre": "TABSA Transbordadores Austral", "sort": "TABSA", "trailer": "tabsa"},
    "gallia_ferry":    {"nombre": "TABSA Barcazas Patagonia", "sort": "TABSA", "trailer": "tabsa"},
    "eolo_lines":      {"nombre": "Naviera Transmarchilay", "sort": "TABSA", "trailer": "tabsa"},
    "polarislines":    {"nombre": "Naviera Navimag Ferries", "sort": "TABSA", "trailer": "tabsa"},
}

# ==============================================================================
# BASE DE DATOS: CARGAS CHILENAS (TOKENS <= 12 CARACTERES PARA MOTOR SCS)
# Con pagos proporcionales a peso, tipo de carga y distancia
# ==============================================================================
CARGAS_CHILENAS = {
    # 1. Cargas Pesadas y Minería (24 - 28.5 Toneladas)
    "maq_pesada": {
        "nombre": "Maquinaria Pesada Minera Cat/Komatsu",
        "masa_total_ton": 28.5,
        "volume": 50,
        "mass": 28500.0,
        "unit_reward_per_km": 28.5,
        "fragilidad": 0.5,
        "valiosa": True,
        "grupo": "machinery"
    },
    "conc_cobre": {
        "nombre": "Concentrado de Cobre a Granel",
        "masa_total_ton": 27.2,
        "volume": 2.6,
        "mass": 850.0,
        "unit_reward_per_km": 0.95,
        "fragilidad": 0.1,
        "valiosa": True,
        "grupo": "bulk"
    },
    "catod_cobre": {
        "nombre": "Cátodos de Cobre de Alta Pureza",
        "masa_total_ton": 24.0,
        "volume": 40,
        "mass": 12000.0,
        "unit_reward_per_km": 15.2,
        "fragilidad": 0.2,
        "valiosa": True,
        "grupo": "machinery"
    },

    # 2. Combustibles y Químicos ADR (26 Toneladas - Alta Peligrosidad)
    "combust_cl": {
        "nombre": "Gasolinas 93/97 y Diésel Copec",
        "masa_total_ton": 26.0,
        "volume": 1,
        "mass": 866.0,
        "unit_reward_per_km": 1.25,
        "adr_class": 3,
        "fragilidad": 0.8,
        "valiosa": True,
        "grupo": "adr_liquid"
    },
    "petrol_ref": {
        "nombre": "Petróleo Crudo y Refinado ENAP",
        "masa_total_ton": 26.0,
        "volume": 1,
        "mass": 866.0,
        "unit_reward_per_km": 1.22,
        "adr_class": 3,
        "fragilidad": 0.8,
        "valiosa": True,
        "grupo": "adr_liquid"
    },
    "acid_sulf": {
        "nombre": "Ácido Sulfúrico Minero en Cisterna",
        "masa_total_ton": 26.0,
        "volume": 1,
        "mass": 1040.0,
        "unit_reward_per_km": 1.48,
        "adr_class": 8,
        "fragilidad": 0.9,
        "valiosa": True,
        "grupo": "adr_liquid"
    },

    # 3. Líquidos Alimenticios y Refrigerados Especializados (18 - 25 Toneladas)
    "leche_sur": {
        "nombre": "Leche Fresca en Cisterna Colun",
        "masa_total_ton": 25.0,
        "volume": 1,
        "mass": 1000.0,
        "unit_reward_per_km": 1.05,
        "fragilidad": 0.3,
        "valiosa": False,
        "grupo": "liquid"
    },
    "salm_fresco": {
        "nombre": "Salmón Atlántico Fresco en Hielo",
        "masa_total_ton": 18.9,
        "volume": 2.6,
        "mass": 590.0,
        "unit_reward_per_km": 0.82,
        "fragilidad": 0.8,
        "valiosa": True,
        "grupo": "refrigerated"
    },
    "vino_res": {
        "nombre": "Vino Chileno Reserva Embotellado",
        "masa_total_ton": 18.4,
        "volume": 2.6,
        "mass": 575.0,
        "unit_reward_per_km": 0.76,
        "fragilidad": 0.7,
        "valiosa": True,
        "grupo": "containers"
    },
    "carne_fresc": {
        "nombre": "Carnes Frescas y Cecinas Agrosuper",
        "masa_total_ton": 21.9,
        "volume": 2.6,
        "mass": 685.0,
        "unit_reward_per_km": 0.70,
        "fragilidad": 0.6,
        "valiosa": False,
        "grupo": "refrigerated"
    },
    "palta_hass": {
        "nombre": "Paltas Hass Chilenas de Exportación",
        "masa_total_ton": 17.4,
        "volume": 2.6,
        "mass": 545.0,
        "unit_reward_per_km": 0.66,
        "fragilidad": 0.6,
        "valiosa": True,
        "grupo": "refrigerated"
    },
    "quesos_col": {
        "nombre": "Quesos y Mantequillas Colun",
        "masa_total_ton": 16.0,
        "volume": 2.6,
        "mass": 500.0,
        "unit_reward_per_km": 0.54,
        "fragilidad": 0.4,
        "valiosa": False,
        "grupo": "refrigerated"
    },

    # 4. Forestal y Materiales (21 - 25 Toneladas)
    "tronc_pino": {
        "nombre": "Trozas y Troncos de Pino Arauco",
        "masa_total_ton": 25.0,
        "volume": 2.6,
        "mass": 780.0,
        "unit_reward_per_km": 0.60,
        "fragilidad": 0.1,
        "valiosa": False,
        "grupo": "bulk"
    },
    "cel_fardo": {
        "nombre": "Fardos de Celulosa Kraft Arauco/CMPC",
        "masa_total_ton": 22.4,
        "volume": 2.6,
        "mass": 700.0,
        "unit_reward_per_km": 0.62,
        "fragilidad": 0.1,
        "valiosa": False,
        "grupo": "bulk"
    },
    "mad_aserr": {
        "nombre": "Madera Aserrada y Tableros MDF",
        "masa_total_ton": 21.0,
        "volume": 2.6,
        "mass": 655.0,
        "unit_reward_per_km": 0.58,
        "fragilidad": 0.2,
        "valiosa": False,
        "grupo": "bulk"
    },

    # 5. Comercio, Bebidas y Cargas Generales (17 - 19 Toneladas)
    "cervez_ccu": {
        "nombre": "Cervezas CCU Cristal y Aguas Minerales",
        "masa_total_ton": 18.9,
        "volume": 2.6,
        "mass": 590.0,
        "unit_reward_per_km": 0.55,
        "fragilidad": 0.5,
        "valiosa": False,
        "grupo": "containers"
    },
    "lubric_cl": {
        "nombre": "Lubricantes y Aceites Mobil/Copec",
        "masa_total_ton": 17.9,
        "volume": 2.6,
        "mass": 560.0,
        "unit_reward_per_km": 0.52,
        "fragilidad": 0.3,
        "valiosa": False,
        "grupo": "containers"
    },

    # 6. Encomiendas y Courier Liviano (7 - 12 Toneladas)
    "encomiendas": {
        "nombre": "Cargas Express y Encomiendas Starken",
        "masa_total_ton": 12.0,
        "volume": 2.6,
        "mass": 375.0,
        "unit_reward_per_km": 0.44,
        "fragilidad": 0.4,
        "valiosa": False,
        "grupo": "containers"
    },
    "paquet_exp": {
        "nombre": "Paquetería Courier y Documentos Chilexpress",
        "masa_total_ton": 7.0,
        "volume": 2.6,
        "mass": 220.0,
        "unit_reward_per_km": 0.35,
        "fragilidad": 0.3,
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

# Concesionarios oficiales para las 52 ciudades de Chile (elimina errores de missing brand en prefabs del mapa)
CIUDAD_BRANDS = {
    # 16 Capitales Regionales (Concesionarios principales verificados)
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

    # Comunas con concesionarios importados en sectores del mapa
    "vallenar": "mercedes",
    "porvenir": "iveco",
    "quilicura": "scania",
    "san_bernardo": "renault",
    "ovalle": "daf",
    "vina_del_mar": "volvo",
    "pto_natales": "iveco",
    "mejillones": "scania",
    "puerto_aysen": "daf",
    "cochrane": "man",
    "coquimbo": "mercedes",
    "quellon": "mercedes",
    "osorno": "man",
    "putre": "scania",
    "san_fernando": "iveco",
    "coronel": "mercedes",
    "los_angeles": "iveco",
    "caldera": "volvo",
    "castro": "daf",

    # Demás comunas de la red vial chilena
    "pozo_almonte": "volvo",
    "calama": "man",
    "san_pedro": "scania",
    "los_vilos": "renault",
    "san_antonio": "daf",
    "los_andes": "scania",
    "santa_cruz": "renault",
    "curico": "volvo",
    "linares": "mercedes",
    "constitucion": "man",
    "san_carlos": "daf",
    "talcahuano": "mercedes",
    "villarrica": "scania",
    "angol": "renault",
    "la_union": "volvo",
    "chaiten": "iveco",
    "v_ohiggins": "man",
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
            cname = ciudad["nombre"].split(" (")[0].strip()
            master_includes.append(f'@include "city/{cid}.sui"')

            sui_path = city_dir / f"{cid}.sui"
            brand_str = f'\n    vehicle_brands[]: "{CIUDAD_BRANDS[cid]}"' if cid in CIUDAD_BRANDS else ""
            content = f"""city_data : city.{cid}
{{
    city_name: "{cname}"
    city_name_localized: "{cname}"
    country: chile{brand_str}

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

    # 1. Generar definiciones de las 47 empresas chilenas
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

        # Generar carpetas in/ y out/ para cargas de transporte
        in_dir = company_dir / comp_id / "in"
        if in_dir.exists():
            shutil.rmtree(in_dir)
        in_dir.mkdir(parents=True, exist_ok=True)
        for cargo_in in comp_data.get("cargas_in", []):
            cargo_sii = in_dir / f"{cargo_in}.sii"
            cargo_sii.write_text(f'SiiNunit\n{{\ncargo_def : .{cargo_in} {{\n cargo: "cargo.{cargo_in}"\n}}\n}}\n', encoding="utf-8")

        out_dir = company_dir / comp_id / "out"
        if out_dir.exists():
            shutil.rmtree(out_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        for cargo_out in comp_data.get("cargas_out", []):
            cargo_sii = out_dir / f"{cargo_out}.sii"
            cargo_sii.write_text(f'SiiNunit\n{{\ncargo_def : .{cargo_out} {{\n cargo: "cargo.{cargo_out}"\n}}\n}}\n', encoding="utf-8")

        # Generar sucursales activas en editor/ para las comunas y estaciones de servicio
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

    # 2. REBRANDING DE EMPRESAS BASE: Sustituye todos los prefabs importados con nombres chilenos
    for base_id, bdata in REBRAND_BASE_COMPANIES.items():
        sui_path = company_dir / f"{base_id}.sui"
        b_content = f"""company_permanent : company.permanent.{base_id}
{{
    name: "{bdata['nombre']}"
    sort_name: "{bdata['sort']}"
    trailer_look: "{bdata['trailer']}"
}}
"""
        with open(sui_path, "w", encoding="utf-8") as f:
            f.write(b_content)

        inc = f'@include "company/{base_id}.sui"'
        if inc not in master_includes:
            master_includes.append(inc)

    # Incluir también empresas base restantes para compatibilidad con prefabs importados
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

    # Limpiar cualquier cargo sui viejo que exceda 12 caracteres
    for old_sui in cargo_dir.glob("*.sui"):
        if len(old_sui.stem) > 12:
            old_sui.unlink()

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
        elif cdata["grupo"] == "machinery":
            body_types_str = "    body_types[]: lowboy\n    body_types[]: lowbed\n    body_types[]: flatbed"
        else:
            body_types_str = "    body_types[]: curtainside\n    body_types[]: dryvan\n    body_types[]: container"

        adr_str = f"\n    adr_class: {cdata['adr_class']}" if "adr_class" in cdata else ""

        content = f"""cargo_data : cargo.{cargo_id}
{{
    name: "{cdata['nombre']}"
    fragility: {cdata['fragilidad']}
    valuable: {valiosa_flag}{adr_str}
    group[]: {cdata['grupo']}
    volume: {cdata['volume']}
    mass: {cdata['mass']}
    unit_reward_per_km: {cdata['unit_reward_per_km']}
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
            cname = ciudad["nombre"].split(" (")[0].strip()
            loc_lines.append(f'    key[]: "{cid}"\n    val[]: "{cname}"')

    for cargo_id, cdata in CARGAS_CHILENAS.items():
        cname = cdata["nombre"]
        loc_lines.append(f'    key[]: "{cargo_id}"\n    val[]: "{cname}"')

    loc_content = "SiiNunit\n{\nlocalization_db : .localization\n{\n" + "\n".join(loc_lines) + "\n}\n}\n"

    for lang in idiomas:
        ldir = BASE_DIR / "locale" / lang
        ldir.mkdir(parents=True, exist_ok=True)
        (ldir / "locale.sii").write_text(loc_content, encoding="utf-8")

    print(f"-> Localización de 52 ciudades y avenidas generada en {len(idiomas)} idiomas (locale/)")


def desactivar_dlcs_europa():
    """Neutraliza ciudades y países de DLCs europeos para garantizar un mapa 100% chileno sin ciudades extranjeras"""
    dlc_files = [
        # Ciudades de DLCs europeos
        DEF_DIR / "city.balt.sii",       # Beyond the Baltic Sea (Lappeenranta, etc.)
        DEF_DIR / "city.north.sii",      # Scandinavia
        DEF_DIR / "city.iberia.sii",     # Iberia
        DEF_DIR / "city.it.sii",         # Italia
        DEF_DIR / "city.fr.sii",         # Vive la France
        DEF_DIR / "city.east.sii",       # Going East
        DEF_DIR / "city.balkan_e.sii",   # Road to the Black Sea
        DEF_DIR / "city.balkan_w.sii",   # West Balkans
        DEF_DIR / "city.greece.sii",     # Greece
        DEF_DIR / "city.halloween.sii",
        DEF_DIR / "city.mod_halloween_2025_event.sii",

        # Países de DLCs europeos
        DEF_DIR / "country.balt.sii",
        DEF_DIR / "country.north.sii",
        DEF_DIR / "country.iberia.sii",
        DEF_DIR / "country.it.sii",
        DEF_DIR / "country.fr.sii",
        DEF_DIR / "country.east.sii",
        DEF_DIR / "country.balkan_e.sii",
        DEF_DIR / "country.balkan_w.sii",
        DEF_DIR / "country.greece.sii",
        DEF_DIR / "country.halloween.sii",
        DEF_DIR / "country.mod_polar_circle.sii",
        DEF_DIR / "country.mod_halloween_2025_event.sii",
    ]
    empty_content = "SiiNunit\n{\n}\n"
    for dlc_f in dlc_files:
        dlc_f.parent.mkdir(parents=True, exist_ok=True)
        with open(dlc_f, "w", encoding="utf-8") as f:
            f.write(empty_content)
    print(f"-> {len(dlc_files)} archivos de DLCs europeos neutralizados (mapa 100% puro de Chile)")


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

