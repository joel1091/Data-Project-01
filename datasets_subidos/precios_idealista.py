import psycopg2
import pandas as pd

# Configuración de la conexión a PostgreSQL
POSTGRES_CONFIG = {
    "host": "postgres",
    "port": 5432,
    "database": "data_project",
    "user": "postgres",
    "password": "Welcome01"
}

# URL del archivo CSV
CSV_URL = "https://valencia.opendatasoft.com/api/explore/v2.1/catalog/datasets/precio-de-compra-en-idealista/exports/csv?lang=es&timezone=Europe%2FBerlin&use_labels=true&delimiter=%3B"

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
            objectid SERIAL PRIMARY KEY,
            geo_point_2d GEOGRAPHY(POINT, 4326),
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

        # Descargar los datos desde el archivo CSV
        print("Descargando datos desde el archivo CSV...")
        data = pd.read_csv(CSV_URL, delimiter=";")

        # Verificar la estructura del CSV
        if data.empty:
            print("El archivo CSV está vacío o no contiene datos válidos.")
            return
        
        print(f"Datos descargados correctamente. Número de registros: {len(data)}")

        # Iterar sobre las filas del DataFrame
        for index, row in data.iterrows():
            # Extracción segura de los campos
            geo_point_2d = row["Geo Point"]
            geo_shape = row["Geo Shape"]
            coddistbar = row["coddistbar"]
            barrio = row["BARRIO"]
            codbarrio = row["codbarrio"]
            coddistrit = row["coddistrit"]
            distrito = row["DISTRITO"]
            precio_2022_euros_m2 = row["Precio_2022 (Euros/m2)"]
            precio_2010_euros_m2 = row["Precio_2010 (Euros/m2)"]
            max_historico_euros_m2 = row["Max_historico (Euros/m2)"]
            ano_max_hist = row["Año_Max_Hist"]
            fecha_creacion = row["Fecha_creacion"]

            # Validación de geometrías
            point_wkt = None
            if geo_point_2d and isinstance(geo_point_2d, str):
                lat, lon = map(float, geo_point_2d.split(","))
                point_wkt = f"POINT({lon} {lat})"
            geojson_str = geo_shape if isinstance(geo_shape, str) else None

            # Depuración: Imprimir datos a insertar
            print(f"Procesando registro: barrio={barrio}, distrito={distrito}")

            # Intentar la inserción en la base de datos
            try:
                cursor.execute("""
                INSERT INTO public."idealista" 
                (geo_point_2d, geo_shape, coddistbar, barrio, codbarrio, coddistrit, distrito, 
                 precio_2022_euros_m2, precio_2010_euros_m2, max_historico_euros_m2, ano_max_hist, fecha_creacion) 
                VALUES (ST_GeogFromText(%s), ST_GeomFromGeoJSON(%s), %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (point_wkt, geojson_str, coddistbar, barrio, codbarrio, coddistrit, distrito,
                      precio_2022_euros_m2, precio_2010_euros_m2, max_historico_euros_m2, ano_max_hist, fecha_creacion))
                print(f"Insertado registro con barrio={barrio}, distrito={distrito}")
            except Exception as e:
                print(f"Error al insertar registro con barrio={barrio}: {e}")

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
