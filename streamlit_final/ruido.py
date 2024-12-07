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
    try:
        conn = psycopg2.connect(**POSTGRES_CONFIG)
        return conn
    except Exception as e:
        st.error(f"Error conectando a la base de datos: {e}")
        return None

# Función para cargar datos del dataset de ruido
def load_ruido_data():
    conn = connect_to_database()
    if not conn:
        return pd.DataFrame()

    query = """
    SELECT 
        ST_AsGeoJSON(geo_shape) AS geometry,  -- Convertir la geometría a formato GeoJSON
        gridcode  -- Nivel de ruido (1 a 6)
    FROM ruido;
    """
    try:
        data = pd.read_sql_query(query, conn)
        return data
    except Exception as e:
        st.error(f"Error cargando los datos: {e}")
        return pd.DataFrame()
    finally:
        conn.close()

# Función para asignar colores según nivel de ruido
def get_ruido_color(gridcode):
    # Gradiente de colores (de menos a más ruido)
    colores = {
        1: [0, 255, 0],  # Verde claro (menos ruidoso)
        2: [173, 255, 47],  # Verde más intenso
        3: [255, 255, 0],  # Amarillo
        4: [255, 165, 0],  # Naranja
        5: [255, 69, 0],  # Rojo claro
        6: [255, 0, 0],  # Rojo fuerte (más ruidoso)
    }
    return colores.get(gridcode, [128, 128, 128])  # Gris por defecto si no está definido

# Función principal
def main():
    st.title("Mapa Interactivo: Zonas Ruidosas")

    # Cargar los datos de ruido
    ruido_data = load_ruido_data()

    if ruido_data.empty:
        st.warning("No se encontraron datos de ruido.")
        return

    # Convertir la columna de geometría (GeoJSON) a formato diccionario
    ruido_data["geometry"] = ruido_data["geometry"].apply(json.loads)

    # Añadir la columna de colores según el nivel de ruido
    ruido_data["color"] = ruido_data["gridcode"].apply(get_ruido_color)

    # Configurar la capa GeoJson para el ruido
    ruido_layer = pdk.Layer(
        "GeoJsonLayer",
        data=ruido_data,
        get_fill_color="color",  # Usar el color según el nivel de ruido
        get_line_color=[0, 0, 0],  # Bordes negros
        pickable=True,
        opacity=0.7  # Transparencia de las zonas
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
        <b>Nivel de Ruido:</b> {gridcode}<br>
        """,
        "style": {"backgroundColor": "black", "color": "white"}
    }

    # Crear y mostrar el mapa con la capa de ruido
    r = pdk.Deck(
        layers=[ruido_layer],
        initial_view_state=view_state,
        map_style="mapbox://styles/mapbox/light-v10",
        tooltip=tooltip
    )

    st.pydeck_chart(r)

if __name__ == "__main__":
    main()
