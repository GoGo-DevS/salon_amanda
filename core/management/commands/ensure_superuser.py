"""Crea o actualiza la cuenta del panel de Sergio desde variables de entorno.

🔴 Por que dejo de estar escrita en el codigo: este repo es PUBLICO, asi que la
clave quedaba a la vista de cualquiera en raw.githubusercontent.com -- y era de
un SUPERUSUARIO, con /admin/ abierto en produccion. Medido el 05-10-2026.

Si PANEL_PASSWORD no esta puesta:
  - cuenta que no existe  -> NO se crea, y se avisa. Antes se creaba con una
    clave conocida, que es peor que no tener cuenta.
  - cuenta que ya existe  -> se deja intacta. El build no puede dejar sin acceso
    a Sergio solo porque falte una variable.
"""
import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Crea o actualiza la cuenta del panel desde PANEL_USERNAME/PANEL_PASSWORD.'

    def handle(self, *args, **options):
        User = get_user_model()
        username = os.environ.get('PANEL_USERNAME', 'Sergio').strip() or 'Sergio'
        password = os.environ.get('PANEL_PASSWORD', '').strip()
        existe = User.objects.filter(username=username).first()

        if not password:
            if existe:
                self.stdout.write(
                    f'PANEL_PASSWORD vacia: se deja la cuenta "{username}" como esta.')
            else:
                self.stderr.write(self.style.ERROR(
                    f'PANEL_PASSWORD vacia y la cuenta "{username}" no existe: NO se crea. '
                    'Ponerla en el panel de Render y volver a desplegar.'))
            return

        if existe:
            existe.set_password(password)
            existe.is_staff = existe.is_superuser = True
            existe.save(update_fields=['password', 'is_staff', 'is_superuser'])
            self.stdout.write(self.style.SUCCESS(
                f'Clave de "{username}" actualizada desde PANEL_PASSWORD.'))
        else:
            User.objects.create_superuser(username=username, email='', password=password)
            self.stdout.write(self.style.SUCCESS(f'Cuenta "{username}" creada.'))
