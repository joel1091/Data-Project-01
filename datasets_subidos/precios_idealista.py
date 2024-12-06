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
JSON_URL = "https://valencia.opendatasoft.com/api/explore/v2.1/catalog/datasets/precio-de-compra-en-idealista/records?select=*&limit=88"

def main():
    try:
        # Conexión a PostgreSQL
        print("Conectando a la base de datos...")
        conn = psycopg2.connect(**POSTGRES_CONFIG)
        conn.autocommit = True
        cursor = conn.cursor()
        print("Conexión establecida.")

        # Verificar si PostGIS está habilitado
        cursor.execute("SELECT PostGIS_Version();")
        if not cursor.fetchone():
            print("Error: PostGIS no está habilitado.")
            return

        # Crear la tabla si no existe
        print("Creando tabla idealista...")
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS public."idealista" (
            objectid INTEGER,
            geo_point_2d GEOGRAPHY,
            geo_shape GEOMETRY,
            coddistbar INTEGER,
            barrio VARCHAR(255),
            codbarrio INTEGER,
            coddistrit INTEGER,
            distrito VARCHAR(255),
            precio_2022_euros_m2 NUMERIC,
            precio_2010_euros_m2 NUMERIC,
            max_historico_euros_m2 NUMERIC,
            ano_max_hist INTEGER,
            fecha_creacion DATE
        );
        """)
        print("Tabla idealista creada exitosamente o ya existe.")

        # Descargar los datos desde la URL
        print("Descargando datos desde la URL...")
        response = requests.get(JSON_URL)
        if response.status_code != 200:
            print(f"Error al descargar los datos: {response.status_code}")
            return
        
        data = response.json()
        if not isinstance(data, dict) or "records" not in data:
            print(f"Estructura del JSON no esperada: {data.keys() if isinstance(data, dict) else type(data)}")
            return
        
        registros = data["records"]
        print(f"Datos descargados correctamente. Número de registros: {len(registros)}")

        # Insertar datos en la tabla
        for item in registros:
            fields = item.get("fields", {})
            if not fields:
                print(f"Advertencia: Registro sin campos válidos: {item}")
                continue

            # Extracción segura de los campos
            objectid = fields.get("_id")
            geo_point_2d = fields.get("geo_point_2d")
            geo_shape = fields.get("geo_shape", {}).get("geometry", None)
            coddistbar = fields.get("coddistbar")
            barrio = fields.get("barrio")
            codbarrio = fields.get("codbarrio")
            coddistrit = fields.get("coddistrit")
            distrito = fields.get("distrito")
            precio_2022_euros_m2 = fields.get("precio_2022_euros_m2")
            precio_2010_euros_m2 = fields.get("precio_2010_euros_m2")
            max_historico_euros_m2 = fields.get("max_historico_euros_m2")
            ano_max_hist = fields.get("ano_max_hist")
            fecha_creacion = fields.get("fecha_creacion")

            # Validación de geometrías
            point_wkt = None
            if geo_point_2d and isinstance(geo_point_2d, list) and len(geo_point_2d) == 2:
                lon, lat = geo_point_2d
                point_wkt = f"POINT({lon} {lat})"
            geojson_str = json.dumps(geo_shape) if geo_shape else None

            # Depuración: Imprimir datos a insertar
            print(f"Procesando registro: objectid={objectid}, barrio={barrio}, distrito={distrito}")

            # Intentar la inserción en la base de datos
            try:
                cursor.execute("""
                INSERT INTO public."idealista" 
                (objectid, geo_point_2d, geo_shape, coddistbar, barrio, codbarrio, coddistrit, distrito, 
                 precio_2022_euros_m2, precio_2010_euros_m2, max_historico_euros_m2, ano_max_hist, fecha_creacion) 
                VALUES (ST_GeogFromText(%s), ST_GeomFromGeoJSON(%s), %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (point_wkt, geojson_str, coddistbar, barrio, codbarrio, coddistrit, distrito,
                      precio_2022_euros_m2, precio_2010_euros_m2, max_historico_euros_m2, ano_max_hist, fecha_creacion))
                print(f"Insertado registro con barrio={barrio}, distrito={distrito}")
            except Exception as e:
                print(f"Error al insertar registro con objectid={objectid}: {e}")

        print("Todos los datos fueron procesados correctamente.")

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
