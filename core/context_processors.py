EMPRESA = {
    "nombre_comercial": "PH Servicios Electrónicos",
    "razon_social": (
        "Patricio Hernández Proyectos y Montajes Eléctricos Limitada"
    ),
    "rut": "76.096.219-5",
    "telefono": "+56 2 2983 688",
    "telefono_href": "tel:+5622983688",
    "correo": "administracion@phinstalaciones.cl",
    "correo_href": "mailto:administracion@phinstalaciones.cl",
    "direccion": "San Diego 1325, Santiago Centro, Santiago",
    "mapa_url": (
        "https://www.google.com/maps/search/?api=1&query="
        "San+Diego+1325%2C+Santiago%2C+Chile"
    ),
    "actividad": (
        "Proyectos y montajes eléctricos · Venta de materiales "
        "para la construcción"
    ),
}


def datos_empresa(request):
    return {"empresa_info": EMPRESA}
