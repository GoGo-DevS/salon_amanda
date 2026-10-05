import io
from unittest import mock
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from core.models import Promocion


class LaFotoQueFallaNoTumbaLaPagina(TestCase):
    """05-10-2026: guardar una promo con foto daba Server Error (500) y no se
    creaba nada. Lo que se arregla no es la subida (eso es del storage), sino
    que el cliente pierda la pagina entera y lo que escribio."""

    def setUp(self):
        U = get_user_model()
        U.objects.create_user('sergio', password='x')
        self.c = Client()
        self.c.login(username='sergio', password='x')

    def _foto(self):
        return SimpleUploadedFile('p.jpg', b'\xff\xd8\xff\xdb' + b'0' * 50,
                                  content_type='image/jpeg')

    def datos(self, **extra):
        d = {'titulo': 'Cyber uñas', 'descripcion': '$31.900',
             'btn_texto': 'Reservar', 'btn_url': 'https://x.cl',
             'fecha_fin': '2026-10-07', 'activa': 'on'}
        d.update(extra)
        return d

    def test_si_la_subida_falla_la_promo_igual_se_crea(self):
        with mock.patch('django.core.files.storage.default_storage._save',
                        side_effect=Exception('cloud_name is disabled')):
            r = self.c.post('/panel/promociones/nueva/',
                            self.datos(imagen=self._foto()))
        self.assertEqual(r.status_code, 302, 'devolvio error en vez de guardar')
        p = Promocion.objects.get()
        self.assertEqual(p.titulo, 'Cyber uñas')
        self.assertFalse(p.imagen, 'quedo con una imagen que nunca subio')

    def test_el_panel_dice_por_que_no_subio(self):
        with mock.patch('django.core.files.storage.default_storage._save',
                        side_effect=Exception('cloud_name is disabled')):
            r = self.c.post('/panel/promociones/nueva/',
                            self.datos(imagen=self._foto()), follow=True)
        txt = ' '.join(str(m) for m in r.context['messages'])
        self.assertIn('no se pudo subir', txt)
        self.assertIn('cloud_name is disabled', txt)

    def test_sin_foto_sigue_funcionando_igual(self):
        r = self.c.post('/panel/promociones/nueva/', self.datos())
        self.assertEqual(r.status_code, 302)
        self.assertEqual(Promocion.objects.count(), 1)
