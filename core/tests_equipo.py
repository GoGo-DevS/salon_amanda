"""El equipo vive escrito a mano en dos lugares (views.profesionales y la
portada). Estas pruebas cuidan lo que se rompe en silencio al cambiar a
alguien: una foto que se nombra en la vista pero no está en el repo (el sitio
muestra un cuadro roto y nadie se entera) y una profesional que entra a una
página y no a la otra.
"""
from django.contrib.staticfiles import finders
from django.test import TestCase, override_settings
from django.urls import reverse

from core.tests_analitica import SIN_MANIFEST


@override_settings(STORAGES=SIN_MANIFEST)
class EquipoTests(TestCase):

    def _equipo(self):
        resp = self.client.get(reverse('profesionales'))
        self.assertEqual(resp.status_code, 200)
        return resp, {p['slug']: p for p in resp.context['equipo']}

    def test_cada_foto_de_trabajos_existe_en_el_repo(self):
        _, equipo = self._equipo()
        for p in equipo.values():
            for foto in p['fotos']:
                self.assertTrue(finders.find(foto),
                                f"{p['nombre']}: falta {foto}")

    def test_evelyn_publica_sus_cuatro_trabajos(self):
        resp, equipo = self._equipo()
        self.assertEqual(len(equipo['evelyn']['fotos']), 4)
        self.assertContains(resp, 'evelyn-01')

    def test_valeria_entra_con_sus_trabajos_y_sin_foto_de_perfil(self):
        resp, equipo = self._equipo()
        valeria = equipo['valeria']
        self.assertEqual(valeria['nombre'], 'Valeria Cabrera')
        self.assertEqual(len(valeria['fotos']), 8)
        # Sin valeria-perfil.jpg cae a la inicial, nunca a una imagen rota.
        self.assertFalse(valeria['tiene_foto'])
        self.assertNotContains(resp, 'valeria-perfil.jpg')
        self.assertContains(resp, 'Reservar con Valeria')

    def test_las_pestanas_de_valeria_van_sobre_las_de_pelo(self):
        # Pedido de Sergio, 07-11-2026: "que aparezca sobre las de pelo".
        resp, equipo = self._equipo()
        titulos = [g['titulo'] for g in equipo['valeria']['grupos']]
        self.assertEqual(titulos, ['Pestañas', 'Cabello'])
        html = resp.content.decode()
        self.assertLess(html.index('valeria-pestanas-04'), html.index('valeria-01'))

    def test_quien_no_declara_grupos_sigue_igual(self):
        # Una sola fila sin subtítulo y nunca más de 6, como antes del cambio.
        _, equipo = self._equipo()
        for slug in ('dominique', 'angela', 'evelyn'):
            grupos = equipo[slug]['grupos']
            self.assertEqual(len(grupos), 1, slug)
            self.assertEqual(grupos[0]['titulo'], '', slug)
            self.assertLessEqual(len(grupos[0]['fotos']), 6, slug)
        self.assertEqual(equipo['paola']['grupos'], [])

    def test_la_portada_y_la_pagina_del_equipo_tienen_a_las_mismas(self):
        _, equipo = self._equipo()
        portada = self.client.get('/').content.decode()
        for p in equipo.values():
            self.assertIn(p['nombre'], portada,
                          f"{p['nombre']} está en /profesionales/ y no en la portada")
