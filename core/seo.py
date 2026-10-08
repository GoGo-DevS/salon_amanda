"""sitemap.xml, robots.txt y la URL canonica.

POR QUE (07-10-2026): el sitio no tenia ninguna de las tres. /sitemap.xml y
/robots.txt daban 404, y ninguna pagina declaraba su canonica, asi que
/productos/?q=shampoo y /productos/?marca=osis se indexaban como paginas
distintas compitiendo contra /productos/. Mismo hueco que tenia Sindicato AZA.

El dominio canonico es www: salonamanda.cl hace 301 a www.salonamanda.cl.
"""
from django.http import HttpResponse
from django.urls import reverse
from django.utils.html import escape

from .models import Producto

DOMINIO = 'https://www.salonamanda.cl'
HOSTS_PROPIOS = ('salonamanda.cl', 'www.salonamanda.cl')

# /links/ queda fuera a proposito: es el Tree de la bio de Instagram, una
# pagina de botones sin contenido propio. El panel tampoco va, va en robots.
PAGINAS = ('home', 'profesionales', 'transformaciones', 'catalogo')


def base_url(request):
    """En produccion siempre el dominio canonico; en local, el host real
    para que el sitemap de prueba no apunte afuera."""
    host = request.get_host().split(':')[0]
    if host in HOSTS_PROPIOS or host.endswith('.onrender.com'):
        return DOMINIO
    return f'{request.scheme}://{request.get_host()}'


def sitemap(request):
    base = base_url(request)
    rutas = [reverse(n) for n in PAGINAS]
    rutas += [p.get_absolute_url()
              for p in Producto.objects.filter(activo=True).order_by('slug')]
    filas = ''.join(f'<url><loc>{escape(base + r)}</loc></url>' for r in rutas)
    xml = ('<?xml version="1.0" encoding="UTF-8"?>'
           '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
           f'{filas}</urlset>')
    return HttpResponse(xml, content_type='application/xml')


def robots(request):
    texto = (
        'User-agent: *\n'
        'Disallow: /panel/\n'
        'Disallow: /admin/\n'
        '\n'
        f'Sitemap: {base_url(request)}/sitemap.xml\n'
    )
    return HttpResponse(texto, content_type='text/plain; charset=utf-8')


def canonica(request):
    """Context processor: la URL canonica de la pagina, SIN query string.
    Asi los filtros del catalogo no se indexan como paginas aparte."""
    return {'canonical_url': base_url(request) + request.path}
