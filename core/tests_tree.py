from contextlib import contextmanager

from django.test import TestCase, override_settings

from core.tests_analitica import SIN_MANIFEST


class _Base:
    @contextmanager
    def medicion(self, ga):
        with override_settings(GA4_MEASUREMENT_ID=ga, STORAGES=SIN_MANIFEST):
            yield


class TreeMedido(_Base, TestCase):
    """El GoGoDevS Tree (/links/) es la puerta de entrada desde la bio de
    Instagram. Hasta el 04-10-2026 no cargaba GA4 y esas visitas no existian
    en los informes. Ademas cada boton manda "tree_click" con su destino, para
    saber si la gente escribe por WhatsApp o se va al catalogo."""

    def _html(self):
        r = self.client.get('/links/')
        self.assertEqual(r.status_code, 200, 'el Tree no respondio 200; no se midio nada')
        return r.content.decode()

    def test_con_el_id_el_tree_carga_ga_y_el_evento(self):
        with self.medicion('G-PRUEBA1234'):
            html = self._html()
        self.assertIn('googletagmanager.com/gtag/js?id=G-PRUEBA1234', html)
        self.assertIn("gtag('config', 'G-PRUEBA1234')", html)
        self.assertIn("'tree_click'", html)

    def test_sin_el_id_no_se_le_pide_nada_a_google(self):
        with self.medicion(''):
            html = self._html()
        self.assertNotIn('googletagmanager', html)
        self.assertNotIn('tree_click', html)

    def test_el_comentario_de_la_plantilla_no_se_imprime(self):
        with self.medicion('G-PRUEBA1234'):
            html = self._html()
        self.assertNotIn('GA4 tambien en el Tree', html)
        self.assertNotIn('{%', html)
