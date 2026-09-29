from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
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

    identificador = f"COT-{cotizacion.pk:06d}"
    contexto = {
        "cotizacion": cotizacion,
        "identificador": identificador,
        "fecha": timezone.localtime(cotizacion.fecha).strftime(
            "%d-%m-%Y %H:%M"
        ),
        "mensaje_generico": (
            "Esta solicitud fue enviada desde el formulario del sitio web. "
            "Contacta al cliente para confirmar los antecedentes y preparar "
            "la cotización correspondiente."
        ),
    }
    contenido_texto = render_to_string(
        "emails/cotizacion_nueva.txt",
        contexto,
    )
    contenido_html = render_to_string(
        "emails/cotizacion_nueva.html",
        contexto,
    )

    referencia = cotizacion.servicio
    if cotizacion.producto:
        referencia = cotizacion.producto.nombre
    elif cotizacion.proyecto:
        referencia = cotizacion.proyecto.nombre

    mensaje = EmailMultiAlternatives(
        subject=f"Nueva cotización {identificador} · {referencia}",
        body=contenido_texto,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=destinatarios,
        reply_to=[cotizacion.email],
    )
    mensaje.attach_alternative(contenido_html, "text/html")

    return mensaje.send(fail_silently=False)
