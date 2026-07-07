from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('links/', views.links, name='links'),
    path('productos/', views.catalogo, name='catalogo'),
    path('productos/<slug:slug>/', views.producto_detail, name='producto_detail'),
]
