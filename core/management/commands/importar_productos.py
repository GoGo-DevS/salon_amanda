import json
import os

from django.conf import settings
from django.core.management.base import BaseCommand

from core.models import Producto, ProductoImagen


# Productos a destacar en el home (por palabra clave en el nombre, en orden de prioridad)
DESTACADO_KEYWORDS = [
    "aceite de arg",
    "tratamiento",
    "mascarilla hidratante",
    "shampoo hidratante",
    "acondicionador hidratante",
    "defensa perfecta",
    "crema de mano",
    "mascarilla con color",
]
MAX_DESTACADOS = 8


class Command(BaseCommand):
    help = "Importa productos Moroccanoil desde core/data/productos.json (idempotente)."

    def handle(self, *args, **options):
        ruta = os.path.join(settings.BASE_DIR, "core", "data", "productos.json")
        if not os.path.exists(ruta):
            self.stderr.write(self.style.ERROR(f"No se encontró {ruta}"))
            return

        with open(ruta, encoding="utf-8") as f:
            data = json.load(f)

        destacados = self._elegir_destacados(data)

        creados = 0
        actualizados = 0
        for i, p in enumerate(data):
            imgs = p.get("imagenes") or []
            obj, created = Producto.objects.update_or_create(
                slug=p["slug"],
                defaults={
                    "nombre": p["nombre"],
                    "sku": p.get("sku", ""),
                    "precio": p.get("precio") or 0,
                    "precio_regular": p.get("precio_regular"),
                    "precio_oferta": p.get("precio_oferta"),
                    "descripcion_corta": p.get("descripcion_corta", ""),
                    "descripcion": p.get("descripcion", ""),
                    "imagen_principal": imgs[0] if imgs else "",
                    "destacado": p["slug"] in destacados,
                    "activo": True,
                    "orden": i,
                },
            )
            obj.imagenes.all().delete()
            for j, ruta_img in enumerate(imgs):
                ProductoImagen.objects.create(producto=obj, imagen=ruta_img, orden=j)
            creados += int(created)
            actualizados += int(not created)

        self.stdout.write(self.style.SUCCESS(
            f"Import OK: {creados} creados, {actualizados} actualizados, "
            f"{len(destacados)} destacados, {Producto.objects.count()} en total."
        ))

    def _elegir_destacados(self, data):
        destacados = []
        for kw in DESTACADO_KEYWORDS:
            for p in data:
                if len(destacados) >= MAX_DESTACADOS:
                    break
                if p["slug"] in destacados:
                    continue
                if p.get("imagenes") and kw in p["nombre"].lower():
                    destacados.append(p["slug"])
        # Rellenar hasta MAX_DESTACADOS con cualquier producto con imagen
        for p in data:
            if len(destacados) >= MAX_DESTACADOS:
                break
            if p.get("imagenes") and p["slug"] not in destacados:
                destacados.append(p["slug"])
        return set(destacados)
