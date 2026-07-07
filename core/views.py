from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, render

from .models import Producto


def home(request):
    destacados = Producto.objects.filter(activo=True, destacado=True).exclude(sku__startswith='OSIS')[:8]
    osis_productos = Producto.objects.filter(activo=True, sku__startswith='OSIS')[:4]
    return render(request, 'core/home.html', {
        'productos_destacados': destacados,
        'osis_productos': osis_productos,
    })


def catalogo(request):
    qs = Producto.objects.filter(activo=True)
    q = request.GET.get('q', '').strip()
    marca = request.GET.get('marca', '').strip().lower()

    if q:
        qs = qs.filter(nombre__icontains=q)

    if marca == 'schwarzkopf':
        qs = qs.filter(sku__startswith='OSIS')
    elif marca == 'moroccanoil':
        qs = qs.exclude(sku__startswith='OSIS')

    paginator = Paginator(qs, 12)
    productos = paginator.get_page(request.GET.get('page'))

    return render(request, 'core/catalogo.html', {
        'productos': productos,
        'q': q,
        'marca': marca,
        'total': qs.count(),
    })


def producto_detail(request, slug):
    producto = get_object_or_404(Producto, slug=slug, activo=True)
    relacionados = (
        Producto.objects.filter(activo=True)
        .exclude(pk=producto.pk)
        .order_by('?')[:4]
    )
    return render(request, 'core/producto_detail.html', {
        'producto': producto,
        'relacionados': relacionados,
    })


def links(request):
    return render(request, 'core/links.html')
