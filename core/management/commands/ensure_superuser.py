from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Crea superusuario Sergio si no existe'

    def handle(self, *args, **options):
        User = get_user_model()
        username = 'Sergio'
        password = 'salonamanda123'
        if User.objects.filter(username=username).exists():
            self.stdout.write(f'Usuario {username} ya existe.')
        else:
            User.objects.create_superuser(username=username, email='', password=password)
            self.stdout.write(self.style.SUCCESS(f'Superusuario {username} creado.'))
