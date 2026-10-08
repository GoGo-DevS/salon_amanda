import re

from django.test import TestCase, override_settings

from core.models import Producto
from core.tests_analitica import SIN_MANIFEST

WWW = {'HTTP_HOST': 'www.salonamanda.cl'}


@override_settings(STORAGES=SIN_MANIFEST, ALLOWED_HOSTS=['*'])
class SitemapRobotsCanonica(TestCase):
    """Hasta el 07-10-2026 /sitemap.xml y /robots.txt daban 404 y ninguna
    pagina declaraba su canonica: los filtros del catalogo se indexaban como
    paginas distintas compitiendo contra /productos/."""

    def setUp(self):
        Producto.objects.create(nombre='Shampoo OSIS', slug='shampoo-osis', sku='OSIS1')
        Producto.objects.create(nombre='Retirado', slug='retirado', activo=False)

    def test_sitemap_lista_paginas_y_solo_productos_activos(self):
        r = self.client.get('/sitemap.xml', **WWW)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r['Content-Type'], 'application/xml')
        locs = re.findall(r'<loc>([^<]+)</loc>', r.content.decode())
        for ruta in ('/', '/profesionales/', '/transformaciones/', '/productos/',
                     '/productos/shampoo-osis/'):
            self.assertIn('https://www.salonamanda.cl' + ruta, locs)
        self.assertNotIn('https://www.salonamanda.cl/productos/retirado/', locs)
        self.assertFalse([l for l in locs if '/panel/' in l or '/links/' in l])

    def test_el_apex_tambien_declara_www(self):
        r = self.client.get('/sitemap.xml', HTTP_HOST='salonamanda.cl')
        locs = re.findall(r'<loc>([^<]+)</loc>', r.content.decode())
        self.assertTrue(locs and all(l.startswith('https://www.salonamanda.cl/') for l in locs))

    def test_robots_bloquea_el_panel_y_apunta_al_sitemap(self):
        r = self.client.get('/robots.txt', **WWW)
        self.assertEqual(r.status_code, 200)
        t = r.content.decode()
        self.assertIn('Disallow: /panel/', t)
        self.assertIn('Disallow: /admin/', t)
        self.assertIn('Sitemap: https://www.salonamanda.cl/sitemap.xml', t)

    def test_la_canonica_no_lleva_los_filtros_del_catalogo(self):
        r = self.client.get('/productos/?q=shampoo&marca=schwarzkopf', **WWW)
        self.assertEqual(r.status_code, 200)
        canon = re.findall(r'<link rel="canonical" href="([^"]+)"', r.content.decode())
        self.assertEqual(canon, ['https://www.salonamanda.cl/productos/'])

    def test_cada_ficha_declara_su_propia_canonica(self):
        r = self.client.get('/productos/shampoo-osis/', **WWW)
        canon = re.findall(r'<link rel="canonical" href="([^"]+)"', r.content.decode())
        self.assertEqual(canon, ['https://www.salonamanda.cl/productos/shampoo-osis/'])
