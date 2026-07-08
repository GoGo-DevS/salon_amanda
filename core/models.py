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
    def marca(self):
        if self.sku.startswith("OSIS"):
            return "Schwarzkopf"
        return "Moroccanoil"

    @property
    def imagen_url(self):
        if not self.imagen_principal:
            return ""
        if self.imagen_principal.startswith("http"):
            return self.imagen_principal
        from django.templatetags.static import static
        return static(self.imagen_principal)

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


class Promocion(models.Model):
    titulo      = models.CharField(max_length=120)
    descripcion = models.TextField()
    btn_texto   = models.CharField(max_length=60, default='Reservar ahora')
    btn_url     = models.CharField(max_length=500, default='https://link.agendapro.com/cl/salonamanda/9581b2de')
    activa      = models.BooleanField(default=True)
    fecha_fin   = models.DateField(null=True, blank=True, help_text='Dejar vacío = sin vencimiento')

    class Meta:
        verbose_name = 'Promoción'
        verbose_name_plural = 'Promociones'

    def __str__(self):
        return self.titulo


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
