import streamlit as st
import pydeck as pdk
import psycopg2
import pandas as pd
import json

# Configuración de conexión a PostgreSQL
POSTGRES_CONFIG = {
    "host": "localhost",  # Cambia según tu configuración
    "port": 5432,
    "database": "data_project",  # Nombre de tu base de datos
    "user": "postgres",
    "password": "Welcome01"  # Cambia tu contraseña
}

# Función para conectar a la base de datos
def connect_to_database():
    """
    Establece conexión con la base de datos PostgreSQL.

    Returns:
        conn: Conexión activa a la base de datos o None si ocurre un error.
    """
    try:
        conn = psycopg2.connect(**POSTGRES_CONFIG)
        return conn
    except Exception as e:
        st.error(f"Error conectando a la base de datos: {e}")
        return None

# Función para cargar datos del dataset de zonas verdes
def load_zones_verdes_data():
    """
    Carga los datos del dataset de zonas verdes desde la base de datos.

    Returns:
        pd.DataFrame: Datos de zonas verdes con geometrías en formato GeoJSON.
    """
    conn = connect_to_database()
    if not conn:
        return pd.DataFrame()

    query = """
    SELECT 
        ST_AsGeoJSON(geo_shape) AS geometry,  -- Convertir la geometría a formato GeoJSON
        nombre,  -- Nombre del área verde
        area,  -- Área de la zona
        tipologia  -- Tipología del área verde
    FROM zones_verdes;
    """
    try:
        data = pd.read_sql_query(query, conn)
        return data
    except Exception as e:
        st.error(f"Error cargando los datos de zonas verdes: {e}")
        return pd.DataFrame()
    finally:
        conn.close()

# Función principal
def main():
    """
    Muestra el mapa con las zonas verdes.
    """
    st.title("Mapa Interactivo: Zonas Verdes en Valencia")

    # Cargar los datos de zonas verdes
    data = load_zones_verdes_data()

    if data.empty:
        st.warning("No se encontraron datos de Zonas Verdes.")
        return

    # Convertir la columna de geometría (GeoJSON) a formato diccionario
    data["geometry"] = data["geometry"].apply(json.loads)

    # Configurar la capa GeoJson
    geojson_layer = pdk.Layer(
        "GeoJsonLayer",
        data=data,
        get_fill_color="[0, 128, 0, 150]",  # Verde con opacidad
        get_line_color=[0, 0, 0],  # Bordes negros
        pickable=True,
    )

    # Configurar el estado inicial del mapa
    view_state = pdk.ViewState(
        latitude=39.4699,  # Coordenadas aproximadas de Valencia
        longitude=-0.3763,
        zoom=12,
        pitch=0
    )

    # Configurar tooltip
    tooltip = {
        "html": """
        <b>Nombre:</b> {nombre}<br>
        <b>Área:</b> {area} m²<br>
        <b>Tipología:</b> {tipologia}<br>
        """,
        "style": {"backgroundColor": "black", "color": "white"}
    }

    # Crear y mostrar el mapa con la capa GeoJson
    r = pdk.Deck(
        layers=[geojson_layer],
        initial_view_state=view_state,
        map_style="mapbox://styles/mapbox/light-v10",
        tooltip=tooltip
    )

    st.pydeck_chart(r)

if __name__ == "__main__":
    main()
