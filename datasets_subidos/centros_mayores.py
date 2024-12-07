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
JSON_URL = "https://valencia.opendatasoft.com/api/explore/v2.1/catalog/datasets/majors-mayores/exports/json?lang=es&timezone=Europe%2FBerlin"

def safe_int(value):
    """Convierte valores a entero o devuelve None si no es posible."""
    try:
        return int(value)
    except (ValueError, TypeError):
        return None

def safe_get(dictionary, key, default=None):
    """Obtiene un valor de un diccionario de forma segura."""
    return dictionary.get(key, default) if dictionary else default

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
        CREATE TABLE IF NOT EXISTS public."centros_mayores" (
            objectid INTEGER,
            equipamien VARCHAR(255),
            x NUMERIC,
            y NUMERIC,
            identifica VARCHAR(50),
            codvia INTEGER,
            numportal VARCHAR(50),
            telefono VARCHAR(20),
            gid INTEGER,
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
            if not isinstance(item, dict):
                print(f"Advertencia: Elemento no válido, se omite: {item}")
                continue

            # Extraer valores del JSON de manera segura
            objectid = safe_int(safe_get(item, "objectid"))
            equipamien = safe_get(item, "equipamien", "Sin nombre")
            x = safe_int(safe_get(item, "x"))
            y = safe_int(safe_get(item, "y"))
            identifica = safe_get(item, "identifica", "Sin identificar")
            codvia = safe_int(safe_get(item, "codvia"))
            numportal = safe_get(item, "numportal", "Desconocido")
            telefono = safe_get(item, "telefono", "No especificado")
            gid = safe_int(safe_get(item, "gid"))
            geo_shape = safe_get(item.get("geo_shape", {}), "geometry")
            geo_point_2d = safe_get(item, "geo_point_2d")

            # Validar geometrías
            geojson_str = json.dumps(geo_shape) if geo_shape else None
            point_wkt = None
            if geo_point_2d:
                lon = safe_get(geo_point_2d, "lon")
                lat = safe_get(geo_point_2d, "lat")
                if lon is not None and lat is not None:
                    point_wkt = f"POINT({lon} {lat})"

            # Insertar registro en la tabla
            try:
                cursor.execute("""
                INSERT INTO public."centros_mayores" 
                (objectid, equipamien, x, y, identifica, codvia, numportal, telefono, gid, geo_shape, geo_point_2d) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, ST_GeomFromGeoJSON(%s), ST_GeogFromText(%s))
                """, (objectid, equipamien, x, y, identifica, codvia, numportal, telefono, gid, geojson_str, point_wkt))
                print(f"Insertado registro con objectid={objectid}, equipamien={equipamien}")
            except Exception as e:
                print(f"Error al insertar registro con objectid={objectid}: {e}")

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
