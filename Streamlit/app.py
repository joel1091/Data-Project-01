import streamlit as st
import pandas as pd
from pymongo import MongoClient
import folium
from streamlit_folium import st_folium

# Conexión a MongoDB
client = MongoClient("mongodb://root:example@localhost:27017/")  # Cambia 'localhost' si estás en otro entorno
db = client["data_DataProject"]  # Nombre de tu base de datos

# Obtener todas las colecciones
collections = db.list_collection_names()

# Función para obtener datos de una colección seleccionada
def get_data(collection_name):
    collection = db[collection_name]
    data = list(collection.find())
    if data:
        df = pd.DataFrame(data)
        return df
    else:
        return pd.DataFrame()

# Selección de la colección
st.sidebar.header("Selecciona una categoría")
selected_collection = st.sidebar.selectbox("Colección", collections)

if selected_collection:
    # Obtener los datos de la colección seleccionada
    df = get_data(selected_collection)

    # Mostrar los datos en el mapa
    if not df.empty:
        # Asegúrate de que hay datos geográficos
        if "geo_point_2d" in df.columns:
            st.subheader(f"Mapa de {selected_collection}")

            # Checkbox para mostrar/ocultar puntos
            show_points = st.checkbox("Mostrar puntos rojos", value=True)

            # Crear el mapa centrado en Valencia
            m = folium.Map(location=[39.4699, -0.3763], zoom_start=12)  # Coordenadas de Valencia

            if show_points:
                # Añadir puntos al mapa (solo marcadores sin información extra)
                for _, row in df.iterrows():
                    geo_point = row.get("geo_point_2d")
                    if geo_point:  # Verificar si existen coordenadas
                        folium.CircleMarker(
                            location=[geo_point['lat'], geo_point['lon']],
                            radius=1,  # Tamaño del punto
                            color='red',  # Color del borde
                            fill=True,
                            fill_color='red',  # Color del relleno
                            fill_opacity=0.8  # Opacidad del punto
                        ).add_to(m)

            # Mostrar el mapa en Streamlit
            st_folium(m, width=700, height=500)
        else:
            st.warning(f"La colección '{selected_collection}' no contiene datos geográficos.")
    else:
        st.error(f"No se encontraron datos en la colección '{selected_collection}'.")
else:
    st.error("Por favor selecciona una colección en el menú lateral.")
