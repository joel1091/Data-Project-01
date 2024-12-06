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

# URL del archivo JSON (ajusta a tu URL)
JSON_URL = "https://valencia.opendatasoft.com/api/explore/v2.1/catalog/datasets/precio-de-compra-en-idealista/records?select=*&limit=88"

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
        CREATE TABLE IF NOT EXISTS public."idealista" (
            "Geo Point" GEOMETRY,
            "Geo Shape" GEOGRAPHY,
            "coddistbar" INTEGER,
            "BARRIO" VARCHAR(255),
            "codbarrio" INTEGER,
            "coddistrit" INTEGER,
            "DISTRITO" VARCHAR(255),
            "Precio_2022 (Euros/m2)" INTEGER,
            "Precio_2010 (Euros/m2)" INTEGER,
            "Max_historico (Euros/m2)" INTEGER,
            "Año_Max_Hist" INTEGER,
            "Fecha_creacion" DATE
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
            geo_point_2d = item.get("geo_point_2d", None)
            geo_shape = item.get("geo_shape", {}).get("geometry", None)
            coddistbar = item.get("coddistbar")
            barrio = item.get("barrio")
            codbarrio = item.get("codbarrio")
            coddistrit = item.get("coddistrit")
            distrito = item.get("distrito")
            precio_2022 = item.get("precio_2022_euros_m2")
            precio_2010 = item.get("precio_2010_euros_m2")
            max_historico = item.get("max_historico_euros_m2")
            ano_max_hist = item.get("ano_max_hist")
            fecha_creacion = item.get("fecha_creacion")

            # Procesar geometrías
            geojson_str = json.dumps(geo_shape) if geo_shape else None
            point_wkt = f"POINT({geo_point_2d['lon']} {geo_point_2d['lat']})" if geo_point_2d else None

            # Insertar registro
            cursor.execute("""
            INSERT INTO public."idealista" 
            ("Geo Point", "Geo Shape", coddistbar, "BARRIO", codbarrio, coddistrit, "DISTRITO", 
             "Precio_2022 (Euros/m2)", "Precio_2010 (Euros/m2)", "Max_historico (Euros/m2)", 
             "Año_Max_Hist", "Fecha_creacion") 
            VALUES (ST_GeogFromText(%s), ST_GeomFromGeoJSON(%s), %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (point_wkt, geojson_str, coddistbar, barrio, codbarrio, coddistrit, distrito,
                  precio_2022, precio_2010, max_historico, ano_max_hist, fecha_creacion))
            print(f"Insertado registro con coddistbar={coddistbar}, barrio={barrio}")

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
