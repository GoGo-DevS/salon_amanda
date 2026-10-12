"""El salon cambio AgendaPro por otra agenda (oct-2026).

Ademas del default, las promociones YA guardadas con el link viejo pasan al
nuevo: si no, el boton de la promo publicada seguiria llevando a AgendaPro.
Solo se tocan las que tienen EXACTAMENTE el link viejo; una promo con otro
destino (WhatsApp, Instagram) queda como esta.
"""

from django.db import migrations, models

VIEJA = 'https://link.agendapro.com/cl/salonamanda/9581b2de'
NUEVA = 'https://salonamanda.synaptechspa.cl'


def a_la_nueva(apps, schema_editor):
    Promocion = apps.get_model('core', 'Promocion')
    Promocion.objects.filter(btn_url=VIEJA).update(btn_url=NUEVA)


def a_la_vieja(apps, schema_editor):
    Promocion = apps.get_model('core', 'Promocion')
    Promocion.objects.filter(btn_url=NUEVA).update(btn_url=VIEJA)


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_promocion_imagen'),
    ]

    operations = [
        migrations.AlterField(
            model_name='promocion',
            name='btn_url',
            field=models.CharField(default=NUEVA, max_length=500),
        ),
        migrations.RunPython(a_la_nueva, a_la_vieja),
    ]
