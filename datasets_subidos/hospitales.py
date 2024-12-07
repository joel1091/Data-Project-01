import psycopg2
import requests
import json

# Configuración de la conexión a PostgreSQL
POSTGRES_CONFIG = {
    "host": "postgres",
    "port": 5432,
    "database": "data_project",
    "user": "postgres",
    "password": "Welcome01"
}

# URL del archivo JSON
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
            nombre VARCHAR(255),
            financiaci VARCHAR(255),
            tipo VARCHAR(255),
            camas INTEGER,
            direccion VARCHAR(255),
            fecha DATE,
            barrio VARCHAR(255),
            codbarrio INTEGER,
            coddistbar INTEGER,
            coddistrit INTEGER,
            x NUMERIC,
            y NUMERIC
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
            nombre = item.get("nombre")
            financiaci = item.get("financiaci")
            tipo = item.get("tipo")
            camas = item.get("camas")
            direccion = item.get("direccion")
            fecha = item.get("fecha")
            barrio = item.get("barrio")
            codbarrio = item.get("codbarrio")
            coddistbar = item.get("coddistbar")
            coddistrit = item.get("coddistrit")
            x = item.get("x")
            y = item.get("y")

            # Procesar geometrías
            geojson_str = json.dumps(geo_shape) if geo_shape else None
            point_wkt = None
            if geo_point_2d:
                lon = geo_point_2d.get("lon")
                lat = geo_point_2d.get("lat")
                if lon is not None and lat is not None:
                    point_wkt = f"POINT({lon} {lat})"

            # Insertar registro en la tabla
            try:
                cursor.execute("""
                INSERT INTO public."hospitales" 
                (geo_point_2d, geo_shape, nombre, financiaci, tipo, camas, direccion, fecha, 
                 barrio, codbarrio, coddistbar, coddistrit, x, y) 
                VALUES (ST_GeogFromText(%s), ST_GeomFromGeoJSON(%s), %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (point_wkt, geojson_str, nombre, financiaci, tipo, camas, direccion, fecha, 
                      barrio, codbarrio, coddistbar, coddistrit, x, y))
                print(f"Insertado registro con nombre={nombre}")
            except Exception as e:
                print(f"Error al insertar registro con nombre={nombre}: {e}")

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
