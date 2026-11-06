# PH Servicios Electrónicos

## Preparar una copia local en Windows con XAMPP

1. Instala Git, Python 3.14 y XAMPP. En XAMPP inicia **MySQL**.
2. Clona la rama principal actual:

   ```powershell
   git clone https://github.com/crispobletep/proyecto-web.git
   cd proyecto-web
   git switch main
   git pull origin main
   ```

3. Crea el entorno e instala las dependencias:

   ```powershell
   py -3.14 -m venv .venv
   .\.venv\Scripts\Activate.ps1
   python -m pip install -r requirements-python314.txt
   ```

4. En phpMyAdmin crea la base `sh_servicios_electronicos` con cotejamiento
   `utf8mb4` e importa el archivo SQL que te compartió el administrador del
   proyecto.
5. Crea `.env` en la carpeta del proyecto con la conexión local. Ajusta el
   usuario, la contraseña y el puerto según tu XAMPP:

   ```dotenv
   DJANGO_DEBUG=1
   MYSQL_DATABASE=sh_servicios_electronicos
   MYSQL_USER=root
   MYSQL_PASSWORD=
   MYSQL_HOST=127.0.0.1
   MYSQL_PORT=3306
   ```

   No compartas el `.env`: contiene configuración privada. El `.env` está
   excluido de Git.

6. Aplica las migraciones pendientes e inicia el sitio:

   ```powershell
   python manage.py migrate
   python manage.py runserver
   ```

   Abre <http://127.0.0.1:8000/>.

## Imágenes del catálogo

El SQL guarda las rutas de las imágenes, no los archivos. Las imágenes están en
`media/` y se descargan junto con el repositorio de GitHub. No hace falta
importar una carpeta de imágenes aparte si se clonó `main` completa.

En desarrollo, `DJANGO_DEBUG=1` hace que Django sirva los archivos de `media/`.
Si una imagen no aparece, confirma que el archivo exista en el clon y abre su
ruta directamente; por ejemplo:

<http://127.0.0.1:8000/media/productos/catalogo/iluminacion/nuevos/estanco-1x18w.png>

Si se usa un servidor de producción con `DJANGO_DEBUG=0`, hay que configurar el
servidor web para servir `/media/` desde la carpeta `media/`; `runserver` y
Django no publican esos archivos en modo de producción.

La base debe ser la que corresponde al mismo proyecto y rama. Después de
importar un SQL antiguo, `python manage.py migrate` aplica las migraciones de
catálogo incluidas en la versión actual del repositorio.
