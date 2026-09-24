#!/usr/bin/env python3
"""Lee cada carpeta dentro de /guias (imagen + .txt) y crea guias.js para la página."""
import json, re, unicodedata, urllib.parse
from pathlib import Path

RAIZ = Path(__file__).parent
IMGS = {".jpg", ".jpeg", ".png", ".webp", ".gif"}


def clave(s):
    s = unicodedata.normalize("NFD", s.lower())
    return re.sub(r"[^a-z]", "", "".join(c for c in s if not unicodedata.combining(c)))


def numero(v):
    v = re.sub(r"[^\d.,]", "", v or "")
    if not v:
        return None
    if "." in v:
        v = v.replace(",", "")
    elif "," in v:
        v = v.replace(",", ".") if len(v.split(",")[-1]) == 2 else v.replace(",", "")
    n = float(v)
    return int(n) if n == int(n) else n


def leer_txt(ruta):
    try:
        txt = ruta.read_text(encoding="utf-8-sig")
    except UnicodeDecodeError:
        txt = ruta.read_text(encoding="latin-1")
    datos, ultima = {}, None
    for linea in txt.splitlines():
        m = re.match(r"^\s*([^:=]{3,25})\s*[:=]\s*(.*)$", linea)
        k = clave(m.group(1)) if m else ""
        if k in ("titulo", "categoria", "descripcion", "preciodigital", "precioimpresa", "precioimpreso"):
            ultima = "precioimpresa" if k == "precioimpreso" else k
            datos[ultima] = m.group(2).strip()
        elif ultima and linea.strip():
            datos[ultima] += " " + linea.strip()
    return datos


def ruta(carpeta, f):
    return "guias/" + urllib.parse.quote(carpeta.name) + "/" + urllib.parse.quote(f.name)


def categorias(v):
    """'Matemáticas, Lengua Española' -> ['Matemáticas', 'Lengua Española']"""
    partes = re.split(r"\s*,\s*", v or "")
    return [p.strip() for p in partes if p.strip()] or ["Otras guías"]


guias = []
for carpeta in sorted((RAIZ / "guias").iterdir(), key=lambda p: p.name.lower()):
    if not carpeta.is_dir():
        continue
    fotos = sorted(f for f in carpeta.iterdir() if f.suffix.lower() in IMGS)
    txts = sorted(carpeta.glob("*.txt"))
    if not fotos or not txts:
        print(f"⚠ {carpeta.name}: falta la imagen o el .txt, se omite")
        continue
    d = leer_txt(txts[0])
    dig, imp = numero(d.get("preciodigital")), numero(d.get("precioimpresa"))
    if dig is None and imp is None:
        print(f"⚠ {carpeta.name}: no tiene ningún precio, se omite")
        continue
    guias.append({
        "titulo": d.get("titulo") or carpeta.name,
        "categoria": categorias(d.get("categoria")),
        "descripcion": d.get("descripcion", ""),
        "digital": dig,
        "impreso": imp,
        "img": ruta(carpeta, fotos[0]),
        "imgs": [ruta(carpeta, f) for f in fotos],
    })

(RAIZ / "guias.js").write_text(
    "window.GUIAS = " + json.dumps(guias, ensure_ascii=False, indent=1) + ";\n", encoding="utf-8")
print(f"✔ {len(guias)} guía(s) en guias.js")
