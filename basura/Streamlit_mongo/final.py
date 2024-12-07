import streamlit as st
from pymongo import MongoClient
import folium
from streamlit_folium import st_folium

# Conexión a MongoDB
client = MongoClient("mongodb://root:example@localhost:27017/")
db = client["data_DataProject"]

# Obtener las colecciones disponibles
collections = db.list_collection_names()

# Configurar la interfaz de Streamlit
st.set_page_config(layout="wide")
st.sidebar.title("Seleccione las colecciones")

# Selección de colecciones
selected_collections = st.sidebar.multiselect(
    "Colecciones disponibles", collections
)

# Crear mapa base
m = folium.Map(location=[39.47, -0.38], zoom_start=12)  # Coordenadas de Valencia

# Procesar las colecciones seleccionadas
for collection_name in selected_collections:
    collection = db[collection_name]
    data = collection.find()  # Obtener todos los documentos

    for doc in data:
        # Manejar geometría en geo_shape
        if "geo_shape" in doc and "geometry" in doc["geo_shape"]:
            geometry = doc["geo_shape"]["geometry"]
            geom_type = geometry["type"]
            coordinates = geometry["coordinates"]

            if geom_type == "Polygon":
                # Convertir las coordenadas a formato folium (lat, lon)
                polygon_coords = [
                    [lat, lon] for lon, lat in coordinates[0]
                ]
                folium.Polygon(
                    locations=polygon_coords,
                    popup=f"{collection_name}: {doc}",
                    color="green",
                    fill=True,
                    fill_color="green",
                    fill_opacity=0.4,
                ).add_to(m)

# Mostrar el mapa en la interfaz
with st.container():
    st_folium(m, width=700, height=500)
