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
JSON_URL = "https://valencia.opendatasoft.com/api/explore/v2.1/catalog/datasets/centros-educativos-en-valencia/exports/json?lang=es&timezone=Europe%2FBerlin"

def main():
    try:
        # Conexión a PostgreSQL
        conn = psycopg2.connect(**POSTGRES_CONFIG)
        conn.autocommit = True
        cursor = conn.cursor()

        # Verificar si PostGIS está habilitado
        cursor.execute("SELECT PostGIS_Version();")
        if not cursor.fetchone():
            print("Error: PostGIS no está habilitado en esta base de datos.")
            return

        # Crear la tabla si no existe
        create_table_query = """
        CREATE TABLE IF NOT EXISTS public."centros_educativos" (
            "Geo Point" GEOGRAPHY,
            "Geo Shape" GEOMETRY,
            "codcen" INTEGER NOT NULL,
            "dlibre" VARCHAR(255),
            "dgenerica_" VARCHAR(255),
            "despecific" VARCHAR(255),
            "regimen" VARCHAR(20),
            "direccion" VARCHAR(255),
            "codpos" INTEGER,
            "municipio" VARCHAR(255),
            "provincia" VARCHAR(255),
            "telef" INTEGER,
            "fax" INTEGER,
            "mail" VARCHAR(255)
        );
        """
        cursor.execute(create_table_query)
        print("Tabla creada exitosamente o ya existe.")

        # Descargar los datos desde la URL
        print("Descargando datos desde la URL...")
        response = requests.get(JSON_URL)
        if response.status_code != 200:
            print(f"Error al descargar los datos: {response.status_code}")
            return
        data = response.json()
        print("Datos descargados correctamente.")

        # Iterar sobre los elementos del JSON e insertar en la tabla
        for item in data:
            # Extraer campos principales
            geo_point_2d = item.get("geo_point_2d", None)
            geo_shape = item.get("geo_shape", {}).get("geometry", None)
            codcen = item.get("codcen")
            dlibre = item.get("dlibre")
            dgenerica_ = item.get("dgenerica")
            despecific = item.get("despecific")
            regimen = item.get("regimen")
            direccion = item.get("direccion")
            codpos = item.get("codpos")
            municipio = item.get("municipio")
            provincia = item.get("provincia")
            telef = item.get("telef")
            fax = item.get("fax")
            mail = item.get("mail")

            # Convertir geo_point_2d a formato WKT
            point_wkt = None
            if geo_point_2d:
                lon = geo_point_2d.get("lon")
                lat = geo_point_2d.get("lat")
                if lon is not None and lat is not None:
                    point_wkt = f"POINT({lon} {lat})"

            # Convertir geo_shape a GeoJSON
            geojson_str = json.dumps(geo_shape) if geo_shape else None

            # Insertar registro en la tabla
            insert_query = """
            INSERT INTO public."centros_educativos" 
            ("Geo Point", "Geo Shape", codcen, dlibre, dgenerica_, despecific, regimen, direccion, codpos, municipio, provincia, telef, fax, mail) 
            VALUES (ST_GeogFromText(%s), ST_GeomFromGeoJSON(%s), %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(insert_query, (point_wkt, geojson_str, codcen, dlibre, dgenerica_, despecific, regimen, direccion, codpos, municipio, provincia, telef, fax, mail))
            print(f"Insertado registro con codcen={codcen}")

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
