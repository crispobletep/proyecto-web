from django.conf import settings
from django.core.mail import EmailMultiAlternatives, get_connection
from django.template.loader import render_to_string
from django.utils import timezone


def enviar_notificacion_cotizacion(cotizacion):
    """Notifica al equipo comercial y confirma la recepción al cliente."""
    destinatarios = [
        correo.strip()
        for correo in settings.COTIZACIONES_EMAIL.split(",")
        if correo.strip()
    ]

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

    mensajes = []

    if destinatarios:
        mensaje_interno = EmailMultiAlternatives(
            subject=f"Nueva cotización {identificador} · {referencia}",
            body=contenido_texto,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=destinatarios,
            reply_to=[cotizacion.email],
        )
        mensaje_interno.attach_alternative(contenido_html, "text/html")
        mensajes.append(mensaje_interno)

    contexto_cliente = {
        **contexto,
        "referencia": referencia,
    }
    confirmacion_texto = render_to_string(
        "emails/cotizacion_confirmacion.txt",
        contexto_cliente,
    )
    confirmacion_html = render_to_string(
        "emails/cotizacion_confirmacion.html",
        contexto_cliente,
    )
    confirmacion_cliente = EmailMultiAlternatives(
        subject=f"Recibimos tu solicitud de cotización · {identificador}",
        body=confirmacion_texto,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[cotizacion.email],
    )
    confirmacion_cliente.attach_alternative(
        confirmacion_html,
        "text/html",
    )
    mensajes.append(confirmacion_cliente)

    conexion = get_connection(fail_silently=False)
    return conexion.send_messages(mensajes)
