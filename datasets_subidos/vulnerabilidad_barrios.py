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
JSON_URL = "https://valencia.opendatasoft.com/api/explore/v2.1/catalog/datasets/vulnerabilidad-por-barrios/records?select=*&limit=70"  # Sustituye con la URL correcta.

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
        CREATE TABLE IF NOT EXISTS public."vulnerabilidad_barrios" (
            objectid INTEGER,
            nombre VARCHAR(255),
            codbar INTEGER,
            distrito VARCHAR(255),
            vul_equip NUMERIC,
            vul_equip_txt VARCHAR(255),
            ind_dem NUMERIC,
            ind_dem_txt VARCHAR(255),
            ind_econom NUMERIC,
            ind_econom_txt VARCHAR(255),
            ind_global NUMERIC,
            ind_global_txt VARCHAR(255),
            shape_leng NUMERIC,
            shape_area NUMERIC,
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
        
        # Comprobar el formato del JSON
        data = response.json()  # Decodifica la respuesta JSON

        # Extraer la lista de elementos desde "results"
        if "results" not in data:
            print("Error: La clave 'results' no está en el JSON.")
            return
        elementos = data["results"]

        print(f"Número de elementos encontrados: {len(elementos)}")

        # Insertar datos en la tabla
        for item in elementos:
            # Extraer campos del JSON
            objectid = item.get("objectid")
            nombre = item.get("nombre")
            codbar = item.get("codbar")
            distrito = item.get("distrito")
            vul_equip = item.get("ind_equip")
            vul_equip_txt = item.get("vul_equip")
            ind_dem = item.get("ind_dem")
            ind_dem_txt = item.get("vul_dem")
            ind_econom = item.get("ind_econom")
            ind_econom_txt = item.get("vul_econom")
            ind_global = item.get("ind_global")
            ind_global_txt = item.get("vul_global")
            shape_leng = item.get("shape_leng")
            shape_area = item.get("shape_area")
            geo_shape = item.get("geo_shape", {}).get("geometry")
            geo_point_2d = item.get("geo_point_2d")

            # Procesar geometrías
            geojson_str = json.dumps(geo_shape) if geo_shape else None
            point_wkt = f"POINT({geo_point_2d['lon']} {geo_point_2d['lat']})" if geo_point_2d else None

            # Insertar registro en la tabla
            cursor.execute("""
            INSERT INTO public."vulnerabilidad_barrios" 
            (objectid, nombre, codbar, distrito, vul_equip, vul_equip_txt, ind_dem, ind_dem_txt, 
             ind_econom, ind_econom_txt, ind_global, ind_global_txt, shape_leng, shape_area, geo_shape, geo_point_2d) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, ST_GeomFromGeoJSON(%s), ST_GeogFromText(%s))
            """, (objectid, nombre, codbar, distrito, vul_equip, vul_equip_txt, ind_dem, ind_dem_txt,
                  ind_econom, ind_econom_txt, ind_global, ind_global_txt, shape_leng, shape_area, geojson_str, point_wkt))
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
