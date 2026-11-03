from django.test import TestCase, override_settings

from core.tests_analitica import SIN_MANIFEST


@override_settings(STORAGES=SIN_MANIFEST)
class CreditoPieTests(TestCase):
    """02-11-2026, consejo de Jorge Urzua: el credito enlaza a gogodevs.cl con
    "Desarrollo web" como texto del enlace, no con la marca."""

    ENLACE = '<a href="https://www.gogodevs.cl/" target="_blank" rel="noopener">Desarrollo web</a> por GoGoDevS'

    def _revisar(self, ruta):
        html = self.client.get(ruta).content.decode()
        self.assertIn(self.ENLACE, html, ruta)
        self.assertNotIn('utm_', html.split('gogodevs.cl', 1)[-1][:80], ruta)

    def test_pie_del_sitio(self):
        self._revisar('/')

    def test_pie_del_tree(self):
        self._revisar('/links/')
