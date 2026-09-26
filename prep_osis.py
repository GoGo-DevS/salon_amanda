# -*- coding: utf-8 -*-
"""
Prep one-time (local): scrapa los 10 productos Schwarzkopf Osis+ desde
MercadoLibre (via meli.la), descarga y comprime imagenes a
static/img/productos/osis/, y agrega/actualiza las entradas en productos.json.

Requiere: pip install requests pillow beautifulsoup4 lxml
"""
import io, json, os, re, time
import requests
from bs4 import BeautifulSoup
from PIL import Image

OUT_IMG  = r"C:\Users\diego\Proyectos GoGoDevS\GoGoCRM\salon_amanda\core\static\img\productos\osis"
OUT_JSON = r"C:\Users\diego\Proyectos GoGoDevS\GoGoCRM\salon_amanda\core\data\productos.json"
MAX_IMGS = 4
MAX_SIDE = 800
JPG_Q    = 82

OSIS_LINKS = {
    "osis-velvet-spray-200ml":              "https://meli.la/142AWxE",
    "osis-curl-jam-gel-300ml":              "https://meli.la/26kAX8M",
    "osis-refresh-dust-shampoo-seco-300ml": "https://meli.la/2ky7GnR",
    "osis-flatliner-termoprotector-200ml":  "https://meli.la/1HBaT33",
    "osis-super-shield-protector-300ml":    "https://meli.la/1qCHwsD",
    "osis-sparkler-spray-brillo-300ml":     "https://meli.la/2PM3MBm",
    "osis-glow-serum-antifrizz-50ml":       "https://meli.la/2MnBfUc",
    "osis-bounty-balm-crema-rizos-150ml":   "https://meli.la/2F5wAUn",
    "osis-dust-it-polvo-texturizante":      "https://meli.la/2ZD55yQ",
    "osis-soft-texture-acondicionador-seco":"https://meli.la/2dkKM34",
}

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "es-CL,es;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

os.makedirs(OUT_IMG, exist_ok=True)


def expandir_url(short):
    """Sigue el redirect de meli.la y devuelve la URL real de ML."""
    r = requests.get(short, headers=HEADERS, allow_redirects=True, timeout=20)
    url = r.url
    # ML social share pages redirigen a /social/... — extraer URL real via og:url
    if '/social/' in url:
        soup = BeautifulSoup(r.text, "lxml")
        og = soup.find("meta", property="og:url")
        if og and og.get("content") and "mercadolibre" in og["content"]:
            return og["content"]
        canonical = soup.find("link", rel="canonical")
        if canonical and canonical.get("href") and "mercadolibre" in canonical["href"]:
            return canonical["href"]
        # Buscar link directo al articulo en el HTML
        a = soup.find("a", href=re.compile(r"articulo\.mercadolibre|mercadolibre\.cl/[A-Z]"))
        if a:
            return a["href"]
    return url


def scrape_ml(url):
    """Extrae nombre, precio, descripcion e imagenes desde una pagina de ML."""
    r = requests.get(url, headers=HEADERS, timeout=30)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "lxml")

    # --- nombre ---
    nombre = ""
    tag = soup.find("h1", class_=re.compile(r"ui-pdp-title|item-title"))
    if tag:
        nombre = tag.get_text(strip=True)

    # --- precio ---
    precio = 0
    p_tag = soup.find("span", class_=re.compile(r"price-tag-fraction|andes-money-amount__fraction"))
    if p_tag:
        precio_str = re.sub(r"\D", "", p_tag.get_text())
        precio = int(precio_str) if precio_str else 0

    # Fallback: og:description suele tener "$XX.XXX"
    if not precio:
        og_desc = soup.find("meta", property="og:description")
        if og_desc:
            m = re.search(r"\$\s*([\d\.,]+)", og_desc.get("content", ""))
            if m:
                precio = int(re.sub(r"\D", "", m.group(1)))

    # Fallback: cualquier span/div que contenga precio CLP
    if not precio:
        for tag in soup.find_all(["span", "b", "strong"], string=re.compile(r"\$\s*\d[\d\.]{3,}")):
            m = re.search(r"\$\s*([\d\.]+)", tag.get_text())
            if m:
                precio = int(re.sub(r"\D", "", m.group(1)))
                break

    # --- descripcion corta desde JSON-LD ---
    desc_corta = ""
    desc_full  = ""
    for script in soup.find_all("script", type="application/ld+json"):
        try:
            d = json.loads(script.string or "")
            if isinstance(d, dict) and d.get("@type") in ("Product", "ItemPage"):
                desc_corta = (d.get("description") or "")[:300]
                desc_full  = d.get("description") or ""
                if not nombre:
                    nombre = d.get("name", "")
                break
        except Exception:
            pass

    # Si no hay JSON-LD, intentar con la seccion de descripcion HTML
    if not desc_corta:
        div = soup.find("div", class_=re.compile(r"ui-pdp-description|item-description"))
        if div:
            txt = div.get_text(" ", strip=True)
            desc_corta = txt[:300]
            desc_full  = txt

    # --- imagenes ---
    img_urls = []
    # JSON-LD primero
    for script in soup.find_all("script", type="application/ld+json"):
        try:
            d = json.loads(script.string or "")
            if isinstance(d, dict) and d.get("@type") == "Product":
                imgs = d.get("image", [])
                if isinstance(imgs, str):
                    imgs = [imgs]
                img_urls = [u for u in imgs if u.startswith("http")]
                break
        except Exception:
            pass

    # Fallback: galeria HTML
    if not img_urls:
        for tag in soup.find_all("figure", class_=re.compile(r"ui-pdp-gallery")):
            for img in tag.find_all("img"):
                src = img.get("data-zoom") or img.get("src") or ""
                if "mlstatic.com" in src and src not in img_urls:
                    img_urls.append(src)

    # Fallback: og:image (funciona en social share pages de ML)
    if not img_urls:
        og_img = soup.find("meta", property="og:image")
        if og_img and og_img.get("content", "").startswith("http"):
            img_urls = [og_img["content"]]

    # Fallback: cualquier img con mlstatic.com
    if not img_urls:
        for img in soup.find_all("img"):
            src = img.get("src", "")
            if "mlstatic.com" in src and src not in img_urls:
                img_urls.append(src)

    # Convertir thumbnails a imagenes grandes (quitar -S,_I_-XXXXX guion bajo)
    big_urls = []
    for u in img_urls[:MAX_IMGS]:
        # ML: cambiar -O.jpg o -I.jpg a version sin sufijo (original)
        u2 = re.sub(r"-[A-Z]\.jpg", "-O.jpg", u)
        u2 = re.sub(r"\.(webp|png)$", ".jpg", u2)
        big_urls.append(u2)

    return {
        "nombre":        nombre,
        "precio":        precio,
        "descripcion_corta": desc_corta.strip(),
        "descripcion":   desc_full.strip(),
        "img_urls":      big_urls,
    }


def descargar_y_comprimir(url, destino):
    try:
        r = requests.get(url, headers=HEADERS, timeout=30)
        r.raise_for_status()
        img = Image.open(io.BytesIO(r.content))
        if img.mode in ("RGBA", "P", "LA"):
            fondo = Image.new("RGB", img.size, (255, 255, 255))
            img = img.convert("RGBA")
            fondo.paste(img, mask=img.split()[-1])
            img = fondo
        else:
            img = img.convert("RGB")
        if max(img.size) > MAX_SIDE:
            ratio = MAX_SIDE / max(img.size)
            img = img.resize(
                (int(img.width * ratio), int(img.height * ratio)), Image.LANCZOS
            )
        img.save(destino, "JPEG", quality=JPG_Q, optimize=True, progressive=True)
        return True
    except Exception as e:
        print(f"    ! imagen error: {e}")
        return False


# ---- cargar JSON existente ----
with open(OUT_JSON, encoding="utf-8") as f:
    data = json.load(f)

osis_existente = {p["slug"]: p for p in data if p.get("sku", "").startswith("OSIS")}
resto = [p for p in data if not p.get("sku", "").startswith("OSIS")]

nuevos = []
for i, (slug, short_url) in enumerate(OSIS_LINKS.items(), 1):
    print(f"\n[{i}/10] {slug}")

    try:
        url_real = expandir_url(short_url)
        print(f"  URL: {url_real[:80]}")
        info = scrape_ml(url_real)
    except Exception as e:
        print(f"  ! scrape falló: {e} — usando datos existentes")
        info = None

    base = osis_existente.get(slug, {})

    if info and info["nombre"]:
        nombre = info["nombre"]
        precio = info["precio"]
        desc_c = info["descripcion_corta"]
        desc_f = info["descripcion"]
        img_src_urls = info["img_urls"]
    else:
        nombre = base.get("nombre", slug)
        precio = 0
        desc_c = base.get("descripcion_corta", "")
        desc_f = base.get("descripcion", "")
        img_src_urls = []

    print(f"  nombre: {nombre[:60]}")
    print(f"  precio: {precio} | imgs disponibles: {len(img_src_urls)}")
    time.sleep(1)

    # Descargar imagenes
    imagenes = []
    for j, img_url in enumerate(img_src_urls[:MAX_IMGS], 1):
        fname   = f"{slug}-{j}.jpg"
        destino = os.path.join(OUT_IMG, fname)
        if os.path.exists(destino):
            print(f"    img {j} ya existe, skip")
            imagenes.append(f"img/productos/osis/{fname}")
            continue
        print(f"    descargando img {j}...")
        ok = descargar_y_comprimir(img_url, destino)
        if ok:
            imagenes.append(f"img/productos/osis/{fname}")
        time.sleep(0.3)

    # Si no hay imagenes descargadas, conservar placeholder
    if not imagenes:
        imagenes = base.get("imagenes", [f"https://placehold.co/400x400/111111/ffffff?text=OSIS%2B"])

    nuevos.append({
        "id":              base.get("id", 1000 + i),
        "sku":             base.get("sku", f"OSIS-{slug.upper()[:10]}"),
        "nombre":          nombre,
        "slug":            slug,
        "precio":          precio,
        "precio_regular":  precio or None,
        "precio_oferta":   precio or None,
        "descripcion_corta": desc_c,
        "descripcion":     desc_f,
        "url_origen":      short_url,
        "imagenes":        imagenes,
    })

# ---- guardar JSON ----
data_final = resto + nuevos
with open(OUT_JSON, "w", encoding="utf-8") as f:
    json.dump(data_final, f, ensure_ascii=False, indent=2)

con_img = sum(1 for p in nuevos if p["imagenes"] and not str(p["imagenes"][0]).startswith("https://placehold"))
print(f"\n========== RESUMEN ==========")
print(f"Osis scraped: {len(nuevos)} | Con imagen real: {con_img} | Sin imagen: {len(nuevos)-con_img}")
print(f"JSON: {OUT_JSON}")
print(f"\nSi las imagenes son locales, corre:")
print(f"  .\\venv\\Scripts\\python.exe manage.py importar_productos")
