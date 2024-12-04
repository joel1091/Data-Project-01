import streamlit as st
import folium
from streamlit_folium import folium_static
from pymongo import MongoClient
import pandas as pd
import numpy as np

# Conexión a MongoDB
client = MongoClient("mongodb://root:example@localhost:27017/")
db = client['data_DataProject']
collection = db['Mapa_Ruido']

def get_color(gridcode):
    color_map = {
        1: 'green',     # Nivel de ruido más bajo
        2: 'lightgreen',
        3: 'yellow', 
        4: 'orange',
        5: 'darkorange',
        6: 'red'        # Nivel de ruido más alto
    }
    return color_map.get(gridcode, 'gray')  # En caso de que no sea un valor esperado, devuelve gris

def create_noise_map(gridcode_min, gridcode_max):
    # Configurar mapa centrado en Valencia
    m = folium.Map(location=[39.4697, -0.3773], zoom_start=12)
    
    # Recuperar documentos filtrados por gridcode
    documentos = list(collection.find({
        'gridcode': {
            '$gte': gridcode_min, 
            '$lte': gridcode_max
        }
    }))
    
    # Agregar polígonos para cada documento
    for doc in documentos:
        try:
            # Verificar que geo_shape y sus coordenadas existan
            if not doc.get('geo_shape') or not doc['geo_shape'].get('geometry'):
                continue
            
            # Extraer coordenadas del geo_shape
            coords = doc['geo_shape']['geometry']['coordinates'][0]
            
            # Invertir coordenadas (lon, lat) para Folium
            coords_inverted = [[point[1], point[0]] for point in coords]
            
            # Obtener gridcode con valor por defecto si es None
            gridcode = doc.get('gridcode', 0)
            
            # Color basado en gridcode
            color = get_color(gridcode)
            
            # Crear popup con información de ruido
            popup_text = f"""
            Grid Code: {gridcode}
            GID: {doc.get('gid', 'N/A')}
            """
            
            # Crear polígono
            folium.Polygon(
                locations=coords_inverted,
                color=color,
                fill=True,
                fill_color=color,
                fill_opacity=0.7,
                popup=popup_text
            ).add_to(m)
        
        except Exception as e:
            st.warning(f"Error procesando documento de ruido: {e}")
    
    return m

def main():
    # Cargar datos en un DataFrame para obtener rangos de gridcode
    df = pd.DataFrame(list(collection.find()))
    gridcodes = df['gridcode'].dropna()
    
    # Sidebar con filtros
    st.sidebar.header('Filtros de Nivel de Ruido')
    
    # Slider para rango de gridcode
    gridcode_min, gridcode_max = st.sidebar.slider(
        'Selecciona rango de niveles de ruido (Grid Code)',
        min_value=int(gridcodes.min()),
        max_value=int(gridcodes.max()),
        value=(int(gridcodes.min()), int(gridcodes.max()))
    )
    
    # Mostrar título principal
    st.title('Mapa de Niveles de Ruido en Valencia')
    
    # Crear mapa con filtro de gridcode
    noise_map = create_noise_map(gridcode_min, gridcode_max)
    
    # Mostrar mapa en Streamlit
    folium_static(noise_map)
    
    # Estadísticas de los niveles de ruido
    st.sidebar.header('Estadísticas de Ruido')
    
    # Filtrar gridcodes según el rango seleccionado
    gridcodes_filtrados = gridcodes[
        (gridcodes >= gridcode_min) & 
        (gridcodes <= gridcode_max)
    ]
    
    st.sidebar.write(f"Nivel de ruido medio: {gridcodes_filtrados.mean():.2f}")
    st.sidebar.write(f"Nivel de ruido mínimo: {gridcodes_filtrados.min():.2f}")
    st.sidebar.write(f"Nivel de ruido máximo: {gridcodes_filtrados.max():.2f}")
    st.sidebar.write(f"Número de zonas: {len(gridcodes_filtrados)}")

if __name__ == "__main__":
    main()