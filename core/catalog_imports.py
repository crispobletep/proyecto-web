def retirar_variantes(variantes):
    """Retirar del catálogo sin borrar la referencia de cotizaciones anteriores."""
    protegidas = variantes.filter(cotizaciones__isnull=False).values_list("pk", flat=True)
    ids_protegidas = list(protegidas)
    variantes.filter(pk__in=ids_protegidas).update(disponible=False)
    variantes.exclude(pk__in=ids_protegidas).delete()
