import streamlit as st
import psycopg2
import pandas as pd
import folium
from streamlit_folium import st_folium
from config import host, port, database, user, password  # Importar credenciales desde config.py


def get_connection():
    """Crea una conexión a la base de datos usando las configuraciones de config.py."""
    return psycopg2.connect(
        host=host,
        port=port,
        database=database,
        user=user,
        password=password
    )


def get_table_names(conn):
    """Obtiene los nombres de las tablas relevantes (no del sistema) en la base de datos."""
    query = """
    SELECT table_name
    FROM information_schema.tables
    WHERE table_schema = 'public'
    AND table_name NOT IN ('geography_columns', 'geometry_columns', 'spatial_ref_sys');
    """
    with conn.cursor() as cursor:
        cursor.execute(query)
        tables = cursor.fetchall()
    return [table[0] for table in tables]


def get_table_data(conn, table_name):
    """Obtiene los datos de una tabla específica."""
    # Detectar si la tabla tiene una columna geográfica
    query = f"""
    SELECT column_name
    FROM information_schema.columns
    WHERE table_schema = 'public' AND table_name = '{table_name}' AND udt_name IN ('geometry', 'geography');
    """
    with conn.cursor() as cursor:
        cursor.execute(query)
        geo_column = cursor.fetchone()

    if geo_column:
        geo_column = geo_column[0]
        # Convertir la columna geográfica a GeoJSON
        query = f"""
        SELECT *, ST_AsGeoJSON({geo_column}) AS geojson
        FROM public.{table_name};
        """
    else:
        # Si no hay columna geográfica, recuperar todos los datos
        query = f"SELECT * FROM public.{table_name};"

    with conn.cursor() as cursor:
        cursor.execute(query)
        columns = [desc[0] for desc in cursor.description]
        data = cursor.fetchall()
    return pd.DataFrame(data, columns=columns)


def main():
    st.title("Visualizador de Bases de Datos Geográficas")
    st.write("Selecciona una tabla de la base de datos `Data_Project` para visualizarla en el mapa.")

    # Conexión a PostgreSQL
    try:
        conn = get_connection()
    except Exception as e:
        st.error(f"Error al conectar a la base de datos: {e}")
        return

    # Obtener nombres de las tablas relevantes
    table_names = get_table_names(conn)
    if not table_names:
        st.error("No se encontraron tablas en la base de datos.")
        conn.close()
        return

    # Selector de tablas
    selected_table = st.selectbox("Selecciona una tabla", table_names)

    # Mostrar datos en un mapa si hay tabla seleccionada
    if selected_table:
        st.write(f"Mostrando datos de la tabla: `{selected_table}`")
        try:
            data = get_table_data(conn, selected_table)

            # Verificar si hay una columna `geojson`
            if 'geojson' not in data.columns:
                st.error("La tabla seleccionada no contiene datos geográficos en un formato compatible.")
            else:
                # Procesar GeoJSON para extraer coordenadas
                data['coordinates'] = data['geojson'].apply(lambda x: pd.json.loads(x)['coordinates'])

                # Crear un mapa
                mapa = folium.Map(location=[data['coordinates'].iloc[0][1], data['coordinates'].iloc[0][0]], zoom_start=12)

                # Agregar marcadores al mapa
                for _, row in data.iterrows():
                    popup_info = f"""
                    <b>Barrio:</b> {row.get('barrio', 'N/A')}<br>
                    <b>Distrito:</b> {row.get('distrito', 'N/A')}<br>
                    """
                    folium.Marker(
                        location=[row['coordinates'][1], row['coordinates'][0]],
                        popup=folium.Popup(popup_info, max_width=300)
                    ).add_to(mapa)

                # Renderizar el mapa
                st_folium(mapa, width=700, height=500)

        except Exception as e:
            st.error(f"Error al procesar los datos de la tabla: {e}")

    # Cerrar conexión
    conn.close()


if __name__ == "__main__":
    main()
