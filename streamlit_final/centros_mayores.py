import streamlit as st
import pydeck as pdk
import psycopg2
import pandas as pd

# Configuración de la conexión a PostgreSQL
POSTGRES_CONFIG = {
    "host": "localhost",  # Cambia según tu configuración
    "port": 5432,
    "database": "data_project",  # Nombre de tu base de datos
    "user": "postgres",
    "password": "Welcome01"  # Cambia tu contraseña
}

# Función para conectar a la base de datos
def connect_to_database():
    try:
        conn = psycopg2.connect(**POSTGRES_CONFIG)
        return conn
    except Exception as e:
        st.error(f"Error conectando a la base de datos: {e}")
        return None

# Función para cargar datos desde la tabla centros_mayores
def load_centros_mayores_data():
    conn = connect_to_database()
    if not conn:
        return pd.DataFrame()  # Retorna un DataFrame vacío si no hay conexión

    query = """
    SELECT 
        ST_X(geo_point_2d::geometry) AS lon,  -- Longitud
        ST_Y(geo_point_2d::geometry) AS lat,  -- Latitud
        equipamien AS nombre,  -- Nombre del centro
        telefono,  -- Teléfono
        numportal AS numero,  -- Número del portal
        codvia,  -- Código de vía
        identifica AS identificador  -- Identificador único (nombre corregido)
    FROM public."centros_mayores";
    """
    try:
        data = pd.read_sql_query(query, conn)
        return data
    except Exception as e:
        st.error(f"Error cargando los datos: {e}")
        return pd.DataFrame()
    finally:
        conn.close()

# Función principal de la aplicación Streamlit
def main():
    st.title("Mapa de Centros de Mayores en Valencia")
    st.write("Este mapa muestra la ubicación de los centros de mayores en Valencia con puntos de tonalidad gris.")

    # Cargar los datos
    data = load_centros_mayores_data()

    if data.empty:
        st.warning("No se encontraron datos de los centros de mayores.")
        return

    # Definir estado inicial del mapa
    view_state = pdk.ViewState(
        latitude=39.4699,  # Coordenada central aproximada de Valencia
        longitude=-0.3763,
        zoom=13,
        pitch=0  # Vista 2D
    )

    # Crear capa de puntos para los centros de mayores
    layer = pdk.Layer(
        "ScatterplotLayer",
        data=data,
        get_position=["lon", "lat"],
        get_color=[96, 96, 96, 255],  # Tonalidad gris con transparencia
        radius_min_pixels=8,  # Tamaño de los puntos
        pickable=True
    )

    # Crear un tooltip dinámico
    tooltip = {
        "html": """
        <b>Nombre:</b> {nombre}<br>
        <b>Teléfono:</b> {telefono}<br>
        <b>Dirección:</b> {numero}, {codvia}
        """,
        "style": {
            "backgroundColor": "black",
            "color": "white"
        }
    }

    # Crear el mapa con Pydeck
    r = pdk.Deck(
        layers=[layer],
        initial_view_state=view_state,
        map_style="mapbox://styles/mapbox/streets-v11",
        tooltip=tooltip
    )

    # Mostrar el mapa
    st.pydeck_chart(r)

# Ejecutar la aplicación
if __name__ == "__main__":
    main()
