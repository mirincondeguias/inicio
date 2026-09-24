#!/usr/bin/env python3
"""Lee cada carpeta dentro de /guias (imagen + .txt) y crea guias.js para la página.

Las carpetas y archivos con tildes, ñ, espacios o ":" fallan al subirlos a GitHub Pages
(las imágenes salen rotas). Por eso este script los renombra solo a un nombre seguro
(ej. "Formas Geométricas" -> "formas-geometricas"). El título que ve el cliente sale del
campo "titulo:" del .txt, así que el nombre de la carpeta puede ser cualquiera.
"""
import json, re, unicodedata, urllib.parse
from pathlib import Path

RAIZ = Path(__file__).parent
IMGS = {".jpg", ".jpeg", ".png", ".webp", ".gif"}


def clave(s):
    s = unicodedata.normalize("NFD", s.lower())
    return re.sub(r"[^a-z]", "", "".join(c for c in s if not unicodedata.combining(c)))


def seguro(nombre):
    """'Formas Geométricas' -> 'formas-geometricas' | 'foto 1.JPG' -> 'foto-1.jpg'"""
    base, punto, ext = nombre.rpartition(".")
    if not punto or len(ext) > 5:
        base, ext = nombre, ""
    base = unicodedata.normalize("NFD", base.lower())
    base = "".join(c for c in base if not unicodedata.combining(c))
    base = re.sub(r"[^a-z0-9_]+", "-", base).strip("-") or "guia"
    return base + ("." + ext.lower() if ext else "")


def renombrar(ruta_vieja):
    """Renombra a nombre seguro si hace falta. Devuelve la ruta final."""
    nuevo = seguro(ruta_vieja.name)
    if nuevo == ruta_vieja.name:
        return ruta_vieja
    destino = ruta_vieja.with_name(nuevo)
    n = 2
    while destino.exists():
        destino = ruta_vieja.with_name(f"{Path(nuevo).stem}-{n}{Path(nuevo).suffix}")
        n += 1
    ruta_vieja.rename(destino)
    print(f"✎ renombrado: {ruta_vieja.name}  ->  {destino.name}")
    return destino


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
        if k in ("titulo", "categoria", "categorias", "descripcion", "preciodigital", "precioimpresa", "precioimpreso"):
            ultima = {"precioimpreso": "precioimpresa", "categorias": "categoria"}.get(k, k)
            nuevo = m.group(2).strip()
            # varias líneas "categoria:" se suman en vez de pisarse
            datos[ultima] = (datos[ultima] + ", " + nuevo) if ultima == "categoria" and ultima in datos else nuevo
        elif ultima and linea.strip():
            # una categoría por línea también vale
            datos[ultima] += (", " if ultima == "categoria" else " ") + linea.strip()
    return datos


def ruta(carpeta, f):
    return "guias/" + urllib.parse.quote(carpeta.name) + "/" + urllib.parse.quote(f.name)


CONOCIDAS = ["Matemáticas", "Lengua Española", "Ciencias Naturales", "Caligrafía", "Religión y Valores"]
NOMBRES = {clave(c): c for c in CONOCIDAS}  # "matematicas" -> "Matemáticas" (unifica tildes/mayúsculas)


def categorias(v):
    """'Matemáticas, Lengua Española' -> ['Matemáticas', 'Lengua Española'].
    Separa por coma o punto y coma, quita repetidas y unifica la escritura
    (así 'matematicas' y 'Matemáticas' no crean dos secciones distintas)."""
    salida = []
    for p in re.split(r"\s*[,;]\s*", v or ""):
        p = re.sub(r"\s+", " ", p).strip()
        if not p:
            continue
        p = NOMBRES.setdefault(clave(p), p)
        if p not in salida:
            salida.append(p)
    return salida or ["Otras guías"]


guias = []
for carpeta in sorted((RAIZ / "guias").iterdir(), key=lambda p: p.name.lower()):
    if not carpeta.is_dir():
        continue
    # el título original se toma del .txt ANTES de renombrar la carpeta
    if any(c.suffix.lower() == ".txt" for c in carpeta.iterdir()):
        carpeta = renombrar(carpeta)
    for f in list(carpeta.iterdir()):
        if f.is_file():
            renombrar(f)
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
