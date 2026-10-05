# Revisión del proyecto

## Alcance y comprobaciones
- Revisión de lógica de vistas, formularios, modelos, administrador, importadores, navegación y selección de variantes; comprobación de rutas, configuración, plantillas y migraciones.
- Sintaxis comprobada en 48 archivos Python propios. No incluye dependencias de venv ni auditoría de vulnerabilidades de paquetes.
- 30 pruebas automatizadas aprobadas, incluidas 8 regresiones nuevas.
- Seis páginas principales comprobadas a 1440 y 390 píxeles, sin errores de JavaScript ni desbordamiento horizontal en esos recorridos.
- Selección de variantes, imagen principal, desplazamiento y teclado verificados en ambos tamaños.
- Modelos y migraciones sincronizados; pip check sin dependencias incompatibles declaradas.
- 546 referencias de archivos revisadas, sin archivos faltantes. Sin relaciones incoherentes de cotizaciones ni imágenes con variantes ajenas en los datos actuales.

## Correcciones aplicadas
1. IDs recibidos por GET y POST: rechazar caracteres numéricos no convertibles y valores fuera del rango de BigAutoField antes de consultar la base de datos.
2. POST vacío de contacto: vincular el formulario para mostrar los errores obligatorios.
3. No precargar productos de categorías o familias ocultas en cotizaciones.
4. Cotización: inferir el producto desde la variante antes de comprobar la incompatibilidad con un proyecto.
5. Teléfono: no confundir un número nacional de nueve dígitos que empieza por 56 con un número internacional. Escapar correctamente el patrón HTML para navegadores actuales.
6. Carrusel: impedir el foco en diapositivas ocultas y respetar la pausa mientras el cursor o el foco permanezcan dentro.
7. Cuatro importadores: conservar las variantes referenciadas por cotizaciones al retirarlas del catálogo; marcarlas no disponibles en vez de borrar su referencia o provocar ProtectedError.
8. Administrador: impedir ciclos y niveles adicionales en categorías, y rechazar variantes de otro producto al registrar una imagen.

## Límites y puntos pendientes
- check --deploy devuelve seis advertencias en la configuración local: DEBUG, fortaleza de SECRET_KEY, HTTPS, HSTS y cookies de sesión/CSRF seguras. Deben resolverse según el servidor definitivo; no se activaron redirecciones HTTPS sobre localhost.
- El correo se verifica con un backend de pruebas. No se enviaron mensajes reales ni se comprobó la entrega SMTP.
- No se verificó la disponibilidad permanente de imágenes o mapas externos.
- La revisión no certifica ausencia absoluta de errores, rendimiento bajo carga ni seguridad del despliegue.
- Las marcas desconocidas y las imágenes con marcas distintas dentro de una ficha siguen requiriendo validación comercial; esta revisión técnica no asigna fabricantes por inferencia.
