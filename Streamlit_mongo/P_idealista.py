import streamlit as st
import folium
from streamlit_folium import folium_static
from pymongo import MongoClient
import pandas as pd
import numpy as np

# Conexión a MongoDB
client = MongoClient("mongodb://root:example@localhost:27017/")
db = client['data_DataProject']
collection = db['Precio_Idealista']

def create_price_map(precio_min, precio_max):
    # Configurar mapa centrado en Valencia
    m = folium.Map(location=[39.4697, -0.3773], zoom_start=12)
    
    # Recuperar documentos filtrados por precio
    documentos = list(collection.find({
        'precio_2022_euros_m2': {
            '$gte': precio_min, 
            '$lte': precio_max
        }
    }))
    
    # Función para escalar colores según precio
    def get_color(precio):
        if precio is None:
            return 'gray'
        elif precio < 2000:
            return 'green'
        elif precio < 2500:
            return 'yellow'
        elif precio < 3000:
            return 'orange'
        else:
            return 'red'
    
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
            
            # Obtener precio con valor por defecto si es None
            precio_2022 = doc.get('precio_2022_euros_m2', 0)
            
            # Color basado en precio 2022
            color = get_color(precio_2022)
            
            # Crear popup con manejo de valores None
            popup_text = f"""
            Barrio: {doc.get('barrio', 'N/A')}
            Distrito: {doc.get('distrito', 'N/A')}
            Precio 2022: {precio_2022}€/m²
            Precio 2010: {doc.get('precio_2010_euros_m2', 'N/A')}€/m²
            Máximo histórico: {doc.get('max_historico_euros_m2', 'N/A')}€/m²
            """
            
            # Crear polígono
            folium.Polygon(
                locations=coords_inverted,
                color=color,
                fill=True,
                fill_color=color,
                fill_opacity=0.5,
                popup=popup_text
            ).add_to(m)
        
        except Exception as e:
            st.warning(f"Error procesando documento: {e}")
    
    return m

def main():
    # Cargar datos en un DataFrame para obtener rangos de precios
    df = pd.DataFrame(list(collection.find()))
    precios_2022 = df['precio_2022_euros_m2'].dropna()
    
    # Sidebar con filtros
    st.sidebar.header('Filtros de Precio')
    
    # Slider para rango de precios
    precio_min, precio_max = st.sidebar.slider(
        'Selecciona rango de precios (€/m²)',
        min_value=int(precios_2022.min()),
        max_value=int(precios_2022.max()),
        value=(int(precios_2022.min()), int(precios_2022.max()))
    )
    
    # Mostrar título principal
    st.title('Mapa de Precios Inmobiliarios de Valencia')
    
    # Crear mapa con filtro de precios
    price_map = create_price_map(precio_min, precio_max)
    
    # Mostrar mapa en Streamlit
    folium_static(price_map)
    
    # Estadísticas de los barrios filtrados
    st.sidebar.header('Estadísticas')
    
    # Filtrar precios según el rango seleccionado
    precios_filtrados = precios_2022[
        (precios_2022 >= precio_min) & 
        (precios_2022 <= precio_max)
    ]
    
    st.sidebar.write(f"Precio medio: {precios_filtrados.mean():.2f}€/m²")
    st.sidebar.write(f"Precio mínimo: {precios_filtrados.min():.2f}€/m²")
    st.sidebar.write(f"Precio máximo: {precios_filtrados.max():.2f}€/m²")
    st.sidebar.write(f"Número de barrios: {len(precios_filtrados)}")

if __name__ == "__main__":
    main()