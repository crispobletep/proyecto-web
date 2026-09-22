from uuid import uuid4

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.text import slugify


class Cotizacion(models.Model):
    nombre = models.CharField(
        max_length=120,
    )

    empresa = models.CharField(
        max_length=150,
        blank=True,
    )

    email = models.EmailField()

    telefono = models.CharField(
        max_length=30,
    )

    servicio = models.CharField(
        max_length=120,
    )

    producto = models.ForeignKey(
        "Producto",
        verbose_name="Producto solicitado",
        on_delete=models.PROTECT,
        related_name="cotizaciones",
        null=True,
        blank=True,
    )

    variante = models.ForeignKey(
        "VarianteProducto",
        verbose_name="Variante solicitada",
        on_delete=models.PROTECT,
        related_name="cotizaciones",
        null=True,
        blank=True,
    )
    mensaje = models.TextField()

    fecha = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        ordering = ["-fecha"]
        verbose_name = "Cotización"
        verbose_name_plural = "Cotizaciones"

    def __str__(self):
        return f"{self.nombre} — {self.servicio}"

    def clean(self):
        super().clean()

        if self.variante_id and not self.producto_id:
            self.producto_id = self.variante.producto_id

        if (
            self.variante_id
            and self.producto_id
            and self.variante.producto_id != self.producto_id
        ):
            raise ValidationError(
                {
                    "variante": (
                        "La variante seleccionada no pertenece al "
                        "producto de esta cotización."
                    ),
                }
            )

    def save(self, *args, **kwargs):
        # La relación producto/variante también queda protegida para
        # importaciones, scripts y usos del ORM fuera del administrador.
        self.full_clean()
        return super().save(*args, **kwargs)


class Categoria(models.Model):
    nombre = models.CharField(
        "Nombre de la categoría",
        max_length=80,
    )

    slug = models.SlugField(
        "Identificador web",
        max_length=80,
        unique=True,
        help_text=(
            "Texto único utilizado en la dirección web. "
            "Se genera automáticamente desde el nombre. "
            "Ejemplo: interruptores-automaticos."
        ),
    )

    padre = models.ForeignKey(
        "self",
        verbose_name="Familia principal",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="subcategorias",
        limit_choices_to={
            "padre__isnull": True,
        },
        help_text=(
            "Deje este campo sin seleccionar para registrar una "
            "familia principal. Para crear una subcategoría, "
            "seleccione la familia a la que pertenece."
        ),
    )

    orden = models.PositiveIntegerField(
        "Orden de visualización",
        default=0,
        help_text=(
            "Los valores menores aparecen primero. "
            "Ejemplo: 1, 2, 3."
        ),
    )

    activa = models.BooleanField(
        "Visible en el catálogo",
        default=True,
        help_text=(
            "Desactive esta opción para ocultar la clasificación "
            "sin eliminarla."
        ),
    )

    class Meta:
        ordering = ["orden", "nombre"]
        verbose_name = "Clasificación de producto"
        verbose_name_plural = "Clasificaciones de productos"

    def __str__(self):
        if self.padre:
            return f"{self.padre.nombre} → {self.nombre}"

        return self.nombre

    @property
    def es_familia(self):
        return self.padre_id is None


class Marca(models.Model):
    nombre = models.CharField(
        max_length=80,
        unique=True,
    )

    slug = models.SlugField(
        "Identificador web",
        max_length=90,
        unique=True,
    )

    logo = models.ImageField(
        upload_to="marcas/",
        blank=True,
    )

    activa = models.BooleanField(
        default=True,
    )

    class Meta:
        ordering = ["nombre"]
        verbose_name = "Marca"
        verbose_name_plural = "Marcas"

    def __str__(self):
        return self.nombre
    
class Producto(models.Model):
    categoria = models.ForeignKey(
        Categoria,
        verbose_name="Subcategoría",
        on_delete=models.PROTECT,
        related_name="productos",
        limit_choices_to={
            "padre__isnull": False,
            "activa": True,
        },
        help_text="Seleccione la subcategoría específica del producto.",
    )
    nombre = models.CharField(
        max_length=180,
    )

    marca = models.CharField(
        "Marca anterior",
        max_length=180,
        blank=True,
        default="",
    )

    marca_nueva = models.ForeignKey(
        Marca,
        verbose_name="Marca",
        on_delete=models.PROTECT,
        related_name="productos",
        null=True,
        blank=True,
    )
    
    modelo = models.CharField(
        "Modelo o referencia",
        max_length=100,
        blank=True,
        help_text=(
            "Modelo oficial indicado por el fabricante. "
            "Puede dejarse vacío si todavía no está disponible."
        ),
    )

    codigo = models.CharField(
        "Código interno o SKU",
        max_length=80,
        unique=True,
        null=True,
        blank=True,
        help_text=(
            "Código único utilizado para identificar el producto. "
            "Puede dejarse vacío."
        ),
    )
    slug = models.SlugField(
        "Identificador web",
        max_length=200,
        unique=True,
        help_text=(
            "Se genera automáticamente desde el nombre del producto."
        ),
    )


    subtitulo = models.CharField(
        max_length=120,
        help_text="Ejemplo: Protección eléctrica",
    )

    descripcion = models.TextField()

    imagen = models.ImageField(
        upload_to="productos/",
        blank=True,
        help_text="Imagen principal que aparecerá en el catálogo",
    )

    texto_alternativo = models.CharField(
        max_length=180,
        blank=True,
        help_text="Descripción accesible de la imagen",
    )

    etiqueta_visual = models.CharField(
        max_length=80,
        blank=True,
        help_text="Ejemplo: PROTECCIÓN, SEGURIDAD o LÍNEA DLX",
    )

    orden = models.PositiveIntegerField(
        default=0,
        help_text="Determina la posición del producto en el catálogo",
    )

    publicado = models.BooleanField(
        "Publicado en el catálogo",
        default=False,
        help_text=(
            "Active esta opción cuando el producto esté listo "
            "para aparecer públicamente."
        ),
    )

    creado = models.DateTimeField(
        auto_now_add=True,
    )

    actualizado = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = ["orden", "nombre"]
        verbose_name = "Producto"
        verbose_name_plural = "Productos"

    def __str__(self):
        return self.nombre

    def clean(self):
        super().clean()

        if self.categoria_id and self.categoria.padre_id is None:
            raise ValidationError(
                {
                    "categoria": (
                        "El producto debe pertenecer a una subcategoría, "
                        "no directamente a una familia principal."
                    ),
                }
            )

    @property
    def alt_imagen(self):
        return self.texto_alternativo or self.nombre

    @property
    def etiqueta_catalogo(self):
        return self.etiqueta_visual or self.categoria.nombre


class CaracteristicaProducto(models.Model):
    producto = models.ForeignKey(
        Producto,
        on_delete=models.CASCADE,
        related_name="caracteristicas",
    )

    texto = models.CharField(
        max_length=180,
    )

    orden = models.PositiveIntegerField(
        default=0,
        help_text="Determina el orden de la característica",
    )

    class Meta:
        ordering = ["orden", "id"]
        verbose_name = "Característica del producto"
        verbose_name_plural = "Características de los productos"

    def __str__(self):
        return f"{self.producto.nombre}: {self.texto}"


class EspecificacionProducto(models.Model):
    producto = models.ForeignKey(
        Producto,
        on_delete=models.CASCADE,
        related_name="especificaciones",
    )

    nombre = models.CharField(
        "Nombre de la especificación",
        max_length=100,
        help_text="Ejemplo: Corriente nominal, Polos o Protección IP.",
    )

    valor = models.CharField(
        "Valor",
        max_length=100,
        help_text="Ejemplo: 16, 1P+N o IP44.",
    )

    unidad = models.CharField(
        "Unidad",
        max_length=30,
        blank=True,
        help_text="Ejemplo: A, V, mm o Hz.",
    )

    orden = models.PositiveIntegerField(
        "Orden de visualización",
        default=0,
    )

    class Meta:
        ordering = ["orden", "nombre"]
        verbose_name = "Especificación técnica"
        verbose_name_plural = "Especificaciones técnicas"

        constraints = [
            models.UniqueConstraint(
                fields=["producto", "nombre"],
                name="especificacion_unica_por_producto",
            ),
        ]

    def __str__(self):
        contenido = f"{self.nombre}: {self.valor}"

        if self.unidad:
            contenido = f"{contenido} {self.unidad}"

        return contenido

class VarianteProducto(models.Model):
    producto = models.ForeignKey(
        Producto,
        on_delete=models.CASCADE,
        related_name="variantes",
    )

    nombre = models.CharField(
        "Nombre de la variante",
        max_length=140,
        help_text="Ejemplo: 2 polos · 25 A",
    )

    modelo = models.CharField(
        "Modelo o referencia",
        max_length=100,
        blank=True,
    )

    codigo = models.CharField(
        "Código o SKU",
        max_length=100,
        unique=True,
        null=True,
        blank=True,
    )

    imagen = models.ImageField(
        upload_to="productos/variantes/",
        blank=True,
    )

    disponible = models.BooleanField(
        default=True,
    )

    orden = models.PositiveIntegerField(
        default=0,
    )

    class Meta:
        ordering = ["orden", "nombre"]
        verbose_name = "Variante del producto"
        verbose_name_plural = "Variantes de los productos"

        constraints = [
            models.UniqueConstraint(
                fields=["producto", "nombre"],
                name="variante_unica_por_producto",
            ),
        ]

    def __str__(self):
        return f"{self.producto.nombre} — {self.nombre}"


class ImagenProducto(models.Model):
    producto = models.ForeignKey(
        Producto,
        on_delete=models.CASCADE,
        related_name="imagenes_catalogo",
    )

    variantes = models.ManyToManyField(
        VarianteProducto,
        related_name="imagenes_catalogo",
        blank=True,
        help_text=(
            "Variantes o códigos representados por esta fotografía. "
            "Puede seleccionar varias cuando comparten la misma imagen."
        ),
    )

    clave = models.SlugField(
        "Identificador de importación",
        max_length=220,
        unique=True,
        help_text=(
            "Identificador estable utilizado por las cargas automáticas "
            "para actualizar la imagen sin duplicarla."
        ),
    )

    imagen = models.ImageField(
        upload_to="productos/catalogo/",
    )

    texto_alternativo = models.CharField(
        max_length=180,
        blank=True,
    )

    orden = models.PositiveIntegerField(
        default=0,
    )

    class Meta:
        ordering = ["orden", "id"]
        verbose_name = "Imagen de producto"
        verbose_name_plural = "Imágenes de productos"

    def __str__(self):
        return f"{self.producto.nombre} — imagen {self.orden or self.pk}"

    def save(self, *args, **kwargs):
        # El administrador permite agregar fotografías dentro de la ficha del
        # producto sin pedir al usuario una clave técnica. Las importaciones
        # pueden seguir entregando su propia clave estable.
        if not self.clave:
            producto = getattr(self, "producto", None)
            producto_slug = getattr(producto, "slug", "producto")
            self.clave = slugify(
                f"manual-{producto_slug}-{uuid4().hex[:12]}"
            )

        return super().save(*args, **kwargs)


class EspecificacionVariante(models.Model):
    variante = models.ForeignKey(
        VarianteProducto,
        on_delete=models.CASCADE,
        related_name="especificaciones",
    )

    nombre = models.CharField(
        max_length=100,
    )

    valor = models.CharField(
        max_length=120,
    )

    unidad = models.CharField(
        max_length=30,
        blank=True,
        help_text="Ejemplo: A, W, mm, V o mA",
    )

    orden = models.PositiveIntegerField(
        default=0,
    )

    class Meta:
        ordering = ["orden", "id"]
        verbose_name = "Especificación de variante"
        verbose_name_plural = "Especificaciones de las variantes"

        constraints = [
            models.UniqueConstraint(
                fields=["variante", "nombre"],
                name="especificacion_unica_por_variante",
            ),
        ]

    def __str__(self):
        return f"{self.variante}: {self.nombre}"
