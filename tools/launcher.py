#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
==============================================================================
TRANSPORTE AUSTRAL - SELECTOR DE REGIONES Y GENERADOR DE TRAYECTORIAS CHILE
==============================================================================
Permite al usuario seleccionar cualquier región de Chile y sortea aleatoriamente
una comuna de dicha región para iniciar su recorrido o sesión de conducción en ETS2.
"""

import os
import sys
import random
import subprocess
from pathlib import Path

# Configurar salida UTF-8 para consola de Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

BASE_DIR = Path(__file__).resolve().parent.parent

# Importar base de datos de generator.py
try:
    from tools.generator import REGIONES_CHILE, CONFIG_REGIONES, EMPRESAS_CHILENAS
except ImportError:
    sys.path.insert(0, str(BASE_DIR))
    from tools.generator import REGIONES_CHILE, CONFIG_REGIONES, EMPRESAS_CHILENAS

# Detección del ejecutable de ETS2
POSIBLES_EXES = [
    Path(r"D:\SteamLibrary\steamapps\common\Euro Truck Simulator 2\bin\win_x64\eurotrucks2.exe"),
    Path(r"C:\Program Files (x86)\Steam\steamapps\common\Euro Truck Simulator 2\bin\win_x64\eurotrucks2.exe"),
    Path(r"E:\SteamLibrary\steamapps\common\Euro Truck Simulator 2\bin\win_x64\eurotrucks2.exe"),
]


def encontrar_ets2():
    for p in POSIBLES_EXES:
        if p.exists():
            return p
    return None


def limpiar_pantalla():
    os.system("cls" if os.name == "nt" else "clear")


def mostrar_banner():
    print("=" * 76)
    print("  [CHILE] TRANSPORTE AUSTRAL - SISTEMA DE TRAYECTORIAS POR REGIONES")
    print("=" * 76)


def seleccionar_region():
    limpiar_pantalla()
    mostrar_banner()
    print(" Selecciona la Región de Chile donde deseas iniciar tu nueva trayectoria:\n")

    lista_regiones = list(CONFIG_REGIONES.items())
    for idx, (reg_code, rinfo) in enumerate(lista_regiones, 1):
        comunas = [c["nombre"] for c in REGIONES_CHILE[reg_code]["ciudades"]]
        comunas_str = ", ".join(comunas[:3])
        if len(comunas) > 3:
            comunas_str += f" (+{len(comunas) - 3} más)"
        print(f"  [{idx:2d}] {rinfo['nombre']:<32} -> ({comunas_str})")

    print(f"  [17] Ruleta Nacional (Cualquier comuna de Chile al azar)")
    print(f"  [ 0] Salir")
    print("-" * 76)

    while True:
        try:
            opcion = input(" Ingresa el número de tu opción (1-17) [0 para salir]: ").strip()
            if opcion == "0":
                return None, None
            op_num = int(opcion)
            if 1 <= op_num <= 16:
                reg_code, rinfo = lista_regiones[op_num - 1]
                return reg_code, rinfo
            elif op_num == 17:
                # Cualquier región al azar
                reg_code, rinfo = random.choice(lista_regiones)
                return reg_code, rinfo
            else:
                print(" -> Opción no válida. Ingresa un número del 1 al 17.")
        except ValueError:
            print(" -> Entrada inválida. Por favor ingresa un número.")


def sortear_comuna(reg_code, rinfo):
    ciudades = REGIONES_CHILE[reg_code]["ciudades"]
    comuna_elegida = random.choice(ciudades)
    return comuna_elegida


def mostrar_resultado_trayectoria(reg_code, rinfo, comuna):
    limpiar_pantalla()
    mostrar_banner()
    print("\n" + ">>> TRAYECTORIA CHILENA ASIGNADA ALEATORIAMENTE <<<".center(76))
    print("-" * 76)
    print(f"  [REGION]   : {rinfo['nombre']} ({reg_code})")
    print(f"  [COMUNA]   : {comuna['nombre'].upper()}")
    print(f"  [COORD]    : X: {comuna['x']}, Z: {comuna['z']}")
    print(f"  [EMPRESAS] : {', '.join(comuna['empresas']).upper()}")
    print("-" * 76)
    print(f"  [CONSOLA]  : goto {comuna['x']} 100 {comuna['z']}")
    print("-" * 76)


def menu_acciones(reg_code, rinfo, comuna):
    ets2_exe = encontrar_ets2()

    while True:
        print("\n ¿Qué deseas hacer a continuación?")
        print("  [1] Iniciar Euro Truck Simulator 2 (Conducir)")
        print("  [2] Abrir SCS Map Editor (Modo Construcción de Sectores)")
        print("  [3] Sortear otra comuna en esta misma región")
        print("  [4] Elegir otra región de Chile")
        print("  [0] Salir")
        print("-" * 76)

        op = input(" Selecciona una acción (1-4) [0 para salir]: ").strip()

        if op == "1":
            if ets2_exe and ets2_exe.exists():
                print(f"\nIniciando Euro Truck Simulator 2 desde:\n{ets2_exe}")
                subprocess.Popen([str(ets2_exe)])
                print("¡Buen viaje por las rutas de Chile! Pulsa enter para salir.")
                input()
                return False
            else:
                print("\n[AVISO] No se encontró automáticamente eurotrucks2.exe.")
                print("Puedes iniciar el juego normalmente desde Steam.")
                input("\nPresiona enter para continuar...")

        elif op == "2":
            if ets2_exe and ets2_exe.exists():
                print(f"\nIniciando SCS Map Editor (mapa 'chile')...")
                cmd = [str(ets2_exe), "-edit", "chile", "-force_mods"]
                subprocess.Popen(cmd)
                print(f"-> Editor abierto. Para ir a {comuna['nombre']}, escribe en la consola (~):")
                print(f"   c_goto {comuna['x']} 100 {comuna['z']}")
                input("\nPresiona enter para continuar...")
            else:
                print("\n[AVISO] No se encontró eurotrucks2.exe para abrir el editor.")
                input("\nPresiona enter para continuar...")

        elif op == "3":
            nueva_comuna = sortear_comuna(reg_code, rinfo)
            mostrar_resultado_trayectoria(reg_code, rinfo, nueva_comuna)
            comuna = nueva_comuna

        elif op == "4":
            return True

        elif op == "0":
            return False


def main():
    while True:
        reg_code, rinfo = seleccionar_region()
        if not reg_code:
            print("\n¡Gracias por utilizar Transporte Austral!")
            break

        comuna = sortear_comuna(reg_code, rinfo)
        mostrar_resultado_trayectoria(reg_code, rinfo, comuna)

        continuar = menu_acciones(reg_code, rinfo, comuna)
        if not continuar:
            break


if __name__ == "__main__":
    main()
