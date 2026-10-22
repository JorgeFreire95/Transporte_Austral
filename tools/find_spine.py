#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from pathlib import Path

src = Path('scratch/base_map/map/europe')

available = set()
for p in src.glob('sec*.base'):
    x = int(p.stem[3:8])
    z = int(p.stem[8:13])
    available.add((x, z))

# The key Chilean capital cities along the North-South corridor
city_nodes = [
    (0, -6),   # XV Arica (Kiel)
    (1, -5),   # I Iquique (Rostock)
    (-1, -4),  # II Antofagasta (Hamburg)
    (-1, -3),  # III Copiapó (Hannover)
    (0, -2),   # IV La Serena (Magdeburg)
    (-1, -1),  # V Valparaíso (Kassel)
    (-2, 0),   # RM Santiago (Frankfurt)
    (-2, 1),   # VI Rancagua (Mannheim)
    (-1, 2),   # VII Talca (Stuttgart)
    (-3, 2),   # XVI Chillán (Strasbourg)
    (0, 3),    # VIII Concepción (München)
    (0, 4),    # IX Temuco (Innsbruck)
    (-2, 5),   # XIV Valdivia (Zürich)
    (-3, 5),   # X Puerto Montt (Bern)
    (-2, 6),   # XI Coyhaique (Milano)
    (-4, 7),   # XII Punta Arenas (Torino)
]

def bfs_path(start, goal):
    q = [[start]]
    vis = {start}
    while q:
        path = q.pop(0)
        curr = path[-1]
        if curr == goal:
            return path
        for dx, dz in [(0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (-1, 1), (1, -1), (-1, -1)]:
            nxt = (curr[0] + dx, curr[1] + dz)
            if nxt in available and nxt not in vis:
                vis.add(nxt)
                q.append(path + [nxt])
    return None

spine = set()
for i in range(len(city_nodes) - 1):
    p = bfs_path(city_nodes[i], city_nodes[i+1])
    if p:
        for node in p:
            spine.add(node)
    else:
        print(f"No path between {city_nodes[i]} and {city_nodes[i+1]}")

sorted_spine = sorted(list(spine))
print(f"Total linear spine sectors: {len(sorted_spine)}")
sector_names = [f"sec{x:+05d}{z:+05d}" for x, z in sorted_spine]
print("SPINE_SECTORS = [")
for s in sector_names:
    print(f'    "{s}",')
print("]")
