import streamlit as st
import psycopg2
import pandas as pd
import pydeck as pdk

# Configuración de la conexión a PostgreSQL
POSTGRES_CONFIG = {
    "host": "localhost",  # Cambia a tu configuración
    "port": 5432,
    "database": "data_project",
    "user": "postgres",
    "password": "Welcome01"
}

# Función para conectar a PostgreSQL
def connect_to_database():
    try:
        conn = psycopg2.connect(**POSTGRES_CONFIG)
        return conn
    except Exception as e:
        st.error(f"Error conectando a la base de datos: {e}")
        return None

# Función para cargar datos de cajeros desde la base de datos
def load_atm_data():
    conn = connect_to_database()
    if not conn:
        return pd.DataFrame()  # Retorna un DataFrame vacío en caso de error

    query = """
    SELECT 
        ST_X(geo_point_2d::geometry) AS lon,  -- Longitud
        ST_Y(geo_point_2d::geometry) AS lat,  -- Latitud
        modelo,
        num_banco,
        emplazamiento,
        distrito,
        barrio
    FROM public."cajeros";
    """
    try:
        data = pd.read_sql_query(query, conn)
        return data
    except Exception as e:
        st.error(f"Error cargando los datos: {e}")
        return pd.DataFrame()
    finally:
        conn.close()

# Aplicación principal de Streamlit
def main():
    # Solo mostramos el título solicitado
    st.title("¿Qué zona prefieres para vivir?")

    # Cargar los datos de cajeros desde la base de datos
    data = load_atm_data()

    if data.empty:
        st.warning("No se pudieron cargar datos. Revisa la conexión con la base de datos.")
        return

    # Configurar el estado inicial del mapa
    view_state = pdk.ViewState(
        latitude=data["lat"].mean(),  # Centro del mapa basado en los datos
        longitude=data["lon"].mean(),
        zoom=13,
        pitch=0  # Sin inclinación (2D)
    )

    # Capa de puntos con ScatterplotLayer
    scatter_layer = pdk.Layer(
        "ScatterplotLayer",
        data=data,
        get_position=["lon", "lat"],
        get_color=[255, 105, 180, 160],  # Rosa con transparencia
        get_radius=20,  # Tamaño de los puntos
        pickable=True,  # Habilitar interactividad
    )

    # Tooltip con información adicional
    tooltip = {
        "html": """
        <b>Barrio:</b> {barrio}<br>
        <b>Distrito:</b> {distrito}
        """,
        "style": {"backgroundColor": "hotpink", "color": "white"}
    }

    # Configurar el estilo del mapa
    r = pdk.Deck(
        layers=[scatter_layer],
        initial_view_state=view_state,
        map_style="mapbox://styles/mapbox/streets-v11",  # Mapa estilo calles
        tooltip=tooltip
    )

    # Mostrar el mapa en Streamlit
    st.pydeck_chart(r)

if __name__ == "__main__":
    main()
