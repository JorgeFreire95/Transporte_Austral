#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
add_comunas.py - Inserta items de ciudad (comunas) en los sectores map/chile.

Cada comuna de fix_map.COMUNAS que aun no tiene etiqueta visible se coloca
sobre un nodo de carretera visible, dentro de la banda N->S de su region.
Es idempotente: las comunas ya presentes (visibles) se omiten.
Se requiere un respaldo previo; el resultado se valida releyendo con sector_walker.
"""
import collections
import glob
import os
import struct
import sys
from collections import OrderedDict

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import sector_walker as w
from import_starter_sectors import str_to_token
import fix_map

MAP_DIR = os.path.join(ROOT, "map", "chile")
BOX = 200.0
MIN_DIST = 220.0
MIN_COMPONENT = 1000
ORPHAN_DIST = 1500.0
# Limite sur del territorio chileno util (mas alla de Rio Verde no hay mapa real)
CITY_Z_MAX = 32500.0

# Territorio insular/antartico fuera del mapa continental y duplicados de ciudades existentes
SKIP_IDS = {"pt_natales"}
SKIP_NAMES = ("antartica", "cabo de hornos", "pascua", "juan fernandez", "guaitecas")
SKIP_ID_PARTS = ("antart", "hornos", "pascua", "n_juan", "guaitec")

# z central (N -> S) de cada region segun las capitales ya presentes en el mapa
REGION_Z = OrderedDict([
    ("Arica y Parinacota", -22000), ("Tarapaca", -19000), ("Antofagasta", -14000),
    ("Atacama", -10000), ("Coquimbo", -7400), ("Valparaiso", -3000),
    ("Metropolitana", 3000), ("OHiggins", 6500), ("Maule", 10000),
    ("Nuble", 11200), ("Biobio", 13500), ("Araucania", 15500),
    ("Los Rios", 18000), ("Los Lagos", 23000), ("Aysen", 28000),
    ("Magallanes", 30800),
])


def load_sector(path):
    d, items, o = w.walk(path)
    cnt = struct.unpack_from("<i", d, o)[0]
    nodes = {}
    for i in range(cnt):
        no = o + 4 + 0x38 * i
        uid = struct.unpack_from("<Q", d, no)[0]
        x, y, z = (c / 256.0 for c in struct.unpack_from("<iii", d, no + 8))
        nodes[uid] = (x, y, z)
    return d, items, o, cnt, nodes


def main():
    files = sorted(glob.glob(os.path.join(MAP_DIR, "sec*.base")))
    par = {}

    def find(a):
        par.setdefault(a, a)
        while par[a] != a:
            par[a] = par[par[a]]
            a = par[a]
        return a

    def union(a, b):
        par[find(a)] = find(b)

    secs = {}
    visible_tokens = set()
    used_uids = set()
    cities = []
    candidates = []
    city_items = []
    template = None

    for p in files:
        d, items, o, cnt, nodes = load_sector(p)
        secs[p] = (d, items, o, cnt, nodes)
        used_uids.update(nodes.keys())
        for it in items:
            used_uids.add(it.uid)
            f = it.flags_off
            if it.type == w.T_CITY:
                nid = struct.unpack_from("<Q", d, f + 21)[0]
                pos = nodes.get(nid)
                if not d[f] & 1:
                    city_items.append((p, f, pos, struct.unpack_from("<Q", d, f + 5)[0]))
                    if template is None:
                        template = (bytes(d[it.offset:it.offset + it.size]), nid, p)
            elif it.type == w.T_ROAD and not d[f + 3] & 0x02:
                union(it.start_node, it.end_node)
                sp = nodes.get(it.start_node)
                if sp:
                    candidates.append((sp[2], sp[0], sp[1], p, it.start_node))
            elif it.type == w.T_PREFAB and not d[f + 2] & 0x02:
                for a in it.nodes[1:]:
                    union(it.nodes[0], a)

    sizes = collections.Counter(find(n) for n in list(par))
    candidates = [c for c in candidates if sizes[find(c[4])] >= MIN_COMPONENT and c[0] <= CITY_Z_MAX]

    # Ocultar etiquetas de ciudad sin carretera conectada cerca (fuera del mapa jugable)
    grid = collections.defaultdict(list)
    for z, x, _, _, _ in candidates:
        grid[(int(x // ORPHAN_DIST), int(z // ORPHAN_DIST))].append((x, z))

    def near_road(x, z):
        gx, gz = int(x // ORPHAN_DIST), int(z // ORPHAN_DIST)
        for i in (-1, 0, 1):
            for j in (-1, 0, 1):
                for rx, rz in grid.get((gx + i, gz + j), ()):
                    if (rx - x) ** 2 + (rz - z) ** 2 <= ORPHAN_DIST ** 2:
                        return True
        return False

    hidden_n = 0
    dirty = set()
    for p, f, pos, tkn in city_items:
        if pos is None or (pos[2] <= CITY_Z_MAX and near_road(pos[0], pos[2])):
            visible_tokens.add(tkn)
            if pos:
                cities.append((pos[0], pos[2]))
            continue
        buf = secs[p][0]
        if not isinstance(buf, bytearray):
            buf = bytearray(buf)
            secs[p] = (buf,) + secs[p][1:]
        buf[f] |= 1
        dirty.add(p)
        hidden_n += 1
    for p in dirty:
        open(p, "wb").write(secs[p][0])
    print(f"  -> etiquetas de ciudad fuera de la red ocultadas: {hidden_n}")

    if template is None:
        raise SystemExit("sin item de ciudad plantilla")
    tmpl_item = template[0]
    td, _, to, tcnt, _ = secs[template[2]]
    node_off = None
    for i in range(tcnt):
        no = to + 4 + 0x38 * i
        if struct.unpack_from("<Q", td, no)[0] == template[1]:
            node_off = no
            break
    tmpl_node = bytes(td[node_off:node_off + 0x38])
    ref = [c for c in cities]

    comunas_by_region = OrderedDict((r, []) for r in REGION_Z)
    for cid, name, reg in fix_map.COMUNAS:
        key = reg
        if key not in comunas_by_region or cid in SKIP_IDS:
            continue
        if any(s in name.lower() for s in SKIP_NAMES) or any(s in cid for s in SKIP_ID_PARTS):
            continue
        if struct.unpack("<Q", struct.pack("<Q", str_to_token(cid)))[0] in visible_tokens:
            continue
        comunas_by_region[key].append(cid)

    regs = list(REGION_Z.keys())
    zs = [REGION_Z[r] for r in regs]
    bounds = [-1e9] + [(zs[i] + zs[i + 1]) / 2 for i in range(len(zs) - 1)] + [1e9]

    placements = []
    for i, r in enumerate(regs):
        ids = comunas_by_region[r]
        if not ids:
            continue
        lo, hi = bounds[i], bounds[i + 1]
        band = sorted(c for c in candidates if lo <= c[0] < hi)
        spaced = []
        for c in band:
            if all((c[1] - x) ** 2 + (c[0] - z) ** 2 > MIN_DIST ** 2 for x, z in ref):
                spaced.append(c)
                ref.append((c[1], c[0]))
        pool = spaced
        n = len(ids)
        if len(pool) > n:
            pick = [pool[int((k + 0.5) * len(pool) / n)] for k in range(n)]
        else:
            pick = pool
        print(f"{r}: {n} comunas, {len(band)} candidatos, {len(pick)} colocadas")
        for cid, c in zip(ids, pick):
            placements.append((cid, c))

    by_file = {}
    for cid, c in placements:
        by_file.setdefault(c[3], []).append((cid, c))

    seq = [0x7C00000000000000]

    def new_uid():
        while True:
            seq[0] += 0x10001
            if seq[0] not in used_uids:
                used_uids.add(seq[0])
                return seq[0]

    total = 0
    for p, plist in by_file.items():
        d, items, o, cnt, nodes = secs[p]
        new_items = bytearray()
        new_nodes = bytearray()
        for cid, (z, x, y, _, _) in plist:
            iu, nu = new_uid(), new_uid()
            it = bytearray(tmpl_item)
            f = 0x34
            X, Z = x - BOX / 2, z - BOX / 2
            struct.pack_into("<Q", it, 4, iu)
            it[f] = it[f] & ~1 & 0xFF
            struct.pack_into("<3f", it, 0x0C, X, y - 100.0, Z)
            struct.pack_into("<2f", it, 0x18, (X + Z) / 2, (X - Z) / 2 - BOX / 2)
            mx, mz = X + BOX, Z + BOX
            struct.pack_into("<3f", it, 0x20, mx, y + 100.0, mz)
            struct.pack_into("<2f", it, 0x2C, (mx + mz) / 2, (mx - mz) / 2 + BOX / 2)
            struct.pack_into("<Q", it, f + 5, str_to_token(cid))
            struct.pack_into("<2f", it, f + 13, BOX, BOX)
            struct.pack_into("<Q", it, f + 21, nu)
            nd = bytearray(tmpl_node)
            struct.pack_into("<Q", nd, 0, nu)
            struct.pack_into("<3i", nd, 8, int(round(x * 256)), int(round(y * 256)), int(round(z * 256)))
            struct.pack_into("<Q", nd, 0x24, 0)
            struct.pack_into("<Q", nd, 0x2C, iu)
            new_items += it
            new_nodes += nd
        k = len(plist)
        nd_start = o + 4
        nd_end = nd_start + 0x38 * cnt
        out = bytearray(d[:0x14])
        struct.pack_into("<I", out, 0x10, struct.unpack_from("<I", d, 0x10)[0] + k)
        out += d[0x14:o] + new_items
        out += struct.pack("<i", cnt + k) + d[nd_start:nd_end] + new_nodes + d[nd_end:]
        open(p, "wb").write(out)
        d2, items2, o2 = w.walk(p)
        c2 = struct.unpack_from("<i", d2, o2)[0]
        vis = struct.unpack_from("<i", d2, o2 + 4 + 0x38 * c2)[0]
        assert o2 + 4 + 0x38 * c2 + 4 + 8 * vis == len(d2), p
        total += k
    print(f"Comunas insertadas: {total}")


if __name__ == "__main__":
    main()
