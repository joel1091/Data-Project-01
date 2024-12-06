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

# URL del archivo JSON
JSON_URL = "https://valencia.opendatasoft.com/api/explore/v2.1/catalog/datasets/zones-jocs-infantils-zona-juegos-infantiles/exports/json?lang=es&timezone=Europe%2FBerlin"  # Sustituye por la URL correcta.

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
        CREATE TABLE IF NOT EXISTS public."parques" (
            objectid INTEGER,
            codigo BIGINT,
            jardin VARCHAR(255),
            barrio VARCHAR(255),
            dm INTEGER,
            zona VARCHAR(50),
            mantenimiento VARCHAR(255),
            tipo VARCHAR(255),
            geo_shape GEOMETRY,
            geo_point_2d GEOGRAPHY
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
            # Extraer campos del JSON
            objectid = item.get("objectid")
            codigo = item.get("codigo")
            jardin = item.get("jardin")
            barrio = item.get("barrio")
            dm = item.get("dm")
            zona = item.get("zona")
            mantenimiento = item.get("mantenimiento")
            tipo = item.get("tipo")
            geo_shape = item.get("geo_shape", {}).get("geometry")
            geo_point_2d = item.get("geo_point_2d")

            # Procesar geometrías
            geojson_str = json.dumps(geo_shape) if geo_shape else None
            point_wkt = f"POINT({geo_point_2d['lon']} {geo_point_2d['lat']})" if geo_point_2d else None

            # Insertar registro en la tabla
            cursor.execute("""
            INSERT INTO public."parques"
            (objectid, codigo, jardin, barrio, dm, zona, mantenimiento, tipo, geo_shape, geo_point_2d) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, ST_GeomFromGeoJSON(%s), ST_GeogFromText(%s))
            """, (objectid, codigo, jardin, barrio, dm, zona, mantenimiento, tipo, geojson_str, point_wkt))
            print(f"Insertado registro con objectid={objectid}, jardin={jardin}")

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
