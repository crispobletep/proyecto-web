from django.db.models import Prefetch, Q
from django.shortcuts import redirect, render

from .models import (
    Categoria,
    Cotizacion,
    Producto,
    VarianteProducto,
)


def inicio(request):
    return render(request, "index.html")


def empresa(request):
    return render(request, "empresa.html")


def servicios(request):
    return render(request, "servicios.html")


def proyectos(request):
    return render(request, "proyectos.html")


def productos(request):
    familia_slug = request.GET.get("familia", "")
    categoria_slug = request.GET.get("categoria", "")

    productos_catalogo = (
        Producto.objects
        .filter(
            publicado=True,
            categoria__activa=True,
        )
        .select_related(
            "categoria",
            "categoria__padre",
            "marca_nueva",
        )
        .prefetch_related(
            "caracteristicas",
            "especificaciones",
            Prefetch(
                "variantes",
                queryset=(
                    VarianteProducto.objects
                    .filter(disponible=True)
                    .prefetch_related("especificaciones")
                ),
                to_attr="variantes_disponibles",
            ),
        )
    )

    if categoria_slug:
        productos_catalogo = productos_catalogo.filter(
            categoria__slug=categoria_slug,
        )

    elif familia_slug:
        productos_catalogo = productos_catalogo.filter(
            Q(categoria__padre__slug=familia_slug)
            | Q(categoria__slug=familia_slug)
        )

    familias = (
        Categoria.objects
        .filter(
            padre__isnull=True,
            activa=True,
        )
        .prefetch_related("subcategorias")
    )

    contexto = {
        "productos": productos_catalogo,
        "familias": familias,
        "familia_activa": familia_slug,
        "categoria_activa": categoria_slug,
    }

    return render(
        request,
        "productos.html",
        contexto,
    )


def contacto(request):
    enviado = request.GET.get("enviado") == "1"
    error = None

    producto_seleccionado = None
    variante_seleccionada = None

    if request.method == "POST":
        producto_id = request.POST.get("producto_id", "").strip()
        variante_id = request.POST.get("variante_id", "").strip()

        if producto_id.isdigit():
            producto_seleccionado = (
                Producto.objects
                .filter(
                    pk=producto_id,
                    publicado=True,
                )
                .select_related("marca_nueva")
                .first()
            )

        if variante_id.isdigit() and producto_seleccionado:
            variante_seleccionada = (
                VarianteProducto.objects
                .filter(
                    pk=variante_id,
                    producto=producto_seleccionado,
                    disponible=True,
                )
                .first()
            )

    else:
        producto_slug = request.GET.get("producto", "").strip()
        variante_id = request.GET.get("variante", "").strip()

        if producto_slug:
            producto_seleccionado = (
                Producto.objects
                .filter(
                    slug=producto_slug,
                    publicado=True,
                )
                .select_related("marca_nueva")
                .first()
            )

        if variante_id.isdigit() and producto_seleccionado:
            variante_seleccionada = (
                VarianteProducto.objects
                .filter(
                    pk=variante_id,
                    producto=producto_seleccionado,
                    disponible=True,
                )
                .first()
            )

    mensaje_sugerido = ""

    if producto_seleccionado:
        mensaje_sugerido = (
            f"Solicito una cotización para "
            f"{producto_seleccionado.nombre}"
        )

        if variante_seleccionada:
            mensaje_sugerido += (
                f", variante {variante_seleccionada.nombre}"
            )

        mensaje_sugerido += "."

    if request.method == "POST":
        nombre = request.POST.get("nombre", "").strip()
        empresa_nombre = request.POST.get("empresa", "").strip()
        email = request.POST.get("email", "").strip()
        telefono = request.POST.get("telefono", "").strip()
        servicio = request.POST.get("servicio", "").strip()
        mensaje = request.POST.get("mensaje", "").strip()

        if nombre and email and telefono and servicio and mensaje:
            Cotizacion.objects.create(
                nombre=nombre,
                empresa=empresa_nombre,
                email=email,
                telefono=telefono,
                servicio=servicio,
                producto=producto_seleccionado,
                variante=variante_seleccionada,
                mensaje=mensaje,
            )

            return redirect("/contacto/?enviado=1")

        error = "Por favor completa todos los campos obligatorios."

    contexto = {
        "enviado": enviado,
        "error": error,
        "producto_seleccionado": producto_seleccionado,
        "variante_seleccionada": variante_seleccionada,
        "mensaje_sugerido": mensaje_sugerido,
        "datos": request.POST if request.method == "POST" else {},
    }

    return render(
        request,
        "contacto.html",
        contexto,
    )