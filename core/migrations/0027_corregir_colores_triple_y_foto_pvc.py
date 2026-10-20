from django.db import migrations


PVC_PRODUCT_SLUG = "catalogo-canalizacion-electricacanalizacion-electricasalida-caja-pvcpng"
PVC_CLEAN_IMAGE = (
    "productos/catalogo/canalizacion-electrica/"
    "salida-caja-pvc-referencia-recortada.png"
)
PVC_OLD_IMAGE = (
    "productos/catalogo/canalizacion-electrica/"
    "salida-caja-pvc-referencia.png"
)
TRIPLE_PRODUCT_SLUG = "catalogo-staford-enchufesstf-et-10a-horizontal"
TRIPLE_CAFE_CODE = "STF-ET-10A-CA-H"
TRIPLE_CAFE_IMAGE = "productos/catalogo/enchufes/enchufe-triple-cafe.png"
TRIPLE_CAFE_COLOR_SUFFIX = "ca"


def corregir_catalogo(apps, schema_editor):
    alias = schema_editor.connection.alias
    Producto = apps.get_model("core", "Producto")
    Variante = apps.get_model("core", "VarianteProducto")
    Imagen = apps.get_model("core", "ImagenProducto")

    producto_pvc = Producto.objects.using(alias).filter(slug=PVC_PRODUCT_SLUG).first()
    if producto_pvc:
        producto_pvc.imagen = PVC_CLEAN_IMAGE
        producto_pvc.save(using=alias, update_fields=("imagen",))

    producto_triple = Producto.objects.using(alias).filter(slug=TRIPLE_PRODUCT_SLUG).first()
    if not producto_triple:
        return

    cafe = Variante.objects.using(alias).filter(
        producto_id=producto_triple.pk,
        codigo=TRIPLE_CAFE_CODE,
    ).first()
    if cafe:
        # El archivo de Café es idéntico al de Champagne; no debe mostrarse
        # como una presentación de color distinta hasta contar con su foto.
        cafe.disponible = False
        cafe.imagen = ""
        cafe.save(using=alias, update_fields=("disponible", "imagen"))

    # La foto duplicada también aparecía como miniatura independiente.
    Imagen.objects.using(alias).filter(
        producto_id=producto_triple.pk,
        clave=f"catalogo-placa-{producto_triple.pk}-{TRIPLE_CAFE_COLOR_SUFFIX}",
    ).delete()


def revertir_catalogo(apps, schema_editor):
    alias = schema_editor.connection.alias
    Producto = apps.get_model("core", "Producto")
    Variante = apps.get_model("core", "VarianteProducto")
    Imagen = apps.get_model("core", "ImagenProducto")

    producto_pvc = Producto.objects.using(alias).filter(slug=PVC_PRODUCT_SLUG).first()
    if producto_pvc:
        producto_pvc.imagen = PVC_OLD_IMAGE
        producto_pvc.save(using=alias, update_fields=("imagen",))

    producto_triple = Producto.objects.using(alias).filter(slug=TRIPLE_PRODUCT_SLUG).first()
    if not producto_triple:
        return

    cafe = Variante.objects.using(alias).filter(
        producto_id=producto_triple.pk,
        codigo=TRIPLE_CAFE_CODE,
    ).first()
    if cafe:
        cafe.disponible = True
        cafe.imagen = TRIPLE_CAFE_IMAGE
        cafe.save(using=alias, update_fields=("disponible", "imagen"))
        imagen, _ = Imagen.objects.using(alias).get_or_create(
            clave=f"catalogo-placa-{producto_triple.pk}-{TRIPLE_CAFE_COLOR_SUFFIX}",
            defaults={
                "producto_id": producto_triple.pk,
                "imagen": TRIPLE_CAFE_IMAGE,
                "texto_alternativo": f"{producto_triple.nombre}, color Café",
                "orden": cafe.orden,
            },
        )
        imagen.producto_id = producto_triple.pk
        imagen.imagen = TRIPLE_CAFE_IMAGE
        imagen.texto_alternativo = f"{producto_triple.nombre}, color Café"
        imagen.orden = cafe.orden
        imagen.save(
            using=alias,
            update_fields=("producto", "imagen", "texto_alternativo", "orden"),
        )
        imagen.variantes.set([cafe.pk])


class Migration(migrations.Migration):
    dependencies = [("core", "0026_ocultar_enchufes_modulares")]

    operations = [
        migrations.RunPython(corregir_catalogo, revertir_catalogo),
    ]
