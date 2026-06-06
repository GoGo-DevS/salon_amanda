from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, render

from .models import Producto


def home(request):
    destacados = Producto.objects.filter(activo=True, destacado=True)[:8]
    return render(request, 'core/home.html', {'productos_destacados': destacados})


def catalogo(request):
    qs = Producto.objects.filter(activo=True)
    q = request.GET.get('q', '').strip()
    if q:
        qs = qs.filter(nombre__icontains=q)

    paginator = Paginator(qs, 12)
    productos = paginator.get_page(request.GET.get('page'))

    return render(request, 'core/catalogo.html', {
        'productos': productos,
        'q': q,
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
