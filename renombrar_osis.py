# -*- coding: utf-8 -*-
"""
Renombra fotos_osis/1.jpg..10.jpg al nombre correcto y las mueve a
core/static/img/productos/osis/, luego actualiza productos.json.

Uso:
    ..\venv\Scripts\python.exe renombrar_osis.py
"""
import io, json, os, shutil
from PIL import Image

BASE  = os.path.dirname(__file__)
SRC   = os.path.join(BASE, "fotos_osis")
DEST  = os.path.join(BASE, "core", "static", "img", "productos", "osis")
JSON  = os.path.join(BASE, "core", "data", "productos.json")
MAX_SIDE = 800
JPG_Q    = 82

ORDEN = [
    "osis-velvet-spray-200ml",
    "osis-curl-jam-gel-300ml",
    "osis-refresh-dust-shampoo-seco-300ml",
    "osis-flatliner-termoprotector-200ml",
    "osis-super-shield-protector-300ml",
    "osis-sparkler-spray-brillo-300ml",
    "osis-glow-serum-antifrizz-50ml",
    "osis-bounty-balm-crema-rizos-150ml",
    "osis-dust-it-polvo-texturizante",
    "osis-soft-texture-acondicionador-seco",
]

os.makedirs(DEST, exist_ok=True)

def comprimir(src_path, dest_path):
    img = Image.open(src_path)
    if img.mode in ("RGBA", "P", "LA"):
        fondo = Image.new("RGB", img.size, (255, 255, 255))
        img = img.convert("RGBA")
        fondo.paste(img, mask=img.split()[-1])
        img = fondo
    else:
        img = img.convert("RGB")
    if max(img.size) > MAX_SIDE:
        ratio = MAX_SIDE / max(img.size)
        img = img.resize((int(img.width * ratio), int(img.height * ratio)), Image.LANCZOS)
    img.save(dest_path, "JPEG", quality=JPG_Q, optimize=True, progressive=True)

with open(JSON, encoding="utf-8") as f:
    data = json.load(f)

ok = 0
for i, slug in enumerate(ORDEN, 1):
    # buscar archivo fuente (1.jpg, 01.jpg, 1.png, etc.)
    src = None
    for ext in ("jpg", "jpeg", "png", "webp"):
        for name in (f"{i}.{ext}", f"{i:02d}.{ext}"):
            candidate = os.path.join(SRC, name)
            if os.path.exists(candidate):
                src = candidate
                break
        if src:
            break

    if not src:
        print(f"[{i:2d}] SKIP no encontrado en fotos_osis/ -- slug: {slug}")
        continue

    dest_name = f"{slug}-1.jpg"
    dest_path = os.path.join(DEST, dest_name)
    comprimir(src, dest_path)

    # actualizar JSON
    for p in data:
        if p.get("slug") == slug:
            p["imagenes"] = [f"img/productos/osis/{dest_name}"]
            break

    print(f"[{i:2d}] OK {os.path.basename(src)} -> {dest_name}")
    ok += 1

with open(JSON, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"\n{ok}/10 fotos procesadas -> corre importar_productos para cargar a DB")
print(r"  .\venv\Scripts\python.exe manage.py importar_productos")
