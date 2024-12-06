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
JSON_URL = "https://valencia.opendatasoft.com/api/explore/v2.1/catalog/datasets/discapacitat-discapacidad/exports/json?lang=es&timezone=Europe%2FBerlin"


# Función para manejar conversiones seguras a entero
def safe_int(value):
    try:
        return int(value)
    except (ValueError, TypeError):
        return None  # Devuelve NULL si no es un entero válido

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
        CREATE TABLE IF NOT EXISTS public."discapacitat-discapacidad" (
            objectid INTEGER,
            equipamient VARCHAR(255),
            x INTEGER,
            y INTEGER,
            identifica INTEGER,
            codvia INTEGER,
            numportal INTEGER,
            telefono INTEGER,
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
            objectid = safe_int(item.get("objectid"))
            equipamient = item.get("equipamien")
            x = safe_int(item.get("x"))
            y = safe_int(item.get("y"))
            identifica = safe_int(item.get("identifica"))
            codvia = safe_int(item.get("codvia"))

            # Manejo de numportal
            numportal_raw = item.get("numportal")
            if numportal_raw == "S/N":
                numportal = None
            else:
                numportal = safe_int(numportal_raw)

            telefono = safe_int(item.get("telefono"))
            geo_shape = item.get("geo_shape", {}).get("geometry")
            geo_point_2d = item.get("geo_point_2d")

            # Convertir geometrías a formato adecuado
            geojson_str = json.dumps(geo_shape) if geo_shape else None
            point_wkt = f"POINT({geo_point_2d['lon']} {geo_point_2d['lat']})" if geo_point_2d else None

            # Insertar registro en la tabla
            cursor.execute("""
            INSERT INTO public."discapacitat-discapacidad" 
            (objectid, equipamient, x, y, identifica, codvia, numportal, telefono, geo_shape, geo_point_2d) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, ST_GeomFromGeoJSON(%s), ST_GeogFromText(%s))
            """, (objectid, equipamient, x, y, identifica, codvia, numportal, telefono, geojson_str, point_wkt))
            print(f"Insertado registro con objectid={objectid}, equipamient={equipamient}")

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
