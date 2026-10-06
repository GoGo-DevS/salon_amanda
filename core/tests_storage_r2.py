"""Las fotos de las promociones tienen que sobrevivir, y la eleccion de storage
tiene que degradarse sin tumbar el sitio.

Se prueba leyendo settings.py con cada combinacion de variables, porque la
decision se toma AL IMPORTAR y no hay forma de cambiarla despues con override.
"""
import importlib
import os
from unittest import mock

from django.test import SimpleTestCase


def _cargar(**entorno):
    """Importa settings de nuevo con ese entorno y devuelve el modulo."""
    base = {k: '' for k in (
        'R2_BUCKET_NAME', 'R2_ACCOUNT_ID', 'R2_ACCESS_KEY_ID',
        'R2_SECRET_ACCESS_KEY', 'R2_PUBLIC_DOMAIN', 'CLOUDINARY_URL',
        'DATABASE_URL')}
    base.update(entorno)
    with mock.patch.dict(os.environ, base, clear=False):
        import config.settings as s
        return importlib.reload(s)


LAS_CUATRO = dict(
    R2_BUCKET_NAME='salonamanda', R2_ACCOUNT_ID='abc123',
    R2_ACCESS_KEY_ID='key', R2_SECRET_ACCESS_KEY='secreto')


class EleccionDeStorage(SimpleTestCase):

    def test_con_las_cuatro_variables_usa_R2(self):
        s = _cargar(**LAS_CUATRO)
        self.assertTrue(s.USAR_R2)
        self.assertEqual(s.STORAGES['default']['BACKEND'],
                         'storages.backends.s3.S3Storage')
        self.assertIn('storages', s.INSTALLED_APPS)

    def test_solo_el_bucket_NO_alcanza(self):
        """La guarda que le salvo el deploy a Popi: con el account id vacio el
        endpoint queda en 'https://.r2.cloudflarestorage.com' y boto3 revienta
        al primer archivo. Mejor degradarse que caerse."""
        s = _cargar(R2_BUCKET_NAME='salonamanda')
        self.assertFalse(s.USAR_R2)
        # Sin 'default' Django usa el de disco: degradarse, no morir.
        self.assertNotEqual(s.STORAGES.get('default', {}).get('BACKEND'),
                            'storages.backends.s3.S3Storage')
        self.assertNotIn('storages', s.INSTALLED_APPS)

    def test_faltando_una_sola_NO_usa_R2(self):
        for falta in LAS_CUATRO:
            parcial = {k: v for k, v in LAS_CUATRO.items() if k != falta}
            with self.subTest(falta=falta):
                self.assertFalse(_cargar(**parcial).USAR_R2)

    def test_sin_R2_pero_con_cloudinary_usa_cloudinary(self):
        s = _cargar(CLOUDINARY_URL='cloudinary://1:2@demo')
        self.assertFalse(s.USAR_R2)
        self.assertEqual(s.STORAGES['default']['BACKEND'],
                         'cloudinary_storage.storage.MediaCloudinaryStorage')

    def test_R2_le_gana_a_cloudinary(self):
        """Si estan los dos, manda R2: Cloudinary cobra por servir."""
        s = _cargar(CLOUDINARY_URL='cloudinary://1:2@demo', **LAS_CUATRO)
        self.assertEqual(s.STORAGES['default']['BACKEND'],
                         'storages.backends.s3.S3Storage')
        self.assertNotIn('cloudinary', s.INSTALLED_APPS)

    def test_sin_nada_cae_a_disco_y_no_revienta(self):
        s = _cargar()
        self.assertFalse(s.USAR_R2)
        self.assertNotIn('default', s.STORAGES)   # Django pone el de disco solo
        self.assertIn('staticfiles', s.STORAGES)

    def test_el_endpoint_se_arma_con_el_account_id(self):
        s = _cargar(**LAS_CUATRO)
        self.assertEqual(s.AWS_S3_ENDPOINT_URL,
                         'https://abc123.r2.cloudflarestorage.com')
        self.assertNotIn('https://.r2', s.AWS_S3_ENDPOINT_URL)

    @classmethod
    def tearDownClass(cls):
        _cargar()          # deja settings como estaba para el resto de la suite
        super().tearDownClass()


class EleccionDeBase(SimpleTestCase):
    """Sin DATABASE_URL el sitio sigue andando con SQLite (desarrollo local);
    con ella usa Postgres. Y conn_max_age tiene que ser 0: con 600 Neon nunca
    suspende y factura 24 h por dia, que es lo que le paso a Punto Parcelas."""

    def test_sin_DATABASE_URL_usa_sqlite(self):
        s = _cargar()
        self.assertIn('sqlite3', s.DATABASES['default']['ENGINE'])

    def test_con_DATABASE_URL_usa_postgres(self):
        s = _cargar(DATABASE_URL='postgres://u:p@host.neon.tech/db')
        self.assertIn('postgresql', s.DATABASES['default']['ENGINE'])

    def test_conn_max_age_es_CERO_para_no_quemar_Neon(self):
        s = _cargar(DATABASE_URL='postgres://u:p@host.neon.tech/db')
        self.assertEqual(s.DATABASES['default'].get('CONN_MAX_AGE'), 0)
