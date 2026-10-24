#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
prune_roads.py - Elimina del mapa las carreteras cortadas.

Las carreteras que terminan en el vacio (porque su continuacion estaba en un sector
de Europa que no se importo, o porque son ramales sin salida) se marcan como
OCULTAS en el mapa. Se repite hasta que no quedan extremos sueltos, de modo que
solo permanecen caminos continuos entre intersecciones.
Es una edicion no destructiva: solo se cambia un bit de flags de cada item,
sin mover offsets ni borrar items ni nodos.
"""

import glob
import struct
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR / "tools") not in sys.path:
    sys.path.insert(0, str(BASE_DIR / "tools"))

import sector_walker as w  # noqa: E402

ROAD_HIDDEN = (3, 0x02)    # byte de flags (+3), bit 0x02
PREFAB_HIDDEN = (2, 0x02)  # byte de flags (+2), bit 0x02


def _is_hidden(d, it):
    off, bit = ROAD_HIDDEN if it.type == w.T_ROAD else PREFAB_HIDDEN
    return bool(d[it.flags_off + off] & bit)


def load(paths):
    sectors = {}
    nodes = {}
    for p in paths:
        d, items, o = w.walk(p)
        n = struct.unpack_from("<i", d, o)[0]
        for i in range(n):
            b = o + 4 + 0x38 * i
            uid = struct.unpack_from("<Q", d, b)[0]
            nodes[uid] = struct.unpack_from("<QQ", d, b + 0x24)
        sectors[p] = (bytearray(d), items)
    return sectors, nodes


def compute_hidden(sectors, nodes):
    """Devuelve el conjunto de uids (rutas y prefabs) que deben quedar ocultos."""
    roads, prefabs = {}, {}
    all_uids = set()
    hidden = set()
    for d, items in sectors.values():
        for it in items:
            all_uids.add(it.uid)
            if it.type in (w.T_ROAD, w.T_PREFAB):
                (roads if it.type == w.T_ROAD else prefabs)[it.uid] = it
                if _is_hidden(d, it):
                    hidden.add(it.uid)

    # Los prefabs de empresas nunca se ocultan: si no, la empresa desaparece del minimapa.
    protected = set()
    for d, items in sectors.values():
        for it in items:
            if it.type == w.T_COMPANY:
                protected.add(struct.unpack_from("<Q", d, it.offset + 65)[0])
    hidden -= protected
    for d, items in sectors.values():
        for it in items:
            if it.uid in protected and it.type == w.T_PREFAB:
                d[it.flags_off + PREFAB_HIDDEN[0]] &= ~PREFAB_HIDDEN[1] & 0xFF

    def other_alive(node, me):
        b, f = nodes.get(node, (0, 0))
        other = f if b == me else b
        if other == 0 or other == me:
            return False
        if other in roads or other in prefabs:
            return other not in hidden
        return other in all_uids

    changed = True
    while changed:
        changed = False
        for uid, r in roads.items():
            if uid in hidden:
                continue
            if not (other_alive(r.start_node, uid) and other_alive(r.end_node, uid)):
                hidden.add(uid)
                changed = True
        for uid, p in prefabs.items():
            if uid in hidden or uid in protected:
                continue
            alive = sum(1 for n in p.nodes if other_alive(n, uid))
            total = len(p.nodes)
            if (total >= 2 and alive < 2) or (total == 1 and alive == 0):
                hidden.add(uid)
                changed = True
    # Se ocultan los fragmentos aislados que no forman parte de la red principal.
    parent = {}

    def find(x):
        while parent.setdefault(x, x) != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    members = {}
    for uid, r in roads.items():
        if uid not in hidden:
            members[uid] = [r.start_node, r.end_node]
    for uid, p in prefabs.items():
        if uid not in hidden and p.nodes:
            members[uid] = list(p.nodes)
    for ns in members.values():
        for n in ns[1:]:
            parent[find(n)] = find(ns[0])
    groups = {}
    for uid, ns in members.items():
        groups.setdefault(find(ns[0]), []).append(uid)
    for g in groups.values():
        if len(g) < 400:
            hidden.update(u for u in g if u not in protected)
    return hidden, roads, prefabs


def apply_hidden(sectors, hidden):
    n = 0
    for d, items in sectors.values():
        for it in items:
            if it.uid in hidden and it.type in (w.T_ROAD, w.T_PREFAB) and not _is_hidden(d, it):
                off, bit = ROAD_HIDDEN if it.type == w.T_ROAD else PREFAB_HIDDEN
                d[it.flags_off + off] |= bit
                n += 1
    return n


def prune(source_dir, extra_dirs=()):
    paths = sorted(glob.glob(str(Path(source_dir) / "sec*.base")))
    sectors, nodes = load(paths)
    hidden, roads, prefabs = compute_hidden(sectors, nodes)
    changed = apply_hidden(sectors, hidden)
    for p, (d, _) in sectors.items():
        for dest in (Path(source_dir), *map(Path, extra_dirs)):
            target = dest / Path(p).name
            if target.parent.exists():
                target.write_bytes(bytes(d))
    visible_roads = sum(1 for u in roads if u not in hidden)
    print(f" -> carreteras cortadas ocultas: {changed} items "
          f"({visible_roads} de {len(roads)} carreteras permanecen visibles)")
    return changed


if __name__ == "__main__":
    prune(BASE_DIR / "map" / "chile", [BASE_DIR / "map" / "europe"])
