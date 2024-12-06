import psycopg2
import requests
import json

# Configuración de la conexión a PostgreSQL
POSTGRES_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "database": "data_project",
    "user": "postgres",
    "password": "Welcome01"
}

# URL del archivo JSON (ajusta según corresponda)
JSON_URL = "https://valencia.opendatasoft.com/api/explore/v2.1/catalog/datasets/hospitales/exports/json?lang=es&timezone=Europe%2FMadrid"

def main():
    try:
        # Conexión a PostgreSQL
        conn = psycopg2.connect(**POSTGRES_CONFIG)
        conn.autocommit = True
        cursor = conn.cursor()

        # Verificar si PostGIS está habilitado
        cursor.execute("SELECT PostGIS_Version();")
        if not cursor.fetchone():
            print("Error: PostGIS no está habilitado.")
            return

        # Crear la tabla si no existe
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS public."hospitales" (
            geo_point_2d GEOGRAPHY,
            geo_shape GEOMETRY,
            Nombre VARCHAR(255),
            Financiaci VARCHAR(255),
            Tipo VARCHAR(255),
            Camas INTEGER,
            Direccion VARCHAR(255),
            Fecha DATE,
            Barrio VARCHAR(255),
            codbarrio INTEGER,
            coddistbar INTEGER,
            coddistrit INTEGER,
            X INTEGER,
            Y INTEGER
        );
        """)
        print("Tabla creada exitosamente o ya existe.")

        # Descargar los datos desde la URL
        print("Descargando datos desde la URL...")
        response = requests.get(JSON_URL)
        if response.status_code != 200:
            print(f"Error al descargar los datos: {response.status_code}")
            return
        data = response.json()
        print("Datos descargados correctamente.")

        # Insertar datos en la tabla
        for item in data:
            # Extraer campos principales
            geo_point_2d = item.get("geo_point_2d", None)
            geo_shape = item.get("geo_shape", {}).get("geometry", None)
            nombre = item.get("Nombre")
            financiaci = item.get("Financiaci")
            tipo = item.get("Tipo")
            camas = item.get("Camas")
            direccion = item.get("Direccion")
            fecha = item.get("Fecha")
            barrio = item.get("Barrio")
            codbarrio = item.get("codbarrio")
            coddistbar = item.get("coddistbar")
            coddistrit = item.get("coddistrit")
            x = item.get("X")
            y = item.get("Y")

            # Procesar geometrías
            geojson_str = json.dumps(geo_shape) if geo_shape else None
            point_wkt = f"POINT({geo_point_2d['lon']} {geo_point_2d['lat']})" if geo_point_2d else None

            # Insertar registro en la tabla
            cursor.execute("""
            INSERT INTO public."hospitales" 
            (geo_point_2d, geo_shape, Nombre, Financiaci, Tipo, Camas, Direccion, Fecha, 
            Barrio, codbarrio, coddistbar, coddistrit, X, Y) 
            VALUES (ST_GeogFromText(%s), ST_GeomFromGeoJSON(%s), %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (point_wkt, geojson_str, nombre, financiaci, tipo, camas, direccion, fecha, 
                  barrio, codbarrio, coddistbar, coddistrit, x, y))
            print(f"Insertado registro con nombre={nombre}")

        print("Todos los datos fueron insertados correctamente.")

    except Exception as e:
        print(f"Error inesperado: {e}")
    finally:
        # Cerrar cursor y conexión
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()
        print("Conexión cerrada.")

# Ejecutar el script
if __name__ == "__main__":
    main()
