#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
sector_walker.py - Lector de sectores .base (version 907) de ETS2.
Recorre los items de un sector y expone sus offsets, tipos, nodos y enlaces,
siguiendo el formato documentado por el proyecto ts-map.
"""

import struct
from dataclasses import dataclass, field

T_TERRAIN, T_BUILDING, T_ROAD, T_PREFAB, T_MODEL, T_COMPANY, T_SERVICE = 1, 2, 3, 4, 5, 6, 7
T_CUTPLANE, T_CITY, T_MAPOVERLAY, T_FERRY, T_GARAGE = 8, 12, 18, 19, 22
T_TRIGGER, T_FUELPUMP, T_ROADSIDE, T_BUSSTOP, T_TRAFFICRULE = 34, 35, 36, 37, 38
T_BEZIER, T_TRAJECTORY, T_MAPAREA, T_CURVE, T_CUTSCENE, T_VISAREA = 39, 41, 42, 44, 46, 48

VEG_SPHERE = 0x14
STAMP = 0x18


class SectorParseError(Exception):
    pass


@dataclass
class Item:
    type: int
    offset: int
    size: int
    uid: int
    flags_off: int
    start_node: int = 0
    end_node: int = 0
    nodes: list = field(default_factory=list)


def _u8(d, o): return d[o]
def _u16(d, o): return struct.unpack_from("<H", d, o)[0]
def _i32(d, o): return struct.unpack_from("<i", d, o)[0]
def _u64(d, o): return struct.unpack_from("<Q", d, o)[0]


def quad_info(d, o):
    s = o
    mat = _u16(d, o)
    o += 2 + 0x0A * mat
    col = _u16(d, o)
    o += 2 + 4 * col + 4
    sto = _i32(d, o)
    o += 4 + 4 * sto
    off = _i32(d, o)
    o += 4 + 0x10 * off
    nor = _i32(d, o)
    o += 4 + 0x10 * nor
    return o - s


def parse_item(d, o, parsers):
    t = struct.unpack_from("<I", d, o)[0]
    fn = parsers.get(t)
    if fn is None:
        raise SectorParseError(f"tipo de item desconocido {t} @ {o}")
    uid = _u64(d, o + 4)
    f = o + 0x34
    it = Item(type=t, offset=o, size=0, uid=uid, flags_off=f)
    it.size = fn(d, o, f, it) - o
    return it


def _terrain(d, o, f, it):
    n = _i32(d, f + 0x05 + 0xEE)
    p = f + 0x05 + 0xEE + 4 + VEG_SPHERE * n
    p += quad_info(d, p)
    p += quad_info(d, p)
    return p + 0x20


def _building(d, o, f, it):
    n = _i32(d, f + 0x05 + 0x2C)
    return f + 0x05 + 0x2C + 4 + 4 * n


def _road(d, o, f, it):
    p = f + 0x09 + 0x08 + 0xB4
    it.start_node = _u64(d, p)
    it.end_node = _u64(d, p + 8)
    return p + 8 + 8 + 4


def _prefab(d, o, f, it):
    p = f + 0x05 + 0x08 + 0x08
    parts = _i32(d, p)
    p += 4 + parts * 8
    nc = _i32(d, p)
    p += 4
    it.nodes = [_u64(d, p + 8 * i) for i in range(nc)]
    p += 8 * nc
    cc = _i32(d, p)
    p += 4 + 8 * cc + 8
    return p + 2 + nc * 0x0C + 8


def _model(d, o, f, it):
    n = _i32(d, f + 0x05 + 0x18)
    return f + 0x05 + 0x18 + 4 + 8 * n + 0x24


def _company(d, o, f, it):
    p = f + 0x05 + 0x08 + 0x08 + 0x08 + 0x08
    n = _i32(d, p)
    return p + 4 + 0x0C * n


def _sub_uids(base):
    def fn(d, o, f, it):
        n = _i32(d, f + 0x05 + base)
        return f + 0x05 + base + 4 + 8 * n
    return fn


def _city(d, o, f, it):
    return f + 0x05 + 0x08 + 0x04 + 0x04 + 0x08


def _cutplane(d, o, f, it):
    n = _i32(d, f + 0x05)
    it.nodes = [_u64(d, f + 0x05 + 4 + 8 * i) for i in range(n)]
    return f + 0x05 + 4 + 8 * n


def _bezier(d, o, f, it):
    p = f + 0x05 + 0xF1
    n = _i32(d, p)
    p += 4 + VEG_SPHERE * n
    return p + quad_info(d, p)


def _maparea(d, o, f, it):
    n = _i32(d, f + 0x05)
    p = f + 0x05 + 4 + 8 * n
    return p + 4


def _visarea(d, o, f, it):
    n = _i32(d, f + 0x05 + 0x10)
    return f + 0x05 + 0x10 + 4 + 8 * n


def _roadside(d, o, f, it):
    p = f + 0x05 + 0x20
    boards = struct.unpack_from("<b", d, p)[0]
    p += 1 + boards * 0x18
    tl = _i32(d, p)
    p += 8
    if tl != 0:
        p += tl
        bo = _i32(d, p)
        p += 4
        for _ in range(bo):
            p += 0x08
            fl = d[p]
            p += 1
            if fl & 1:
                p += 2
            if fl & 2:
                p += 8
        so = _i32(d, p)
        p += 4
        for _ in range(so):
            p += 0x0C
            ac = _i32(d, p)
            p += 4
            for _ in range(ac):
                ty = struct.unpack_from("<h", d, p)[0]
                p += 6
                if ty == 5:
                    p += 8 + _i32(d, p)
                elif ty == 6:
                    p += 8
                elif ty == 1:
                    p += 1
                else:
                    p += 4
    return p


def _trigger(d, o, f, it):
    p = f + 0x05
    tags = _i32(d, p)
    p += 4 + 8 * tags
    nc = _i32(d, p)
    p += 4 + 8 * nc
    na = _i32(d, p)
    p += 4
    for _ in range(na):
        p += 0x08
        ho = _i32(d, p)
        p += 4
        if ho < 0:
            continue
        p += 4 * ho
        pc = _i32(d, p)
        p += 4
        for _ in range(pc):
            p += 8 + _i32(d, p)
        tt = _i32(d, p)
        p += 4 + tt * 8 + 8
    if nc == 1:
        p += 4
    return p


def _trafficrule(d, o, f, it):
    p = f + 0x05
    tags = _i32(d, p)
    p += 4
    p += 8 * tags
    nc = _i32(d, p)
    return p + 4 + 8 * nc + 0x0C


def _trajectory(d, o, f, it):
    p = f + 0x05
    nc = _i32(d, p)
    p += 4 + 8 * nc + 8
    rr = _i32(d, p)
    p += 4 + 0x1C * rr
    cp = _i32(d, p)
    p += 4 + 0x10 * cp
    tg = _i32(d, p)
    return p + 4 + 8 * tg


def _curve(d, o, f, it):
    p = f + 0x05 + 32 + 4
    mask = _i32(d, p) & 0xFFFFFFFF
    p += 4
    cnt = bin(mask).count("1")
    for _ in range(cnt):
        p += 0x4C
        h = _i32(d, p)
        p += 4 + 4 * h + 0x14
    return p


def _mapoverlay(d, o, f, it):
    return f + 0x05 + 0x08 + 0x08


def _busstop(d, o, f, it):
    return f + 0x05 + 0x08 + 0x08 + 0x08


def _ferry(d, o, f, it):
    return f + 0x05 + 0x10 + 0x08 + 0x0C


def _cutscene(d, o, f, it):
    p = f + 0x05
    tg = _i32(d, p)
    p += 4 + 8 * tg + 8
    ac = _i32(d, p)
    p += 4
    for _ in range(ac):
        npc = _i32(d, p)
        p += 4 + 4 * npc
        spc = _i32(d, p)
        p += 4
        for _ in range(spc):
            p += 8 + _i32(d, p)
        tt = _i32(d, p)
        p += 4 + 8 * tt + 8
    return p


PARSERS = {
    T_ROADSIDE: _roadside, T_TRIGGER: _trigger, T_TRAFFICRULE: _trafficrule,
    T_TRAJECTORY: _trajectory, T_CURVE: _curve, T_MAPOVERLAY: _mapoverlay,
    T_BUSSTOP: _busstop, T_FERRY: _ferry, T_CUTSCENE: _cutscene,
    T_TERRAIN: _terrain, T_BUILDING: _building, T_ROAD: _road, T_PREFAB: _prefab,
    T_MODEL: _model, T_COMPANY: _company, T_SERVICE: _sub_uids(0x10),
    T_CUTPLANE: _cutplane, T_CITY: _city, T_GARAGE: _sub_uids(0x1C),
    T_FUELPUMP: _sub_uids(0x10), T_BEZIER: _bezier, T_MAPAREA: _maparea,
    T_VISAREA: _visarea,
}


def walk(path, extra_parsers=None):
    """Devuelve (data, items, nodes_off, nodes) o lanza SectorParseError."""
    d = open(path, "rb").read()
    parsers = dict(PARSERS)
    if extra_parsers:
        parsers.update(extra_parsers)
    version = struct.unpack_from("<I", d, 0)[0]
    if version != 907:
        raise SectorParseError(f"version {version} no soportada")
    count = struct.unpack_from("<I", d, 0x10)[0]
    o = 0x14
    items = []
    for _ in range(count):
        try:
            it = parse_item(d, o, parsers)
        except (SectorParseError, struct.error) as e:
            prev = items[-1] if items else None
            raise SectorParseError(f"{e}; item previo tipo {prev.type if prev else None} @ {prev.offset if prev else None} tam {prev.size if prev else None}")
        items.append(it)
        o += it.size
    return d, items, o
