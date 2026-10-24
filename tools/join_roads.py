#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
join_roads.py - Une los extremos de carretera que quedaron cortados.

Tras la poda (prune_roads) quedan cruces/extremos visibles cuyo ramal fue ocultado.
Este script empareja extremos libres que se miran entre si (misma direccion, altura
parecida, cercanos) y agrega un item de carretera que los une, clonando el tipo
de la carretera oculta del extremo. Es idempotente: solo actua sobre extremos
que siguen libres. Ejecutar despues de prune_roads.
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
import sector_walker as w  # noqa: E402
from bridge_gap import fwd2, PAD  # noqa: E402

MAP_DIR = os.path.join(ROOT, "map", "chile")
MAX_DIST = 4000.0
MIN_DIST = 25.0
MIN_COS = 0.7
MAX_DH = 80.0


def hidden(d, it):
    fo = it.flags_off + (3 if it.type == w.T_ROAD else 2)
    return bool(d[fo] & 0x02)


def main(map_dir=MAP_DIR, extra_dirs=()):
    files = sorted(glob.glob(os.path.join(map_dir, "sec*.base")))
    bufs, tables = {}, {}
    pos, nq, nref, node_secs = {}, {}, {}, collections.defaultdict(list)
    items = {}
    used = set()
    for p in files:
        d, its, o = w.walk(p)
        bufs[p] = bytearray(d)
        tables[p] = o
        for i in range(struct.unpack_from("<i", d, o)[0]):
            b = o + 4 + 0x38 * i
            u = struct.unpack_from("<Q", d, b)[0]
            used.add(u)
            node_secs[u].append((p, b))
            if u not in pos:
                pos[u] = tuple(c / 256.0 for c in struct.unpack_from("<iii", d, b + 8))
                nq[u] = struct.unpack_from("<4f", d, b + 0x14)
                nref[u] = struct.unpack_from("<QQ", d, b + 0x24)
        for it in its:
            used.add(it.uid)
            if it.type in (w.T_ROAD, w.T_PREFAB):
                items[it.uid] = (it, p, hidden(d, it))

    vis_use = collections.defaultdict(list)
    for uid, (it, p, h) in items.items():
        if h:
            continue
        for n in (it.nodes if it.type == w.T_PREFAB else [it.start_node, it.end_node]):
            vis_use[n].append(uid)

    roads_xyz = [(it, p) for uid, (it, p, h) in items.items() if it.type == w.T_ROAD]
    ends = []
    for n, us in vis_use.items():
        if len(us) != 1 or n not in pos:
            continue
        b, f = nref[n]
        if f == us[0]:
            role = "Q"
        elif b == us[0]:
            role = "P"
        else:
            continue
        free = b if role == "Q" else f
        ends.append((n, role, us[0], free))

    cand = []
    Ps = [e for e in ends if e[1] == "P"]
    Qs = [e for e in ends if e[1] == "Q"]
    for pn, _, pu, _ in Ps:
        fp = fwd2(nq[pn])
        for qn, _, qu, _ in Qs:
            if pu == qu:
                continue
            dx, dz = pos[qn][0] - pos[pn][0], pos[qn][2] - pos[pn][2]
            dist = math.hypot(dx, dz)
            if dist < MIN_DIST or dist > MAX_DIST or abs(pos[qn][1] - pos[pn][1]) > MAX_DH:
                continue
            ux, uz = dx / dist, dz / dist
            fq = fwd2(nq[qn])
            if min(fp[0] * ux + fp[1] * uz, fq[0] * ux + fq[1] * uz) < MIN_COS:
                continue
            cand.append((dist, pn, qn))
    cand.sort()
    taken, pairs = set(), []
    for dist, pn, qn in cand:
        if pn in taken or qn in taken:
            continue
        taken.update((pn, qn))
        pairs.append((dist, pn, qn))
    print(f"  -> {len(ends)} extremos libres, {len(pairs)} pares unibles")
    if not pairs:
        return 0

    free_of = {e[0]: e[3] for e in ends}

    def template(pn):
        r = items.get(free_of[pn])
        if r and r[0].type == w.T_ROAD:
            return r[0], r[1]
        best = None
        for it, p in roads_xyz:
            q = pos.get(it.start_node)
            if q:
                dd = (q[0] - pos[pn][0]) ** 2 + (q[2] - pos[pn][2]) ** 2
                if best is None or dd < best[0]:
                    best = (dd, it, p)
        return best[1], best[2]

    uid = 0x7C20000000000000
    by_home = collections.defaultdict(list)
    for dist, pn, qn in pairs:
        it, p = template(pn)
        raw = bytearray(bufs[p][it.offset:it.offset + it.size])
        while uid in used:
            uid += 0x10001
        used.add(uid)
        npos = raw.find(struct.pack("<QQ", it.start_node, it.end_node))
        if npos < 0:
            continue
        struct.pack_into("<Q", raw, 4, uid)
        fo = it.flags_off - it.offset + 3
        raw[fo] &= ~0x02 & 0xFF
        p0, q0 = pos[pn], pos[qn]
        mn = (min(p0[0], q0[0]) - PAD, min(p0[1], q0[1]) - PAD, min(p0[2], q0[2]) - PAD)
        mx = (max(p0[0], q0[0]) + PAD, max(p0[1], q0[1]) + PAD, max(p0[2], q0[2]) + PAD)
        struct.pack_into("<3f", raw, 0x0C, *mn)
        struct.pack_into("<2f", raw, 0x18, (mn[0] + mn[2]) / 2, (mn[0] - mx[2]) / 2)
        struct.pack_into("<3f", raw, 0x20, *mx)
        struct.pack_into("<2f", raw, 0x2C, (mx[0] + mx[2]) / 2, (mx[0] - mn[2]) / 2)
        struct.pack_into("<QQ", raw, npos, pn, qn)
        for (sp, b) in node_secs[pn]:
            struct.pack_into("<Q", bufs[sp], b + 0x2C, uid)
        for (sp, b) in node_secs[qn]:
            struct.pack_into("<Q", bufs[sp], b + 0x24, uid)
        by_home[node_secs[pn][0][0]].append((bytes(raw), qn))

    added = 0
    for home, news in by_home.items():
        d = bufs[home]
        o = tables[home]
        cnt = struct.unpack_from("<i", d, o)[0]
        have = {struct.unpack_from("<Q", d, o + 4 + 0x38 * i)[0] for i in range(cnt)}
        extra = b""
        for raw, qn in news:
            if qn not in have:
                sp, b = node_secs[qn][0]
                extra += bytes(bufs[sp][b:b + 0x38])
                have.add(qn)
        nd0, nd1 = o + 4, o + 4 + 0x38 * cnt
        out = bytearray(d[:0x14])
        struct.pack_into("<I", out, 0x10, struct.unpack_from("<I", d, 0x10)[0] + len(news))
        out += d[0x14:o] + b"".join(r for r, _ in news)
        out += struct.pack("<i", cnt + len(extra) // 0x38) + d[nd0:nd1] + extra + d[nd1:]
        bufs[home] = out
        added += len(news)

    for p, buf in bufs.items():
        open(p, "wb").write(bytes(buf))
        for dest in extra_dirs:
            t = os.path.join(dest, os.path.basename(p))
            if os.path.isdir(dest):
                open(t, "wb").write(bytes(buf))
    for p in files:
        d2, _, o2 = w.walk(p)
        c2 = struct.unpack_from("<i", d2, o2)[0]
        vis = struct.unpack_from("<i", d2, o2 + 4 + 0x38 * c2)[0]
        assert o2 + 4 + 0x38 * c2 + 4 + 8 * vis == len(d2), p
    print(f"  -> {added} carreteras agregadas para unir extremos cortados")
    return added


if __name__ == "__main__":
    main(MAP_DIR, [os.path.join(ROOT, "map", "europe")])
