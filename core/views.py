from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, render

from .models import Producto


def home(request):
    destacados = Producto.objects.filter(activo=True, destacado=True).exclude(sku__startswith='OSIS')[:8]
    osis_productos = Producto.objects.filter(activo=True, sku__startswith='OSIS')[:4]
    pares_transf = [
        {
            'titulo': 'Corrección de Color',
            'profesional': 'Danitza San Martín',
            'antes': 'img/profesionales/danitza/danitza-03.jpg',
            'despues': 'img/profesionales/danitza/danitza-04.jpg',
        },
        {
            'titulo': 'Coloración & Ondas',
            'profesional': 'Dominique Castillo',
            'antes': 'img/profesionales/dominique/dominique-07.jpg',
            'despues': 'img/profesionales/dominique/dominique-08.jpg',
        },
        {
            'titulo': 'Alisado Keratina',
            'profesional': 'Dominique Castillo',
            'antes': 'img/profesionales/dominique/dominique-04.jpg',
            'despues': 'img/profesionales/dominique/dominique-03.jpg',
        },
        {
            'titulo': 'Platinado Premium',
            'profesional': 'Dominique Castillo',
            'antes': 'img/profesionales/dominique/dominique-11.jpg',
            'despues': 'img/profesionales/dominique/dominique-12.jpg',
        },
    ]
    return render(request, 'core/home.html', {
        'productos_destacados': destacados,
        'osis_productos': osis_productos,
        'pares_transf': pares_transf,
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


def transformaciones(request):
    pares = [
        {
            'titulo': 'Corrección de Color',
            'descripcion': 'De naranja dañado a mechas ash naturales con ondas perfectas.',
            'profesional': 'Danitza San Martín',
            'antes': 'img/profesionales/danitza/danitza-03.jpg',
            'despues': 'img/profesionales/danitza/danitza-04.jpg',
        },
        {
            'titulo': 'Coloración & Ondas',
            'descripcion': 'Coloración caramelo con efecto de volumen y movimiento natural.',
            'profesional': 'Dominique Castillo',
            'antes': 'img/profesionales/dominique/dominique-07.jpg',
            'despues': 'img/profesionales/dominique/dominique-08.jpg',
        },
        {
            'titulo': 'Alisado Keratina',
            'descripcion': 'Tratamiento alisado con keratina para brillo y suavidad extrema.',
            'profesional': 'Dominique Castillo',
            'antes': 'img/profesionales/dominique/dominique-04.jpg',
            'despues': 'img/profesionales/dominique/dominique-03.jpg',
        },
        {
            'titulo': 'Platinado Premium',
            'descripcion': 'Decoloración controlada con tonificación platinada en corte corto.',
            'profesional': 'Dominique Castillo',
            'antes': 'img/profesionales/dominique/dominique-11.jpg',
            'despues': 'img/profesionales/dominique/dominique-12.jpg',
        },
    ]
    return render(request, 'core/transformaciones.html', {'pares': pares})


def profesionales(request):
    equipo = [
        {
            'slug': 'dominique',
            'nombre': 'Dominique Castillo',
            'titulo': 'Directora & Colorista Senior',
            'directora': True,
            'descripcion': 'Especialista en coloración, técnicas avanzadas de color, decoloración, corte, visagismo, manejo de rulos, permanentes, alisados y tratamientos capilares.',
            'certificaciones': ['Schwarkprof', 'Moroccanoil'],
            'fotos': [f'img/profesionales/dominique/dominique-{i:02d}.jpg' for i in range(1, 13)],
        },
        {
            'slug': 'danitza',
            'nombre': 'Danitza San Martín',
            'titulo': 'Colorista Senior',
            'directora': False,
            'descripcion': 'Especialista en coloración, técnicas avanzadas de color, decoloración, técnicas de touca, corte, visagismo, alisados y tratamientos capilares.',
            'certificaciones': ['Redken', 'L\'Oréal', 'Richee'],
            'fotos': [f'img/profesionales/danitza/danitza-{i:02d}.jpg' for i in range(1, 11)],
        },
        {
            'slug': 'angela',
            'nombre': 'Angela Contreras',
            'titulo': 'Nail Art & Lash Lifting',
            'directora': False,
            'descripcion': 'Especialista en esmaltado Semi-Permanente, extensión con soft gel, nivelación, Lifting tradicional y técnica coreana.',
            'certificaciones': [],
            'fotos': [f'img/profesionales/angela/angela-{i:02d}.jpg' for i in range(1, 7)],
        },
        {
            'slug': 'estefania',
            'nombre': 'Estefanía Padilla',
            'titulo': 'Cosmetóloga & Nail Art',
            'directora': False,
            'descripcion': 'Especialista en extensión con acrílico, soft gel, nivelación, esmaltado Semi-Permanente, diseños y depilación con cera.',
            'certificaciones': [],
            'fotos': [f'img/profesionales/estefania/estefania-{i:02d}.jpg' for i in range(1, 7)],
        },
    ]
    return render(request, 'core/profesionales.html', {'equipo': equipo})
