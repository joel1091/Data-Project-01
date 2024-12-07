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

# Función para cargar datos del dataset vulnerabilidad_barrios
def load_vulnerabilidad_barrios_data():
    conn = connect_to_database()
    if not conn:
        return pd.DataFrame()

    query = """
    SELECT 
        ST_AsGeoJSON(geo_shape) AS geometry,  -- Convertir la geometría a formato GeoJSON
        nombre,  -- Nombre del barrio
        ind_global_txt,  -- Nivel de vulnerabilidad (Texto)
        ind_global  -- Índice global de vulnerabilidad (Numérico)
    FROM vulnerabilidad_barrios;
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
    st.title("Mapa Interactivo: Vulnerabilidad de Barrios en Valencia")

    # Cargar los datos de vulnerabilidad de barrios
    data = load_vulnerabilidad_barrios_data()

    if data.empty:
        st.warning("No se encontraron datos de vulnerabilidad de barrios.")
        return

    # Convertir la columna de geometría (GeoJSON) a formato diccionario
    data["geometry"] = data["geometry"].apply(json.loads)

    # Configurar la selección de niveles de vulnerabilidad
    vulnerabilidad_opcion = st.sidebar.selectbox(
        "Selecciona el nivel de vulnerabilidad a visualizar:",
        options=["Todas", "Vulnerabilidad Alta", "Vulnerabilidad Media", "Vulnerabilidad Baja"],
        index=0
    )

    # Filtrar los datos según la opción seleccionada
    if vulnerabilidad_opcion != "Todas":
        filtered_data = data[data["ind_global_txt"] == vulnerabilidad_opcion]
    else:
        filtered_data = data

    # Asignar colores según el nivel de vulnerabilidad
    def get_color(vulnerability):
        if vulnerability == "Vulnerabilidad Alta":
            return [255, 0, 0, 150]  # Rojo
        elif vulnerability == "Vulnerabilidad Media":
            return [255, 165, 0, 150]  # Naranja
        elif vulnerability == "Vulnerabilidad Baja":
            return [0, 255, 0, 150]  # Verde
        else:
            return [200, 200, 200, 150]  # Gris para valores desconocidos

    filtered_data["color"] = filtered_data["ind_global_txt"].apply(get_color)

    # Configurar la capa GeoJson
    geojson_layer = pdk.Layer(
        "GeoJsonLayer",
        data=filtered_data,
        get_fill_color="color",  # Usar la columna de color
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
        <b>Nombre del Barrio:</b> {nombre}<br>
        <b>Nivel de Vulnerabilidad:</b> {ind_global_txt}<br>
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
