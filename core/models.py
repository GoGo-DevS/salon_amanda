from urllib.parse import quote

from django.db import models
from django.urls import reverse


class Producto(models.Model):
    nombre            = models.CharField(max_length=255)
    slug              = models.SlugField(max_length=255, unique=True)
    sku               = models.CharField(max_length=100, blank=True)
    precio            = models.PositiveIntegerField(default=0, help_text='Precio referencial en CLP')
    precio_regular    = models.PositiveIntegerField(null=True, blank=True)
    precio_oferta     = models.PositiveIntegerField(null=True, blank=True)
    descripcion_corta = models.TextField(blank=True)
    descripcion       = models.TextField(blank=True)
    imagen_principal  = models.CharField(max_length=255, blank=True, help_text='Ruta relativa en static, ej: img/productos/slug-1.jpg')
    destacado         = models.BooleanField(default=False)
    activo            = models.BooleanField(default=True)
    orden             = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['orden', 'nombre']
        verbose_name = 'Producto'
        verbose_name_plural = 'Productos'

    def __str__(self):
        return self.nombre

    def get_absolute_url(self):
        return reverse('producto_detail', args=[self.slug])

    @property
    def precio_clp(self):
        """Precio formateado estilo chileno: 43.990"""
        if not self.precio:
            return None
        return f"{self.precio:,}".replace(",", ".")

    @property
    def mensaje_whatsapp(self):
        """Texto URL-encoded para el CTA de WhatsApp."""
        return quote(f"Hola Salón Amanda, me interesa el producto: {self.nombre}")


class ProductoImagen(models.Model):
    producto = models.ForeignKey(Producto, related_name='imagenes', on_delete=models.CASCADE)
    imagen   = models.CharField(max_length=255, help_text='Ruta relativa en static')
    orden    = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['orden']
        verbose_name = 'Imagen de producto'
        verbose_name_plural = 'Imágenes de producto'

    def __str__(self):
        return f"{self.producto.nombre} #{self.orden}"
