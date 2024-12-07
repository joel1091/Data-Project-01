import psycopg2
import requests
import json
from datetime import datetime

# Configuración de la conexión a PostgreSQL
POSTGRES_CONFIG = {
    "host": "postgres",
    "port": 5432,
    "database": "data_project",
    "user": "postgres",
    "password": "Welcome01"
}

# URL del archivo JSON
JSON_URL = "https://valencia.opendatasoft.com/api/explore/v2.1/catalog/datasets/valenbisi-disponibilitat-valenbisi-dsiponibilidad/exports/json?lang=es&timezone=Europe%2FBerlin"

def to_boolean(value):
    """Convierte 'T' a True y 'F' a False."""
    return True if value == 'T' else False if value == 'F' else None

def to_timestamp(value):
    """Convierte una cadena de fecha y hora en un objeto TIMESTAMP para PostgreSQL."""
    try:
        return datetime.strptime(value, '%d/%m/%Y %H:%M:%S') if value else None
    except ValueError:
        return None

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
        CREATE TABLE IF NOT EXISTS public."valenbisi" (
            direccion VARCHAR(255),
            numero INTEGER,
            activo BOOLEAN,
            bicis_disponibles INTEGER,
            espacios_libres INTEGER,
            espacios_totales INTEGER,
            ticket BOOLEAN,
            fecha_actualizacion TIMESTAMP,
            geo_shape GEOMETRY,
            geo_point_2d GEOGRAPHY,
            update_jcd TIMESTAMP
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
            direccion = item.get("address")
            numero = item.get("number")
            activo = to_boolean(item.get("open"))
            bicis_disponibles = item.get("available")
            espacios_libres = item.get("free")
            espacios_totales = item.get("total")
            ticket = to_boolean(item.get("ticket"))
            fecha_actualizacion = to_timestamp(item.get("updated_at"))
            update_jcd = to_timestamp(item.get("update_jcd"))
            geo_shape = item.get("geo_shape", {}).get("geometry")
            geo_point_2d = item.get("geo_point_2d")

            # Convertir geometrías a formato adecuado
            geojson_str = json.dumps(geo_shape) if geo_shape else None
            point_wkt = f"POINT({geo_point_2d['lon']} {geo_point_2d['lat']})" if geo_point_2d else None

            # Insertar registro en la tabla
            cursor.execute("""
            INSERT INTO public."valenbisi" 
            (direccion, numero, activo, bicis_disponibles, espacios_libres, espacios_totales, 
            ticket, fecha_actualizacion, geo_shape, geo_point_2d, update_jcd) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, ST_GeomFromGeoJSON(%s), ST_GeogFromText(%s), %s)
            """, (direccion, numero, activo, bicis_disponibles, espacios_libres, espacios_totales, 
                  ticket, fecha_actualizacion, geojson_str, point_wkt, update_jcd))
            print(f"Insertado registro con dirección={direccion}")

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
