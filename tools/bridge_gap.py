#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
bridge_gap.py - Une las dos mitades desconectadas de la red vial de map/chile.

Busca el par de extremos libres (nodo P con lado forward libre, nodo Q con lado
backward libre) que une las dos componentes mas grandes, con direcciones
alineadas, y agrega un item de carretera P -> Q clonando el de P.
Es idempotente: si la red ya esta unida no hace nada. Ejecutar antes de prune_roads.
"""
import collections
import glob
import math
import os
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import sector_walker as w

MAP_DIR = os.path.join(ROOT, "map", "chile")
PAD = 60.0


def rot(q, v):
    qw, qx, qy, qz = q
    x, y, z = v
    tx = 2 * (qy * z - qz * y)
    ty = 2 * (qz * x - qx * z)
    tz = 2 * (qx * y - qy * x)
    return (x + qw * tx + (qy * tz - qz * ty), y + qw * ty + (qz * tx - qx * tz), z + qw * tz + (qx * ty - qy * tx))


def fwd2(q):
    fw = rot(q, (0, 0, -1))
    h = math.hypot(fw[0], fw[2]) or 1.0
    return fw[0] / h, fw[2] / h


def main():
    files = sorted(glob.glob(os.path.join(MAP_DIR, "sec*.base")))
    par = {}

    def find(a):
        par.setdefault(a, a)
        while par[a] != a:
            par[a] = par[par[a]]
            a = par[a]
        return a

    pos, nq, nref, kind, road_of = {}, {}, {}, {}, {}
    road_bytes = {}
    used = set()
    for p in files:
        d, items, o = w.walk(p)
        cnt = struct.unpack_from("<i", d, o)[0]
        for i in range(cnt):
            no = o + 4 + 0x38 * i
            uid = struct.unpack_from("<Q", d, no)[0]
            used.add(uid)
            pos[uid] = tuple(c / 256.0 for c in struct.unpack_from("<iii", d, no + 8))
            nq[uid] = struct.unpack_from("<4f", d, no + 0x14)
            nref[uid] = struct.unpack_from("<QQ", d, no + 0x24)
        for it in items:
            used.add(it.uid)
            if it.type == w.T_ROAD:
                par[find(it.start_node)] = find(it.end_node)
                kind[it.start_node] = "start"
                kind[it.end_node] = "end"
                road_of[it.start_node] = it.uid
                road_of[it.end_node] = it.uid
                road_bytes[it.uid] = bytes(d[it.offset:it.offset + it.size])
            elif it.type == w.T_PREFAB:
                for a in it.nodes[1:]:
                    par[find(it.nodes[0])] = find(a)
                for a in it.nodes:
                    kind.setdefault(a, "prefab")
    groups = collections.defaultdict(list)
    for n in par:
        if n in pos:
            groups[find(n)].append(n)
    big = sorted(groups.values(), key=len, reverse=True)
    if len(big) < 2 or len(big[1]) < 500:
        print("  -> red vial ya unida, sin puente que agregar")
        return
    A, B = big[0], big[1]

    def role(n):
        b, f = nref[n]
        if kind.get(n) not in ("start", "end") or (b == 0) == (f == 0):
            return None
        return "P" if f == 0 else "Q"

    best = None
    for GA, GB in ((A, B), (B, A)):
        Ps = [n for n in GA if role(n) == "P"]
        Qs = [n for n in GB if role(n) == "Q"]
        for pn in Ps:
            fp = fwd2(nq[pn])
            for qn in Qs:
                dx, dz = pos[qn][0] - pos[pn][0], pos[qn][2] - pos[pn][2]
                dist = math.hypot(dx, dz)
                if dist < 80 or dist > 8000:
                    continue
                ux, uz = dx / dist, dz / dist
                fq = fwd2(nq[qn])
                cp = fp[0] * ux + fp[1] * uz
                cq = fq[0] * ux + fq[1] * uz
                if min(cp, cq) < 0.9 or abs(pos[qn][1] - pos[pn][1]) > 60:
                    continue
                if best is None or dist < best[0]:
                    best = (dist, pn, qn)
    if best is None:
        print("  -> no se encontro un par de extremos compatible para el puente")
        return
    dist, pn, qn = best
    print(f"  -> puente de {dist:.0f} m entre nodos {pn:#x} y {qn:#x}")

    def _flag_items():
        idx = collections.defaultdict(list)
        for p in files:
            d, items, o = w.walk(p)
            for it in items:
                if it.type == w.T_ROAD:
                    ns, fo = [it.start_node, it.end_node], it.flags_off + 3
                elif it.type == w.T_PREFAB:
                    ns, fo = it.nodes, it.flags_off + 2
                else:
                    continue
                rec = (p, fo, bool(d[fo] & 0x02), it.uid)
                for n in ns:
                    idx[n].append((rec, ns))
        return idx

    def unhide_path(start):
        # Recorre items ocultos desde el extremo hasta alcanzar la red visible y los hace visibles
        idx = _flag_items()
        seen = {start}
        queue = collections.deque([(start, [])])
        while queue:
            n, path = queue.popleft()
            if any(not rec[2] for rec, _ in idx[n]) and path:
                return path
            for rec, ns in idx[n]:
                if rec[2]:
                    for m in ns:
                        if m not in seen:
                            seen.add(m)
                            queue.append((m, path + [rec]))
        return []

    fixes = {}
    for end in (pn, qn):
        path = unhide_path(end)
        print(f"  -> {len(path)} items ocultos del extremo {end:#x} se hacen visibles")
        for p, fo, _, _ in path:
            fixes.setdefault(p, set()).add(fo)
    for p, offs in fixes.items():
        buf = bytearray(open(p, "rb").read())
        for fo in offs:
            buf[fo] &= ~0x02 & 0xFF
        open(p, "wb").write(buf)

    uid = 0x7C10000000000000
    while uid in used:
        uid += 0x10001
    tmpl = bytearray(road_bytes[road_of[pn]])
    f = 0x34
    struct.pack_into("<Q", tmpl, 4, uid)
    tmpl[f + 3] &= ~0x02 & 0xFF
    p0, q0 = pos[pn], pos[qn]
    minx, maxx = min(p0[0], q0[0]) - PAD, max(p0[0], q0[0]) + PAD
    miny, maxy = min(p0[1], q0[1]) - PAD, max(p0[1], q0[1]) + PAD
    minz, maxz = min(p0[2], q0[2]) - PAD, max(p0[2], q0[2]) + PAD
    struct.pack_into("<3f", tmpl, 0x0C, minx, miny, minz)
    struct.pack_into("<2f", tmpl, 0x18, (minx + minz) / 2, (minx - maxz) / 2)
    struct.pack_into("<3f", tmpl, 0x20, maxx, maxy, maxz)
    struct.pack_into("<2f", tmpl, 0x2C, (maxx + maxz) / 2, (maxx - minz) / 2)
    np_ = f + 0x09 + 0x08 + 0xB4
    struct.pack_into("<QQ", tmpl, np_, pn, qn)

    # Actualizar referencias de los nodos P (fwd) y Q (back) en todos los sectores
    node_bytes = {}
    home = None
    for p in files:
        d, items, o = w.walk(p)
        cnt = struct.unpack_from("<i", d, o)[0]
        buf = bytearray(d)
        changed = False
        for i in range(cnt):
            no = o + 4 + 0x38 * i
            u = struct.unpack_from("<Q", buf, no)[0]
            if u == pn:
                struct.pack_into("<Q", buf, no + 0x2C, uid)
                changed = True
                node_bytes.setdefault(pn, bytes(buf[no:no + 0x38]))
                if home is None:
                    home = p
            elif u == qn:
                struct.pack_into("<Q", buf, no + 0x24, uid)
                changed = True
                node_bytes.setdefault(qn, bytes(buf[no:no + 0x38]))
        if changed:
            open(p, "wb").write(buf)

    # Insertar el item (y el nodo Q si falta) en el sector de P
    d, items, o = w.walk(home)
    cnt = struct.unpack_from("<i", d, o)[0]
    have = {struct.unpack_from("<Q", d, o + 4 + 0x38 * i)[0] for i in range(cnt)}
    extra = b"" if qn in have else node_bytes[qn]
    k_nodes = 0 if qn in have else 1
    nd_start = o + 4
    nd_end = nd_start + 0x38 * cnt
    out = bytearray(d[:0x14])
    struct.pack_into("<I", out, 0x10, struct.unpack_from("<I", d, 0x10)[0] + 1)
    out += d[0x14:o] + bytes(tmpl)
    out += struct.pack("<i", cnt + k_nodes) + d[nd_start:nd_end] + extra + d[nd_end:]
    open(home, "wb").write(out)
    d2, _, o2 = w.walk(home)
    c2 = struct.unpack_from("<i", d2, o2)[0]
    vis = struct.unpack_from("<i", d2, o2 + 4 + 0x38 * c2)[0]
    assert o2 + 4 + 0x38 * c2 + 4 + 8 * vis == len(d2), home
    print(f"  -> puente insertado en {os.path.basename(home)}")


if __name__ == "__main__":
    main()
