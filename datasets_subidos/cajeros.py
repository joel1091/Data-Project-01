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

# URL del archivo JSON (ajusta según corresponda)
JSON_URL = "https://valencia.opendatasoft.com/api/explore/v2.1/catalog/datasets/bancs-en-via-publica-bancos-en-via-publica/exports/json?lang=es&timezone=Europe%2FBerlin"

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
        CREATE TABLE IF NOT EXISTS public."cajeros" (
            gid INTEGER,
            modelo VARCHAR(255),
            num_banco INTEGER,
            emplazamiento VARCHAR(255),
            num_policia INTEGER,
            distrito VARCHAR(255),
            barrio VARCHAR(255),
            ano_instalacion INTEGER,
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
            gid = item.get("objectid")
            modelo = item.get("modelo")
            num_banco = item.get("numbanco")
            emplazamiento = item.get("emplazamiento")
            num_policia = item.get("numpolicia")
            distrito = item.get("distrito")
            barrio = item.get("barrio")
            ano_instalacion = item.get("anyoinstalacion")
            geo_point_2d = item.get("geo_point_2d")

            # Procesar geometrías
            point_wkt = f"POINT({geo_point_2d['lon']} {geo_point_2d['lat']})" if geo_point_2d else None

            # Insertar registro en la tabla
            cursor.execute("""
            INSERT INTO public."cajeros" 
            (gid, modelo, num_banco, emplazamiento, num_policia, distrito, barrio, ano_instalacion, geo_point_2d) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, ST_GeogFromText(%s))
            """, (gid, modelo, num_banco, emplazamiento, num_policia, distrito, barrio, ano_instalacion, point_wkt))
            print(f"Insertado registro con gid={gid}")

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
