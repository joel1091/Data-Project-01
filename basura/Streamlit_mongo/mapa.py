import streamlit as st
import folium
import pandas as pd
from pymongo import MongoClient
from folium.plugins import MarkerCluster
from streamlit_folium import st_folium  # Asegúrate de importar st_folium

# Conexión a MongoDB
client = MongoClient("mongodb://root:example@localhost:27017/")  # Cambia 'localhost' si estás en otro entorno
db = client["data_DataProject"]  # Nombre de tu base de datos

# Obtener todas las colecciones
collections = db.list_collection_names()

# Función para obtener datos de una colección
def get_data(collection_name):
    collection = db[collection_name]
    data = list(collection.find())
    if data:
        df = pd.DataFrame(data)
        return df
    else:
        return pd.DataFrame()

# Crear una lista para almacenar los puntos (latitud, longitud, y el nombre de la colección)
points = []

# Recopilar los datos de todas las colecciones
for collection_name in collections:
    df = get_data(collection_name)
    if not df.empty:
        # Verificar si la colección tiene las coordenadas necesarias
        if 'geo_point_2d' in df.columns:
            # Extraer latitud y longitud
            for _, row in df.iterrows():
                geo_point = row['geo_point_2d']
                if geo_point and isinstance(geo_point, dict):
                    lat = geo_point.get('lat')
                    lon = geo_point.get('lon')
                    if lat and lon:
                        points.append({'lat': lat, 'lon': lon, 'collection': collection_name})

# Crear un mapa centrado en Valencia
m = folium.Map(location=[39.4699, -0.3763], zoom_start=12)

# Crear un grupo de marcadores (para agrupar los puntos)
marker_cluster = MarkerCluster().add_to(m)

# Añadir los puntos al mapa
for point in points:
    folium.Marker(
        location=[point['lat'], point['lon']],
        popup=f"Colección: {point['collection']}",
        icon=folium.Icon(color='red')
    ).add_to(marker_cluster)

# Mostrar el mapa en Streamlit
st.title("Mapa de puntos de varias colecciones")
st.markdown("Mapa que muestra los puntos de las colecciones con coordenadas en MongoDB.")
st.write("Haz clic en los puntos para ver a qué colección pertenecen.")
st_folium(m, width=700, height=500)

Actividades_Infantiles, Cajeros, Carril_Bici, Centros_Discapacitados, Centros_Educativos, Centros_Mayores, Centros_Migrantes,
Hospitales, Mapa_Ruido, Monumentos_historicos, Parking_Movilidad_Reducida, Precio_Fotocasa, Precio_Idealista, Puntos_Carga_ElectricCar,
Tramvia, ValenBisi, Vulnerabilidad_Barrios, Zonas_Verdes, Parques, EMT