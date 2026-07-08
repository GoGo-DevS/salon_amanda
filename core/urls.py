from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('links/', views.links, name='links'),
    path('profesionales/', views.profesionales, name='profesionales'),
    path('transformaciones/', views.transformaciones, name='transformaciones'),
    path('productos/', views.catalogo, name='catalogo'),
    path('productos/<slug:slug>/', views.producto_detail, name='producto_detail'),
]
