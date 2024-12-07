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
JSON_URL = "https://valencia.opendatasoft.com/api/explore/v2.1/catalog/datasets/emt/exports/json?lang=es&timezone=Europe%2FBerlin"

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
        CREATE TABLE IF NOT EXISTS public.emt (
            "Id Parada" INTEGER,
            "Cod Via" VARCHAR(255),
            "Num Portal" VARCHAR(255),
            "Suprimida" INTEGER,
            "Denominació / Denominación" VARCHAR(255),
            "Línies / Líneas" VARCHAR(255),
            "Pròximes Arribades / Proximas Llegadas" VARCHAR(255),
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
            id_parada = item.get("id_parada")
            cod_via = item.get("codvia")
            num_portal = item.get("numportal")
            suprimida = item.get("suprimida")
            denominacion = item.get("denominacion")
            lineas = item.get("lineas")
            proximas_llegadas = item.get("proximas_llegadas")
            geo_shape = item.get("geo_shape", {}).get("geometry")
            geo_point_2d = item.get("geo_point_2d")

            # Convertir geometrías a formato adecuado
            geojson_str = json.dumps(geo_shape) if geo_shape else None
            point_wkt = f"POINT({geo_point_2d['lon']} {geo_point_2d['lat']})" if geo_point_2d else None

            # Insertar registro en la tabla
            cursor.execute("""
            INSERT INTO public.emt 
            ("Id Parada", "Cod Via", "Num Portal", "Suprimida", "Denominació / Denominación", 
             "Línies / Líneas", "Pròximes Arribades / Proximas Llegadas", geo_shape, geo_point_2d) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, ST_GeomFromGeoJSON(%s), ST_GeogFromText(%s))
            """, (id_parada, cod_via, num_portal, suprimida, denominacion, lineas, proximas_llegadas, geojson_str, point_wkt))
            print(f"Insertado registro con Id Parada={id_parada}, Denominación={denominacion}")

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
