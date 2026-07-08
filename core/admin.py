from django.contrib import admin

from .models import Producto, ProductoImagen, Promocion


class ProductoImagenInline(admin.TabularInline):
    model = ProductoImagen
    extra = 0


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display  = ('nombre', 'precio', 'destacado', 'activo', 'orden')
    list_editable = ('destacado', 'activo', 'orden')
    list_filter   = ('destacado', 'activo')
    search_fields = ('nombre', 'sku', 'slug')
    prepopulated_fields = {'slug': ('nombre',)}
    inlines = [ProductoImagenInline]


@admin.register(Promocion)
class PromocionAdmin(admin.ModelAdmin):
    list_display  = ('titulo', 'activa', 'fecha_fin')
    list_editable = ('activa',)
    fieldsets = (
        (None, {'fields': ('titulo', 'descripcion', 'activa')}),
        ('Botón', {'fields': ('btn_texto', 'btn_url')}),
        ('Vigencia', {'fields': ('fecha_fin',), 'description': 'Dejar fecha_fin vacío = promo sin vencimiento'}),
    )
