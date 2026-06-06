from django.contrib import admin

from .models import Producto, ProductoImagen


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
