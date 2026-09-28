from django.conf import settings
from django.core.mail import EmailMessage
from django.utils import timezone


def enviar_notificacion_cotizacion(cotizacion):
    """Envía al equipo comercial una copia legible de la cotización."""
    destinatarios = [
        correo.strip()
        for correo in settings.COTIZACIONES_EMAIL.split(",")
        if correo.strip()
    ]

    if not destinatarios:
        return 0

    producto = cotizacion.producto.nombre if cotizacion.producto else "No indicado"
    variante = (
        cotizacion.variante.nombre if cotizacion.variante else "No indicada"
    )
    fecha = timezone.localtime(cotizacion.fecha).strftime("%d-%m-%Y %H:%M")

    contenido = "\n".join(
        (
            "Se recibió una nueva solicitud de cotización desde el sitio web.",
            "",
            f"Identificador: COT-{cotizacion.pk:06d}",
            f"Fecha: {fecha}",
            f"Nombre: {cotizacion.nombre}",
            f"Empresa: {cotizacion.empresa or 'No indicada'}",
            f"Correo: {cotizacion.email}",
            f"Teléfono: {cotizacion.telefono}",
            f"Servicio: {cotizacion.servicio}",
            f"Producto: {producto}",
            f"Variante: {variante}",
            "",
            "Descripción:",
            cotizacion.mensaje,
            "",
            "La solicitud también quedó guardada en el administrador de Django.",
        )
    )

    mensaje = EmailMessage(
        subject=(
            f"Nueva cotización COT-{cotizacion.pk:06d} · "
            f"{cotizacion.servicio}"
        ),
        body=contenido,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=destinatarios,
        reply_to=[cotizacion.email],
    )

    return mensaje.send(fail_silently=False)
