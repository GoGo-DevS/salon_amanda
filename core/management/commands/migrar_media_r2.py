"""Mueve a R2 las fotos que las promociones tienen hoy en Cloudinary (o en disco).

La clave de cada archivo NO cambia: se sube con el MISMO nombre que el
ImageField ya tiene guardado, asi que no hay que reescribir una sola fila de la
base. Esa es la idea que saco a Punto Parcelas del apuro el 21-08 sin necesitar
la contrasena de su base de produccion.

EL ORDEN NO SE PUEDE INVERTIR: primero correr esto, y SOLO despues poner las
variables de R2 en Render. Al reves, el sitio le pide las fotos a un bucket
vacio y quedan todas rotas -- paso exactamente asi con Punto Parcelas.

Ensayo por defecto. Escribe solo con --confirmar.
"""
from django.core.management.base import BaseCommand
from django.core.files.storage import storages
from core.models import Promocion


class Command(BaseCommand):
    help = 'Copia a R2 las imagenes de las promociones conservando su clave.'

    def add_arguments(self, p):
        p.add_argument('--confirmar', action='store_true',
                       help='Sin esto solo muestra que haria.')

    def handle(self, *a, **o):
        confirmar = o['confirmar']

        import django.conf
        if not getattr(django.conf.settings, 'USAR_R2', False):
            self.stderr.write(self.style.ERROR(
                'Faltan variables de R2. Se exigen las CUATRO: R2_BUCKET_NAME, '
                'R2_ACCOUNT_ID, R2_ACCESS_KEY_ID y R2_SECRET_ACCESS_KEY.'))
            return

        from storages.backends.s3 import S3Storage
        destino = S3Storage()

        # El origen es el storage que la promo esta usando HOY (Cloudinary o disco).
        con_foto = [p for p in Promocion.objects.all() if p.imagen]
        if not con_foto:
            self.stdout.write('No hay ninguna promocion con imagen. Nada que mover.')
            return

        self.stdout.write(f'{len(con_foto)} promocion(es) con imagen.')
        movidas = fallidas = ya_estaban = 0

        for promo in con_foto:
            clave = promo.imagen.name
            try:
                if destino.exists(clave):
                    self.stdout.write(f'  = ya en R2: {clave}')
                    ya_estaban += 1
                    continue
                if not confirmar:
                    self.stdout.write(f'  + subiria: {clave}  ({promo.titulo})')
                    movidas += 1
                    continue
                promo.imagen.open('rb')
                datos = promo.imagen.read()
                promo.imagen.close()
                destino.save(clave, __import__('io').BytesIO(datos))
                # Se comprueba LEYENDO el destino: que save() no reviente no
                # prueba que el archivo quedo.
                if destino.exists(clave):
                    self.stdout.write(self.style.SUCCESS(f'  + {clave}  ({len(datos)/1024:.0f} KB)'))
                    movidas += 1
                else:
                    self.stderr.write(self.style.ERROR(f'  ! subio sin error pero no esta: {clave}'))
                    fallidas += 1
            except Exception as e:
                self.stderr.write(self.style.ERROR(f'  ! {clave}: {e}'))
                fallidas += 1

        resumen = f'{movidas} movidas, {ya_estaban} ya estaban, {fallidas} fallidas'
        if not confirmar:
            self.stdout.write(self.style.WARNING(f'ENSAYO. {resumen}. Repetir con --confirmar.'))
        elif fallidas:
            self.stderr.write(self.style.ERROR(f'CON FALLAS: {resumen}'))
        else:
            self.stdout.write(self.style.SUCCESS(resumen))
