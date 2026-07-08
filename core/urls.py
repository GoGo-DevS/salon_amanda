from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('links/', views.links, name='links'),
    path('profesionales/', views.profesionales, name='profesionales'),
    path('transformaciones/', views.transformaciones, name='transformaciones'),
    path('productos/', views.catalogo, name='catalogo'),
    path('productos/<slug:slug>/', views.producto_detail, name='producto_detail'),
    # Panel interno
    path('panel/', views.panel_dashboard, name='panel_dashboard'),
    path('panel/login/', views.panel_login, name='panel_login'),
    path('panel/logout/', views.panel_logout, name='panel_logout'),
    path('panel/promociones/nueva/', views.panel_promo_crear, name='panel_promo_crear'),
    path('panel/promociones/<int:pk>/editar/', views.panel_promo_editar, name='panel_promo_editar'),
    path('panel/promociones/<int:pk>/eliminar/', views.panel_promo_eliminar, name='panel_promo_eliminar'),
    path('panel/promociones/<int:pk>/toggle/', views.panel_promo_toggle, name='panel_promo_toggle'),
]
