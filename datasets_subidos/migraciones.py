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
JSON_URL = "https://valencia.opendatasoft.com/api/explore/v2.1/catalog/datasets/migrants-migrantes/exports/json?lang=es&timezone=Europe%2FBerlin"  # Sustituye con la URL correcta.

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
        CREATE TABLE IF NOT EXISTS public."migraciones" (
            objectid INTEGER,
            equipamient VARCHAR(255),
            x NUMERIC,
            y NUMERIC,
            identifca VARCHAR(50),
            codvia INTEGER,
            numportal VARCHAR(50),
            telefono VARCHAR(20),
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
            if item is None:
                print("Advertencia: Elemento vacío en los datos, omitiendo.")
                continue
            
            # Extraer y validar campos del JSON
            objectid = item.get("objectid")
            equipamient = item.get("equipamien")
            x = item.get("x")
            y = item.get("y")
            identifca = item.get("identifica")
            codvia = item.get("codvia")
            numportal = item.get("numportal")
            telefono = item.get("telefono")
            geo_shape = item.get("geo_shape", {}).get("geometry") if item.get("geo_shape") else None
            geo_point_2d = item.get("geo_point_2d") if item.get("geo_point_2d") else None

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
                INSERT INTO public."migraciones" 
                (objectid, equipamient, x, y, identifca, codvia, numportal, telefono, geo_shape, geo_point_2d) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, ST_GeomFromGeoJSON(%s), ST_GeogFromText(%s))
                """, (objectid, equipamient, x, y, identifca, codvia, numportal, telefono, geojson_str, point_wkt))
                print(f"Insertado registro con objectid={objectid}, equipamiento={equipamient}")
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
