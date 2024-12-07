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

# URL del archivo JSON (ajusta a tu URL)
JSON_URL = "https://valencia.opendatasoft.com/api/explore/v2.1/catalog/datasets/recarrega-vehicles-electrics-recarga-vehiculos-electricos/exports/json?lang=es&timezone=Europe%2FBerlin"

def main():
    try:
        # Conexión a PostgreSQL
        conn = psycopg2.connect(**POSTGRES_CONFIG)
        conn.autocommit = True
        cursor = conn.cursor()

        # Verificar si PostGIS está habilitado
        cursor.execute("SELECT PostGIS_Version();")
        if not cursor.fetchone():
            print("Error: PostGIS no está habilitado en esta base de datos.")
            return

        # Crear la tabla si no existe
        create_table_query = """
        CREATE TABLE IF NOT EXISTS public."recarga_coches" (
            objectid INTEGER,
            proyecto VARCHAR(255),
            localizacion VARCHAR(255),
            estado VARCHAR(255),
            geo_shape GEOMETRY,
            geo_point_2d GEOGRAPHY
        );
        """
        cursor.execute(create_table_query)
        print("Tabla creada exitosamente o ya existe.")

        # Descargar los datos desde la URL
        print("Descargando datos desde la URL...")
        response = requests.get(JSON_URL)
        if response.status_code != 200:
            print(f"Error al descargar los datos: {response.status_code}")
            return
        data = response.json()
        print("Datos descargados correctamente.")

        # Iterar sobre los elementos del JSON e insertar en la tabla
        for item in data:
            # Extraer campos principales
            objectid = item.get("objectid")
            proyecto = item.get("proyecto")
            localizacion = item.get("localizacion")
            estado = item.get("estado")
            geo_shape = item.get("geo_shape", {}).get("geometry", None)
            geo_point_2d = item.get("geo_point_2d", None)

            # Convertir geo_point_2d a formato WKT
            point_wkt = None
            if geo_point_2d:
                lon = geo_point_2d.get("lon")
                lat = geo_point_2d.get("lat")
                if lon is not None and lat is not None:
                    point_wkt = f"POINT({lon} {lat})"

            # Convertir geo_shape a GeoJSON
            geojson_str = json.dumps(geo_shape) if geo_shape else None

            # Insertar registro en la tabla
            insert_query = """
            INSERT INTO public."recarga_coches" 
            (objectid, proyecto, localizacion, estado, geo_shape, geo_point_2d) 
            VALUES (%s, %s, %s, %s, ST_GeomFromGeoJSON(%s), ST_GeogFromText(%s))
            """
            cursor.execute(insert_query, (objectid, proyecto, localizacion, estado, geojson_str, point_wkt))
            print(f"Insertado registro con objectid={objectid}")

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
