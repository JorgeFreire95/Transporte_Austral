#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
chile_signs_aux.py - Cambia los textos de los letreros de carretera (ciudades,
rutas, servicios) de los sectores .aux por nombres chilenos.

El texto de los letreros vive en el .aux de cada sector como cadenas
'05 00 00 00 00 00' + u64 longitud + bytes UTF-8. No hay tablas de offsets que
se puedan reajustar, por lo que cada reemplazo conserva exactamente la misma
longitud en bytes (se rellena con espacios) y el proceso es idempotente.
"""

import re
import sys
import unicodedata
from collections import Counter
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
DIRS = [BASE / "map" / "chile", BASE / "map" / "europe"]

HEADER = re.compile(rb"\x05\x00\x00\x00\x00\x00([\x01-\xff])\x00\x00\x00\x00\x00\x00\x00")

# Ciudades chilenas ASCII, de mayor a menor prioridad
POOL = [
    "Santiago", "Valparaiso", "Concepcion", "La Serena", "Antofagasta", "Temuco", "Rancagua", "Talca",
    "Arica", "Iquique", "Chillan", "Puerto Montt", "Osorno", "Valdivia", "Los Angeles", "Copiapo",
    "Curico", "Calama", "Punta Arenas", "Coquimbo", "Ovalle", "San Antonio", "Linares", "Los Andes",
    "Quillota", "Melipilla", "Angol", "Coyhaique", "Castro", "Ancud", "Pucon", "Villarrica", "Lautaro",
    "Victoria", "Collipulli", "Parral", "Cauquenes", "Constitucion", "Penco", "Lota", "Coronel", "Tome",
    "Pica", "Vicuna", "Illapel", "Combarbala", "Salamanca", "Vallenar", "Taltal", "Tocopilla",
    "Mejillones", "Pozo Almonte", "Cabrero", "Yumbel", "Nacimiento", "Mulchen", "Lonquimay",
    "Panguipulli", "Futrono", "Rio Bueno", "La Union", "Paillaco", "Frutillar", "Llanquihue", "Calbuco",
    "Quellon", "Chonchi", "Puerto Varas", "Natales", "Porvenir", "Cochrane", "Chile Chico", "Rengo",
    "San Fernando", "Santa Cruz", "Pichilemu", "Graneros", "Machali", "Buin", "Paine", "Talagante",
    "Maipu", "Colina", "Til Til", "Los Vilos", "Cartagena", "Casablanca", "Limache", "Olmue", "Cabildo",
    "La Ligua", "San Felipe", "Llay Llay", "Lebu", "Arauco", "Cañete", "Traiguen", "Loncoche", "Lanco",
    "Vilcun", "Cunco", "Pitrufquen", "Gorbea", "Rapa Nui", "Chepica", "Lolol", "Pelluhue", "Vichuquen",
    "Mariquina", "Corral", "Purranque", "Fresia", "Puyehue", "Hualaihue", "Maullin", "Dalcahue",
    "Quemchi", "Achao", "Curaco", "Palena", "Chaiten", "Futaleufu", "Puerto Aysen", "Villa O'Higgins",
    "Puerto Williams", "Cerro Sombrero", "Puerto Natales", "San Pedro", "Ollague", "Camina", "Huara",
    "Colchane", "Putre", "Codpa", "Pisagua", "Chanaral", "Caldera", "Huasco", "Freirina", "Domeyko",
]
POOL = [p.replace("ñ", "n") for p in POOL]
POOL_KEYS = {p.lower() for p in POOL}

ALIAS = {
    "zurigo": "zurich", "berna": "bern", "bale": "basel", "lione": "lyon", "nizza": "nice",
    "mailand": "milano", "mannheim": "mannheim", "frankfurt a.m.": "frankfurt",
    "frankfurt am main": "frankfurt", "strasbourg": "strassburg", "stuttgart": "stuttgart",
    "prag/praha": "prag", "geneve": "genf",
}

KEYWORDS = {
    "flughafen": ["Aeropuerto", "Aeropto.", "Aerop."], "airport": ["Aeropuerto", "Aeropto.", "Aerop."],
    "messe": ["Feria", "Exp."], "zentrum": ["Centro"], "centro": ["Centro"], "city": ["Centro"],
    "hafen": ["Puerto"], "autohof": ["Servicentro", "Copec"], "polizei": ["Carabineros", "Policia"],
    "autostrada": ["autopista"], "autobahn": ["Autopista"],
    "tangenziale ovest": ["Circunvalacion", "Costanera"], "kontrollzentrum": ["Control", "Peaje"],
    "landeshauptstadt": ["Capital"], "universitat irchel": ["Universidad"], "routen": ["Rutas"],
    "ika bohag": ["Falabella"], "cargo center": ["Carga"], "kreuz": ["Enlace"], "dreieck": ["Enlace"],
    "hotel": ["Hotel"], "land": ["Pais"], "zur": ["a"],
}

ROUTE = re.compile(r"^[AEBNSD]\s?\d{1,3}[a-z]?$")
NUMERIC = re.compile(r"^[\d\s.,/:+\-]*(m|km|h|min|t|%)?$")
KEEP_PREFIX = ("traffic_rule", "sign_templ", "@@", "/", "def.", "sign.")
TAG = re.compile(r"(<[^>]*>|\r|\n)")
SPACES = re.compile(r"(\s{2,})")
EDGE = re.compile(r"^([^A-Za-zÀ-ÿ0-9@]*)(.*?)([^A-Za-zÀ-ÿ0-9.)]*)$", re.S)


def norm(s):
    s = unicodedata.normalize("NFKD", s.lower())
    return "".join(c for c in s if not unicodedata.combining(c)).strip()


def fit(text, nbytes, upper):
    """Centra text en nbytes (UTF-8) usando espacios; None si no cabe."""
    if upper:
        text = text.upper()
    b = len(text.encode("utf-8"))
    if b > nbytes:
        return None
    gap = nbytes - b
    return " " * (gap // 2) + text + " " * (gap - gap // 2)


class Mapper:
    def __init__(self, freq):
        self.freq = freq
        self.assigned = {}
        self.used = set()
        self.cycle = 0

    def city(self, key, nbytes):
        key = ALIAS.get(key, key)
        hit = self.assigned.get(key)
        if hit and len(hit.encode()) <= nbytes:
            return hit
        for cand in POOL:
            if cand.lower() in self.used or len(cand.encode()) > nbytes:
                continue
            self.used.add(cand.lower())
            self.assigned[key] = cand
            return cand
        fits = [c for c in POOL if len(c.encode()) <= nbytes]
        if not fits:
            return None
        self.cycle += 1
        cand = fits[self.cycle % len(fits)]
        self.assigned[key] = cand
        return cand


def convert_piece(piece, mp):
    """piece: texto sin etiquetas ni dobles espacios. Devuelve el reemplazo (mismo largo en bytes)."""
    total = len(piece.encode("utf-8"))
    if not piece.strip() or total <= 3 and not ROUTE.match(piece.strip()):
        return piece
    m = EDGE.match(piece)
    lead, core, trail = m.group(1), m.group(2), m.group(3)
    if not core or core.startswith(KEEP_PREFIX) or NUMERIC.match(core) or not re.search(r"[A-Za-zÀ-ÿ]", core):
        return piece
    if norm(core) in POOL_KEYS or "".join(norm(core).split()) in {k.replace(" ", "") for k in POOL_KEYS}:
        return piece
    avail = total - len(lead.encode()) - len(trail.encode())
    upper = core.isupper() and len(core) > 3
    if ROUTE.match(core):
        out = fit("5", avail, False)
    else:
        k = norm(core)
        words = KEYWORDS.get(k)
        out = None
        if words:
            for w in words:
                out = fit(w, avail, upper)
                if out is not None:
                    break
        elif k in {"a", "e", "f", "d", "i", "xxxxxxx"}:
            return piece
        else:
            base = re.split(r"[-(/]", k)[0].strip()
            name = mp.city(base if len(base) > 3 else k, avail)
            out = fit(name, avail, upper) if name else None
    if out is None:
        out = " " * avail
    return lead + out + trail


def convert_text(text, mp):
    parts = TAG.split(text)
    res = []
    for seg in parts:
        if TAG.fullmatch(seg) or not seg:
            res.append(seg)
            continue
        sub = SPACES.split(seg)
        res.append("".join(s if SPACES.fullmatch(s) else convert_piece(s, mp) for s in sub))
    return "".join(res)


def entries(data):
    for m in HEADER.finditer(data):
        n = data[m.end() - 8]
        yield m.end(), n


def collect(files):
    cnt = Counter()
    for f in files:
        d = f.read_bytes()
        for start, n in entries(d):
            try:
                t = d[start:start + n].decode("utf-8")
            except UnicodeDecodeError:
                continue
            for seg in TAG.split(t):
                if TAG.fullmatch(seg):
                    continue
                for s in SPACES.split(seg):
                    m = EDGE.match(s)
                    c = norm(m.group(2)) if m else ""
                    c = re.split(r"[-(/]", c)[0].strip() if len(re.split(r"[-(/]", c)[0].strip()) > 3 else c
                    if c:
                        cnt[ALIAS.get(c, c)] += 1
    return cnt


def run(dirs=None, verbose=True):
    files = []
    for d in (dirs or DIRS):
        files += sorted(Path(d).glob("*.aux"))
    mp = Mapper(collect(files))
    # asignacion estable: primero los nombres mas frecuentes
    for key, _ in mp.freq.most_common():
        if key.startswith(KEEP_PREFIX) or NUMERIC.match(key) or len(key) <= 3 or key in KEYWORDS or ROUTE.match(key):
            continue
        if key in POOL_KEYS or key.replace(" ", "") in {k.replace(" ", "") for k in POOL_KEYS}:
            continue
        mp.city(key, 99)
    changed = total = 0
    for f in files:
        d = bytearray(f.read_bytes())
        dirty = False
        for start, n in list(entries(bytes(d))):
            try:
                t = bytes(d[start:start + n]).decode("utf-8")
            except UnicodeDecodeError:
                continue
            if not t.isprintable() and not re.search(r"[\r\n]", t):
                continue
            new = convert_text(t, mp)
            nb = new.encode("utf-8")
            if len(nb) != n:
                new = t
                nb = t.encode("utf-8")
            if nb != d[start:start + n]:
                d[start:start + n] = nb
                dirty = True
                changed += 1
            total += 1
        if dirty:
            f.write_bytes(bytes(d))
    if verbose:
        print(f" -> {changed} textos de letreros cambiados a nombres chilenos ({total} revisados)")
    return changed


if __name__ == "__main__":
    sys.exit(0 if run() >= 0 else 1)
