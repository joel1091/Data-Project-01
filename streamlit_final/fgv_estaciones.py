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

# Función para cargar datos desde la tabla de estaciones FGV
def load_fgv_estaciones_data():
    conn = connect_to_database()
    if not conn:
        return pd.DataFrame()  # Retorna un DataFrame vacío si no hay conexión

    query = """
    SELECT 
        ST_X(geo_point_2d::geometry) AS lon,  -- Longitud
        ST_Y(geo_point_2d::geometry) AS lat,  -- Latitud
        "Nom / Nombre" AS nombre,  -- Nombre de la estación
        "Línia / Línea" AS linea,  -- Líneas asociadas
        "Tipus / Tipo" AS tipo  -- Tipo de estación
    FROM fgv_estaciones;
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
    st.title("Mapa de Estaciones FGV en Valencia")
    st.write("Este mapa muestra las estaciones de FGV en Valencia con puntos de color amarillo.")

    # Cargar los datos
    data = load_fgv_estaciones_data()

    if data.empty:
        st.warning("No se encontraron datos de las estaciones FGV.")
        return

    # Definir estado inicial del mapa
    view_state = pdk.ViewState(
        latitude=data["lat"].mean(),  # Centro del mapa basado en los datos
        longitude=data["lon"].mean(),
        zoom=13,
        pitch=0  # Vista 2D
    )

    # Crear capa de puntos para las estaciones FGV
    layer = pdk.Layer(
        "ScatterplotLayer",
        data=data,
        get_position=["lon", "lat"],
        get_color=[255, 223, 0, 255],  # Color amarillo (RGB) con opacidad máxima
        radius_min_pixels=8,  # Tamaño de los puntos
        pickable=True
    )

    # Crear un tooltip dinámico
    tooltip = {
        "html": """
        <b>Nombre:</b> {nombre}<br>
        <b>Línea:</b> {linea}<br>
        <b>Tipo:</b> {tipo}
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
