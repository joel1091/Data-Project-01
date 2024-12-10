# **Data Project - README**

## 📋 **Descripción del Proyecto**
El objetivo de este proyecto es proporcionar una plataforma interactiva que permita a los usuarios visualizar, filtrar y consultar la disponibilidad de centros educativos, centros de mayores y centros de atención para discapacitados en la ciudad de Valencia, España. La aplicación permite visualizar los centros en un mapa interactivo, aplicar filtros personalizados y ver detalles específicos sobre cada uno de los centros.

La aplicación carga los datos desde archivos CSV remotos y los almacena en una base de datos PostgreSQL con soporte para PostGIS, permitiendo así manejar información geográfica.

## ⚙️ **Funcionalidades Principales**
- Mapa Interactivo: Visualización de centros educativos, centros de mayores y centros de discapacitados.
- Filtros Personalizados: Filtrar centros por categorías (tipo de centro, ubicación, etc.).
- Consulta de Datos: Listado de los centros filtrados en formato tabular.
- Carga de Datos: Los datos de los centros se descargan de fuentes abiertas y se almacenan en una base de datos PostgreSQL.
- Base de Datos Relacional: Gestión de los datos con PostgreSQL y PostGIS para el manejo de datos espaciales.
- Ejecución en Docker: Implementación de un entorno de contenedor para garantizar la portabilidad y la reproducibilidad del proyecto.


## 🛠️ **Requisitos Previos**
1. Docker y Docker Compose
2. PostgreSQL con extensión PostGIS habilitada
3. Sistema operativo: Windows, Linux o macOS
4. RAM: 4 GB mínimo

## 🚀 **Cómo Ejecutar el Proyecto**
1. Clonar el repositorio:
   ```bash
   git clone https://github.com/joel1091/Data-Project-01
   cd Data-Project-01

	2.	Configurar el archivo .env:

POSTGRES_USER=postgres
POSTGRES_PASSWORD=Welcome01
POSTGRES_DB=data_project


	3.	Construir la imagen de Docker:

docker-compose build


	4.	Iniciar la aplicación:

docker-compose up


	5.	Ver la aplicación:
Accede a la aplicación en tu navegador en la URL:

http://localhost:8501



📁 Archivos Clave

Archivo	Descripción
main.py	Archivo principal de la aplicación.
centros_educativos.py	Carga los centros educativos.
centros_mayores.py	Carga los centros de mayores.
discapacitados.py	Carga los centros de discapacitados.
Dockerfile	Archivo para la construcción de la imagen Docker.
docker-compose.yml	Ejecuta los contenedores de PostgreSQL y la app.
requirements.txt	Dependencias del proyecto.

🎥 Demostración en Video

🌐 Descripción de la Interfaz
	•	Página Principal:
	•	Filtros: Filtra por categoría (educativos, mayores, discapacitados).
	•	Mapa Interactivo: Muestra los centros según los filtros.
	•	Tablas de Datos: Listados de centros de acuerdo con los filtros aplicados.

🛠️ Tecnologías Usadas

Tecnología	Uso
Docker	Contenerización de la aplicación
PostgreSQL	Base de datos relacional
PostGIS	Extensión para datos espaciales
Python	Lenguaje de programación
Streamlit	Interfaz web de la aplicación
Pandas	Procesamiento de datos CSV
Geopandas	Datos geoespaciales
psycopg2	Conexión de Python con PostgreSQL

📈 Explicación de la Lógica de Carga de Datos

1. Cargar Centros Educativos
	•	Descarga los datos desde una URL CSV.
	•	Los datos se limpian y transforman.
	•	Se almacenan en la base de datos PostgreSQL.

2. Cargar Centros de Mayores
	•	Descarga los datos desde una URL CSV.
	•	Los datos se limpian y se validan.
	•	Se almacenan en PostgreSQL.

3. Cargar Centros de Discapacitados
	•	Descarga los datos desde una URL CSV.
	•	Los datos se procesan y se estructuran.
	•	Se almacenan en PostgreSQL.

🐛 Posibles Errores y Soluciones

Error	Causa	Solución
Falla la conexión a la BD	Variables de entorno mal configuradas	Verifica el archivo .env
Error en PostGIS	Falta de permisos en la base de datos	Usa CREATE EXTENSION postgis;
Error con ast en pip	ast no debe estar en requirements.txt	Elimina ast de requirements.txt.

🤝 Contribuciones

Para contribuir:
	1.	Crea una nueva rama.
	2.	Realiza tus cambios.
	3.	Crea un Pull Request.

📄 Licencia

Este proyecto está bajo la Licencia MIT.

