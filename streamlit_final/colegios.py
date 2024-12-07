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

# Función para cargar datos desde la base de datos
def load_data():
    conn = connect_to_database()
    if not conn:
        return pd.DataFrame()  # Retorna un DataFrame vacío en caso de error

    query = """
    SELECT 
        ST_X("Geo Point"::geometry) AS lon,  -- Longitud
        ST_Y("Geo Point"::geometry) AS lat,  -- Latitud
        dlibre AS nombre_centro,
        direccion,
        municipio,
        regimen
    FROM public."centros_educativos";
    """
    try:
        data = pd.read_sql_query(query, conn)
        return data
    except Exception as e:
        st.error(f"Error cargando los datos: {e}")
        return pd.DataFrame()
    finally:
        conn.close()

# Función para asignar colores según el régimen
def assign_colors(data):
    # Mapeo de colores: CONCERTADO = azul, PÚBLICO = rojo, PRIVADO = verde oscuro
    color_map = {
        "CONCERTADO": [0, 100, 255],  # Azul
        "PÚBLICO": [255, 0, 0],       # Rojo
        "PRIVADO": [0, 128, 0]        # Verde oscuro
    }
    # Asignar un color basado en el régimen
    data["color"] = data["regimen"].map(color_map)
    return data

# Aplicación principal de Streamlit
def main():
    st.title("Mapa Interactivo de Centros Educativos en Valencia")
    st.write("Elija opciones en el panel lateral para explorar los colegios disponibles.")

    # Panel lateral para la pregunta inicial
    st.sidebar.title("Opciones")
    tiene_hijos = st.sidebar.radio(
        "¿Tiene hijos en edad de ir al colegio?",
        ("No", "Sí")
    )

    # Mapa vacío si selecciona "No"
    if tiene_hijos == "No":
        r = pdk.Deck(
            layers=[],  # Sin capas
            initial_view_state=pdk.ViewState(
                latitude=39.4699,  # Coordenadas aproximadas de Valencia
                longitude=-0.3763,
                zoom=13,
                pitch=0
            ),
            map_style="mapbox://styles/mapbox/streets-v11",
        )
        st.pydeck_chart(r)
        return

    # Cargar los datos desde la base de datos
    data = load_data()

    if data.empty:
        st.warning("No se pudieron cargar datos. Revisa la conexión con la base de datos.")
        return

    # Filtrar datos por régimen según selección en el desplegable
    regimen_opcion = st.sidebar.selectbox(
        "¿A qué tipo de colegio le gustaría llevar a su hijo?",
        ("CONCERTADO", "PÚBLICO", "PRIVADO")
    )

    # Filtrar los datos según el régimen seleccionado
    data = data[data["regimen"] == regimen_opcion]

    if data.empty:
        st.warning(f"No hay colegios disponibles para el régimen seleccionado: {regimen_opcion}")
        return

    # Asignar colores según el régimen
    data = assign_colors(data)

    st.write(f"Se han cargado los colegios del tipo: {regimen_opcion}")

    # Mostrar la tabla de datos (opcional)
    if st.checkbox("Mostrar datos en tabla"):
        st.dataframe(data)

    # Configurar el estado inicial del mapa
    view_state = pdk.ViewState(
        latitude=39.4699,  # Coordenadas aproximadas de Valencia
        longitude=-0.3763,
        zoom=13,
        pitch=0  # Sin inclinación (2D)
    )

    # Capa de puntos con ScatterplotLayer
    scatter_layer = pdk.Layer(
        "ScatterplotLayer",
        data=data,
        get_position=["lon", "lat"],
        get_color="color",  # Usar la columna de colores asignados
        radius_min_pixels=8,  # Tamaño constante de los puntos
        radius_max_pixels=8,  # Fijar el tamaño al mismo valor
        pickable=True,
    )

    # Tooltip con información adicional
    tooltip = {
        "html": """
        <b>Centro:</b> {nombre_centro}<br>
        <b>Dirección:</b> {direccion}<br>
        """,
        "style": {"backgroundColor": "steelblue", "color": "white"}
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
