from django.urls import path
from . import views


urlpatterns = [

    path("", views.inicio, name="inicio"),

    path("productos/", views.productos, name="productos"),

    path(
        "empresa/",
        views.empresa,
        name="empresa"
    ),

    path(
        "servicios/",
        views.servicios,
        name="servicios"
    ),

    path(
        "proyectos/",
        views.proyectos,
        name="proyectos"
    ),

    path(
        "contacto/",
        views.contacto,
        name="contacto"
    ),

]