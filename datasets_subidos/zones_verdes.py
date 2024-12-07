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
JSON_URL = "https://valencia.opendatasoft.com/api/explore/v2.1/catalog/datasets/espais-verds-espacios-verdes/exports/json?lang=es&timezone=Europe%2FBerlin"

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
        CREATE TABLE IF NOT EXISTS public."zones_verdes" (
            objectid INTEGER,
            "Id Jardí / Id. Jardín" INTEGER,
            "Nom / Nombre" VARCHAR(255),
            "Barri / Barrio" VARCHAR(255),
            "Tipologia / Tipología" VARCHAR(255),
            "Àrea / Área" INTEGER,
            "Número Elementos Fitness" INTEGER,
            "Superficie Huerto Urbano" INTEGER,
            "Zona" VARCHAR(55),
            "DM" VARCHAR(255),
            "Ud. Gestion" VARCHAR(255),
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
            # Extraer campos principales
            objectid = item.get("objectid")
            id_jardin = item.get("id_jardin")
            nombre = item.get("nombre")
            barrio = item.get("barrio")
            tipologia = item.get("tipologia")
            area = item.get("st_area_shape")
            n_elementos_fitness = item.get("n_elementos_fitness")
            sup_huerto_urbano = item.get("sup_huerto_urbano")
            zona = item.get("zona")
            dm = item.get("dm")
            ud_gestion = item.get("ud_gestion")
            geo_shape = item.get("geo_shape", {}).get("geometry")
            geo_point_2d = item.get("geo_point_2d")

            # Convertir geometrías a formato adecuado
            geojson_str = json.dumps(geo_shape) if geo_shape else None
            point_wkt = f"POINT({geo_point_2d['lon']} {geo_point_2d['lat']})" if geo_point_2d else None

            # Insertar registro en la tabla
            cursor.execute("""
            INSERT INTO public."zones_verdes" 
            (objectid, "Id Jardí / Id. Jardín", "Nom / Nombre", "Barri / Barrio", 
            "Tipologia / Tipología", "Àrea / Área", "Número Elementos Fitness", 
            "Superficie Huerto Urbano", "Zona", "DM", "Ud. Gestion", geo_shape, geo_point_2d) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, ST_GeomFromGeoJSON(%s), ST_GeogFromText(%s))
            """, (objectid, id_jardin, nombre, barrio, tipologia, area, n_elementos_fitness, 
                  sup_huerto_urbano, zona, dm, ud_gestion, geojson_str, point_wkt))
            print(f"Insertado registro con objectid={objectid}, nombre={nombre}")

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
