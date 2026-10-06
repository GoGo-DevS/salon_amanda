"""La cuenta del panel y el /admin/ de Django.

Este repo es PUBLICO. El 05-10-2026 la clave del superusuario estaba escrita en
ensure_superuser.py y /admin/ respondia 200 en produccion: cualquiera que
encontrara el repo entraba con permisos totales. Estas pruebas existen para que
no vuelva a pasar en silencio.
"""
import os
from io import StringIO
from unittest import mock

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import SimpleTestCase, TestCase, override_settings
from django.urls import NoReverseMatch, clear_url_caches, reverse


def _recargar_urls():
    """reload() no alcanza: Django cachea el URLconf ya resuelto."""
    from importlib import reload
    import config.urls as u
    reload(u)
    clear_url_caches()


class LaClaveNoVivePorEscritoEnElRepo(SimpleTestCase):

    def test_el_codigo_no_trae_ninguna_clave(self):
        ruta = os.path.join(os.path.dirname(__file__),
                            'management', 'commands', 'ensure_superuser.py')
        codigo = open(ruta, encoding='utf-8').read()
        # Lo que importa no es una palabra concreta sino que no haya NINGUNA
        # asignacion literal: password = '...'
        import re
        literales = re.findall(r"password\s*=\s*['\"][^'\"]+['\"]", codigo)
        self.assertEqual(literales, [], f'hay una clave escrita: {literales}')
        self.assertIn('PANEL_PASSWORD', codigo)


class CuentaDelPanel(TestCase):

    def _correr(self):
        salida, error = StringIO(), StringIO()
        call_command('ensure_superuser', stdout=salida, stderr=error)
        return salida.getvalue() + error.getvalue()

    def test_sin_variable_y_sin_cuenta_NO_se_crea(self):
        """Crear una cuenta con clave conocida es peor que no tenerla."""
        with mock.patch.dict(os.environ, {'PANEL_PASSWORD': ''}):
            self._correr()
        self.assertFalse(get_user_model().objects.exists())

    def test_sin_variable_pero_con_cuenta_NO_la_toca(self):
        """Un deploy no puede dejar a Sergio afuera porque falte una variable."""
        u = get_user_model().objects.create_superuser('Sergio', '', 'la-que-tenia')
        with mock.patch.dict(os.environ, {'PANEL_PASSWORD': ''}):
            self._correr()
        u.refresh_from_db()
        self.assertTrue(u.check_password('la-que-tenia'))

    def test_con_variable_crea_la_cuenta(self):
        with mock.patch.dict(os.environ, {'PANEL_PASSWORD': 'una-nueva-larga'}):
            self._correr()
        u = get_user_model().objects.get(username='Sergio')
        self.assertTrue(u.check_password('una-nueva-larga'))
        self.assertTrue(u.is_superuser)

    def test_con_variable_ACTUALIZA_la_clave_existente(self):
        """Asi se rota la que quedo publica, sin entrar a la base a mano."""
        get_user_model().objects.create_superuser('Sergio', '', 'la-vieja-publica')
        with mock.patch.dict(os.environ, {'PANEL_PASSWORD': 'la-nueva'}):
            self._correr()
        u = get_user_model().objects.get(username='Sergio')
        self.assertTrue(u.check_password('la-nueva'))
        self.assertFalse(u.check_password('la-vieja-publica'))


class AdminDeDjango(SimpleTestCase):

    @override_settings(DEBUG=False)
    def test_en_produccion_no_existe(self):
        _recargar_urls()
        with self.assertRaises(NoReverseMatch):
            reverse('admin:index')

    @override_settings(DEBUG=True)
    def test_en_desarrollo_si_existe(self):
        _recargar_urls()
        self.assertEqual(reverse('admin:index'), '/admin/')

    @classmethod
    def tearDownClass(cls):
        _recargar_urls()
        super().tearDownClass()
