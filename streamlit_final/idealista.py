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

# Función para cargar datos del dataset idealista
def load_idealista_data():
    conn = connect_to_database()
    if not conn:
        return pd.DataFrame()

    query = """
    SELECT 
        ST_AsGeoJSON(geo_shape) AS geometry,  -- Convertir la geometría a formato GeoJSON
        barrio,  -- Nombre del barrio
        distrito,  -- Nombre del distrito
        precio_2022_euros_m2  -- Precio en euros por metro cuadrado
    FROM idealista;
    """
    try:
        data = pd.read_sql_query(query, conn)
        return data
    except Exception as e:
        st.error(f"Error cargando los datos: {e}")
        return pd.DataFrame()
    finally:
        conn.close()

# Función principal
def main():
    st.title("Mapa Interactivo: Precios por Zonas en Valencia")

    # Cargar los datos de Idealista
    data = load_idealista_data()

    if data.empty:
        st.warning("No se encontraron datos de Idealista.")
        return

    # Convertir la columna de geometría (GeoJSON) a formato diccionario
    data["geometry"] = data["geometry"].apply(json.loads)

    # Configurar el control deslizante para presupuesto máximo
    max_price = st.sidebar.slider(
        "Selecciona tu presupuesto máximo (€ por m²):",
        min_value=int(data["precio_2022_euros_m2"].min()),
        max_value=int(data["precio_2022_euros_m2"].max()),
        value=int(data["precio_2022_euros_m2"].max())
    )

    # Filtrar las zonas por presupuesto máximo
    filtered_data = data[data["precio_2022_euros_m2"] <= max_price]

    # Configurar la capa GeoJson
    geojson_layer = pdk.Layer(
        "GeoJsonLayer",
        data=filtered_data,
        get_fill_color="[255, 0, 0, 100 * (1 - precio_2022_euros_m2 / max_price)]",  # Más transparente para zonas caras
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
        <b>Distrito:</b> {distrito}<br>
        <b>Precio (€/m²):</b> {precio_2022_euros_m2}<br>
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
