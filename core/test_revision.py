from django.core.exceptions import ValidationError
from django.test import TestCase

from .catalog_imports import retirar_variantes
from .forms import CotizacionForm
from .models import Categoria, Cotizacion, Producto, Proyecto, VarianteProducto


class RevisionRegresionesTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.familia = Categoria.objects.create(nombre='Familia', slug='familia')
        cls.categoria = Categoria.objects.create(nombre='Categoría', slug='categoria', padre=cls.familia)
        cls.producto = Producto.objects.create(nombre='Producto', slug='producto', categoria=cls.categoria, publicado=True)
        cls.variante = VarianteProducto.objects.create(producto=cls.producto, nombre='Variante')
        cls.proyecto = Proyecto.objects.create(nombre='Proyecto', slug='proyecto', sector='comercial', estado='finalizado', descripcion='Proyecto de prueba')

    def datos_cotizacion(self):
        return dict(nombre='Cliente Prueba', email='cliente@example.com', telefono='+56912345678', servicio='Productos', mensaje='Solicitud de prueba suficientemente larga.')

    def test_identificadores_invalidos_no_producen_error_de_servidor(self):
        for valor in ['²', '999999999999999999999999', '-1', 'abc']:
            with self.subTest(valor=valor):
                self.assertEqual(self.client.get('/productos/', {'marca': valor}).status_code, 200)
                self.assertEqual(self.client.get('/contacto/', {'producto': self.producto.slug, 'variante': valor}).status_code, 200)
                response = self.client.post('/contacto/', {'producto_id': valor, 'proyecto_id': valor, 'variante_id': valor})
                self.assertEqual(response.status_code, 200)
                self.assertTrue(response.context['formulario'].errors)
        self.assertFalse(Cotizacion.objects.exists())

    def test_post_vacio_muestra_errores(self):
        response = self.client.post('/contacto/', {})
        self.assertTrue(response.context['formulario'].is_bound)
        self.assertIn('nombre', response.context['formulario'].errors)

    def test_no_cotizar_producto_de_familia_oculta(self):
        self.familia.activa = False
        self.familia.save()
        response = self.client.get('/contacto/', {'producto': self.producto.slug})
        self.assertIsNone(response.context['producto_seleccionado'])

    def test_proyecto_y_variante_no_pueden_combinarse(self):
        with self.assertRaises(ValidationError):
            Cotizacion.objects.create(**self.datos_cotizacion(), proyecto=self.proyecto, variante=self.variante)

    def test_retirar_variante_conserva_cotizaciones(self):
        cotizacion = Cotizacion.objects.create(**self.datos_cotizacion(), producto=self.producto, variante=self.variante)
        sin_cotizacion = VarianteProducto.objects.create(producto=self.producto, nombre='Otra')
        retirar_variantes(self.producto.variantes.all())
        cotizacion.refresh_from_db()
        self.variante.refresh_from_db()
        self.assertEqual(cotizacion.variante_id, self.variante.pk)
        self.assertFalse(self.variante.disponible)
        self.assertFalse(VarianteProducto.objects.filter(pk=sin_cotizacion.pk).exists())

    def test_telefono_nacional_no_pierde_prefijo_56(self):
        for telefono in ['561234567', '+56561234567']:
            formulario = CotizacionForm({**self.datos_cotizacion(), 'telefono': telefono})
            self.assertTrue(formulario.is_valid(), formulario.errors)
            self.assertEqual(formulario.cleaned_data['telefono'], '+56561234567')

    def test_categoria_no_puede_crear_ciclo(self):
        self.familia.padre = self.categoria
        with self.assertRaises(ValidationError):
            self.familia.full_clean()
        self.categoria.padre = self.categoria
        with self.assertRaises(ValidationError):
            self.categoria.full_clean()

    def test_imagen_admin_rechaza_variante_de_otro_producto(self):
        from .admin import ImagenProductoForm
        from .models import ImagenProducto
        otro = Producto.objects.create(nombre="Otro", slug="otro", categoria=self.categoria)
        imagen = ImagenProducto.objects.create(producto=otro, imagen="productos/prueba.png")
        form = ImagenProductoForm(data={"producto": otro.pk, "variantes": [self.variante.pk], "clave": imagen.clave, "orden": 1}, instance=imagen)
        self.assertFalse(form.is_valid())
        self.assertIn("variantes", form.errors)
