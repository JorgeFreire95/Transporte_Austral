ESTRUCTURA DE SECTORES DEL MAPA DE CHILE (SCS PRISM3D ENGINE)
==============================================================

Para crear y editar el mapa de Chile en Euro Truck Simulator 2:

1. Iniciar el editor con el parámetro del mapa 'chile':
   eurotrucks2.exe -edit chile -force_mods

2. En la consola del editor (tecla ~):
   - Para guardar: 'save chile' (guardará en map/chile/secXXXX+YYYY.base)
   - Para recargar: 'load chile'
   - Para teleportarse: 'c_goto X Y Z' (usa tools/geo_converter.py para obtener coordenadas)

3. Archivos generados automáticamente por el editor al guardar:
   - map/chile.mbd             (Master Binary Database)
   - map/chile/sec*.base       (Geometría, caminos, elevaciones y prefabs)
   - map/chile/sec*.data       (Entidades y triggers)
   - map/chile/sec*.desc       (Descripciones de sector)
   - map/chile/sec*.aux        (Datos auxiliares de render)

4. Toda la red de carreteras, puentes, peajes y terrenos modelados en el editor
   se almacena en estos archivos de sector binarios.
