from importlib import import_module

from django.apps import apps as django_apps
from django.test import TestCase, override_settings

from core.models import AGENDA_URL, Promocion
from core.tests_analitica import SIN_MANIFEST

VIEJA = 'https://link.agendapro.com/cl/salonamanda/9581b2de'


@override_settings(STORAGES=SIN_MANIFEST)
class AgendaNueva(TestCase):
    """12-10-2026: el salon cambio AgendaPro por otra agenda. Ninguna pagina
    publica puede seguir mandando a reservar a la agenda vieja."""

    def test_las_paginas_con_boton_de_reserva_llevan_a_la_nueva(self):
        for url in ('/', '/links/', '/transformaciones/'):
            r = self.client.get(url)
            self.assertEqual(r.status_code, 200, url)
            html = r.content.decode()
            self.assertIn(f'href="{AGENDA_URL}"', html, url)
            self.assertNotIn('link.agendapro.com', html, url)

    def test_la_portada_ya_no_nombra_agendapro(self):
        html = self.client.get('/').content.decode()
        self.assertNotIn('AgendaPro', html)

    def test_la_promo_nueva_reserva_en_la_nueva(self):
        self.assertEqual(Promocion(titulo='x', descripcion='y').btn_url, AGENDA_URL)

    def test_la_migracion_pasa_las_promos_guardadas_con_el_link_viejo(self):
        vieja = Promocion.objects.create(titulo='Cyber', descripcion='d', btn_url=VIEJA)
        otra = Promocion.objects.create(titulo='WA', descripcion='d',
                                        btn_url='https://wa.me/56939308418')
        mig = import_module('core.migrations.0004_agenda_nueva')
        mig.a_la_nueva(django_apps, None)
        vieja.refresh_from_db()
        otra.refresh_from_db()
        self.assertEqual(vieja.btn_url, AGENDA_URL)
        self.assertEqual(otra.btn_url, 'https://wa.me/56939308418')
