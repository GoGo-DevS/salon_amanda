from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import models
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from .models import Producto, Promocion


def home(request):
    destacados = Producto.objects.filter(activo=True, destacado=True).exclude(sku__startswith='OSIS')[:8]
    osis_productos = Producto.objects.filter(activo=True, sku__startswith='OSIS')[:4]
    pares_transf = [
        {'antes': 'img/transformaciones/danitza-a1.jpg', 'despues': 'img/transformaciones/danitza-a2.jpg'},
        {'antes': 'img/transformaciones/danitza-b1.jpg', 'despues': 'img/transformaciones/danitza-b2.jpg'},
        {'antes': 'img/transformaciones/dominique-1antes.jpg', 'despues': 'img/transformaciones/dominique-1despues.jpg'},
        {'antes': 'img/transformaciones/dominique-2antes.jpg', 'despues': 'img/transformaciones/dominique-2despues.jpg'},
    ]
    hoy = timezone.now().date()
    promociones = Promocion.objects.filter(activa=True).filter(
        models.Q(fecha_fin__isnull=True) | models.Q(fecha_fin__gte=hoy)
    )
    return render(request, 'core/home.html', {
        'productos_destacados': destacados,
        'osis_productos': osis_productos,
        'pares_transf': pares_transf,
        'promociones': promociones,
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
        {'antes': 'img/transformaciones/danitza-a1.jpg', 'despues': 'img/transformaciones/danitza-a2.jpg'},
        {'antes': 'img/transformaciones/danitza-b1.jpg', 'despues': 'img/transformaciones/danitza-b2.jpg'},
        {'antes': 'img/transformaciones/danitza-c1.jpg', 'despues': 'img/transformaciones/danitza-c2.jpg'},
        {'antes': 'img/transformaciones/danitza-d1.jpg', 'despues': 'img/transformaciones/danitza-d2.jpg'},
        {'antes': 'img/transformaciones/dominique-1antes.jpg', 'despues': 'img/transformaciones/dominique-1despues.jpg'},
        {'antes': 'img/transformaciones/dominique-2antes.jpg', 'despues': 'img/transformaciones/dominique-2despues.jpg'},
        {'antes': 'img/transformaciones/dominique-3antes.jpg', 'despues': 'img/transformaciones/dominique-3despues.jpg'},
        {'antes': 'img/transformaciones/dominique-4antes.jpg', 'despues': 'img/transformaciones/dominique-4despues.jpg'},
        {'antes': 'img/transformaciones/dominique-5antes.jpg', 'despues': 'img/transformaciones/dominique-5despues.jpg'},
        {'antes': 'img/transformaciones/dominique-6antes.jpg', 'despues': 'img/transformaciones/dominique-6despues.jpg'},
    ]
    return render(request, 'core/transformaciones.html', {'pares': pares})


# ── PANEL INTERNO ────────────────────────────────────────────

def panel_login(request):
    if request.user.is_authenticated:
        return redirect('panel_dashboard')
    error = None
    if request.method == 'POST':
        user = authenticate(request,
                            username=request.POST.get('username', ''),
                            password=request.POST.get('password', ''))
        if user:
            login(request, user)
            return redirect('panel_dashboard')
        error = 'Usuario o contraseña incorrectos.'
    return render(request, 'core/panel/login.html', {'error': error})


def panel_logout(request):
    logout(request)
    return redirect('panel_login')


@login_required(login_url='panel_login')
def panel_dashboard(request):
    promociones = Promocion.objects.all().order_by('-activa', 'titulo')
    return render(request, 'core/panel/dashboard.html', {'promociones': promociones})


@login_required(login_url='panel_login')
def panel_promo_crear(request):
    if request.method == 'POST':
        promo = Promocion(
            titulo=request.POST.get('titulo', '').strip(),
            descripcion=request.POST.get('descripcion', '').strip(),
            btn_texto=request.POST.get('btn_texto', 'Reservar ahora').strip(),
            btn_url=request.POST.get('btn_url', '').strip(),
            fecha_fin=request.POST.get('fecha_fin') or None,
            activa=bool(request.POST.get('activa')),
        )
        if request.FILES.get('imagen'):
            promo.imagen = request.FILES['imagen']
        promo.save()
        messages.success(request, 'Promoción creada correctamente.')
        return redirect('panel_dashboard')
    return render(request, 'core/panel/promo_form.html', {'promo': None})


@login_required(login_url='panel_login')
def panel_promo_editar(request, pk):
    promo = get_object_or_404(Promocion, pk=pk)
    if request.method == 'POST':
        promo.titulo = request.POST.get('titulo', '').strip()
        promo.descripcion = request.POST.get('descripcion', '').strip()
        promo.btn_texto = request.POST.get('btn_texto', 'Reservar ahora').strip()
        promo.btn_url = request.POST.get('btn_url', '').strip()
        promo.fecha_fin = request.POST.get('fecha_fin') or None
        promo.activa = bool(request.POST.get('activa'))
        if request.FILES.get('imagen'):
            promo.imagen = request.FILES['imagen']
        promo.save()
        messages.success(request, 'Promoción actualizada.')
        return redirect('panel_dashboard')
    return render(request, 'core/panel/promo_form.html', {'promo': promo})


@login_required(login_url='panel_login')
@require_POST
def panel_promo_eliminar(request, pk):
    promo = get_object_or_404(Promocion, pk=pk)
    promo.delete()
    messages.success(request, 'Promoción eliminada.')
    return redirect('panel_dashboard')


@login_required(login_url='panel_login')
@require_POST
def panel_promo_toggle(request, pk):
    promo = get_object_or_404(Promocion, pk=pk)
    promo.activa = not promo.activa
    promo.save()
    estado = 'activada' if promo.activa else 'desactivada'
    messages.success(request, f'Promoción {estado}.')
    return redirect('panel_dashboard')


def profesionales(request):
    equipo = [
        {
            'slug': 'dominique',
            'nombre': 'Dominique Castillo',
            'titulo': 'Directora & Colorista Senior',
            'directora': True,
            'descripcion': 'Especialista en coloración, técnicas avanzadas de color, decoloración, corte, visagismo, manejo de rulos, permanentes, alisados y tratamientos capilares.',
            'certificaciones': ['Schwarkprof', 'Moroccanoil'],
            'fotos': [
                'img/transformaciones/dominique-1despues.jpg',
                'img/transformaciones/dominique-2despues.jpg',
                'img/transformaciones/dominique-3despues.jpg',
                'img/transformaciones/dominique-4despues.jpg',
                'img/transformaciones/dominique-5despues.jpg',
                'img/transformaciones/dominique-6despues.jpg',
            ],
        },
        {
            'slug': 'danitza',
            'nombre': 'Danitza San Martín',
            'titulo': 'Colorista Senior',
            'directora': False,
            'descripcion': 'Especialista en coloración, técnicas avanzadas de color, decoloración, técnicas de touca, corte, visagismo, alisados y tratamientos capilares.',
            'certificaciones': ['Redken', 'L\'Oréal', 'Richee'],
            'fotos': [
                'img/profesionales/danitza/danitza-02.jpg',
                'img/profesionales/danitza/danitza-04.jpg',
                'img/profesionales/danitza/danitza-05.jpg',
                'img/profesionales/danitza/danitza-06.jpg',
                'img/profesionales/danitza/danitza-07.jpg',
            ],
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
