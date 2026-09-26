"""GA4 en el sitio publico, y NUNCA en el panel.

El panel muestra datos personales. Mandarle esas URLs a Google es un problema de
privacidad, no una preferencia: por eso el identificador solo lo hereda la
plantilla publica, y hay una prueba que falla si alguien lo agrega a la del panel.

La medicion se apaga sola sin la variable: asi el codigo se despliega antes de
que exista la propiedad sin cambiarle el comportamiento al sitio.
"""
from django.test import TestCase, override_settings

# El manifest de estaticos local esta viejo y la home revienta con
# "Missing staticfiles manifest entry". Es del entorno, no del sitio: el archivo
# esta en el repo y en produccion el build corre collectstatic. Estas pruebas
# miden GA4, no los estaticos, asi que se sirven sin manifest.
SIN_MANIFEST = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
}


class Ga4(TestCase):

    @override_settings(GA4_MEASUREMENT_ID="", STORAGES=SIN_MANIFEST)
    def test_sin_la_variable_no_se_le_pide_nada_a_google(self):
        r = self.client.get("/")
        self.assertEqual(r.status_code, 200, "la home no respondio 200; no se midio nada")
        self.assertNotIn("googletagmanager", r.content.decode())

    @override_settings(GA4_MEASUREMENT_ID="G-PRUEBA1234", STORAGES=SIN_MANIFEST)
    def test_con_la_variable_carga_el_script_con_ese_id(self):
        html = self.client.get("/").content.decode()
        self.assertIn("googletagmanager.com/gtag/js?id=G-PRUEBA1234", html)
        self.assertIn("gtag(\x27config\x27, \x27G-PRUEBA1234\x27)", html)

    def test_la_plantilla_del_panel_no_menciona_el_identificador(self):
        """Si esto falla, se estan enviando a Google las URLs con datos de
        personas. No se arregla cambiando la prueba."""
        with open("core/templates/core/panel/base.html", encoding="utf-8") as f:
            panel = f.read()
        self.assertNotIn("ga4_id", panel)
        self.assertNotIn("googletagmanager", panel)
