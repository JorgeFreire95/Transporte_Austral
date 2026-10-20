# Regla del Proyecto: Actualización Automática del Archivo .SCS

Cada vez que se realice cualquier modificación en los archivos del mod (definiciones SII/SUI en `def/`, mapas en `map/`, materiales en `material/`, iconos, descripciones o scripts en `tools/`), se DEBE ejecutar automáticamente:

```bash
python tools/build.py
```

Esto asegura que:
1. Se valide la integridad y consistencia de todos los archivos del mod.
2. Se reempaquete el archivo `dist/Transporte_Austral_Chile.scs`.
3. Se copie y actualice automáticamente en la carpeta de mods de Euro Truck Simulator 2 del usuario (`Documents/Euro Truck Simulator 2/mod/`).
