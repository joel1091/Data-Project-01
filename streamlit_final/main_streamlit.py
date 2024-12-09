import streamlit as st
import pydeck as pdk
import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
from shapely.geometry import Point, shape
import json

# 🔄 Importar funciones desde los archivos correspondientes
from idealista import load_idealista_data
from vulnerabilidad_barrios import load_vulnerabilidad_barrios_data
from colegios import load_data as load_colegios_data
from discapacidad import load_discapacidad_data
from ruido import load_ruido_data, get_ruido_color  # 🔥 Importación de la función de ruido

# 🌈 Función para calcular el color del precio
def calculate_price_color(price, min_price, max_price):
    norm = (price - min_price) / (max_price - min_price)
    r = int(255 * norm)
    g = int(255 * (1 - norm))
    return [r, g, 0, 150]  # Transparencia de 150

# 🚀 Función principal
def main():
    st.title("Mapa Interactivo de Valencia 🗺️")

    # 🔧 Opciones de Visualización
    st.sidebar.title("🔧 Incluir las siguientes capas:")
    incluir_precios = st.sidebar.radio("¿Incluir precios por zonas?", ("No", "Sí")) == "Sí"
    incluir_vulnerabilidad = st.sidebar.radio("¿Incluir vulnerabilidad de barrios?", ("No", "Sí")) == "Sí"
    incluir_ruido = st.sidebar.radio("¿Incluir ruido?", ("No", "Sí")) == "Sí"
    incluir_colegios = st.sidebar.radio("¿Incluir colegios?", ("No", "Sí")) == "Sí"
    incluir_discapacidad = st.sidebar.radio("¿Incluir centros de discapacidad?", ("No", "Sí")) == "Sí"

    layers = []
    visible_zone = None

    # 🗂️ 1️⃣ Cargar los datos de Precios de Idealista
    if incluir_precios:
        precios_data = load_idealista_data()
        if not precios_data.empty:
            precios_data['geometry'] = precios_data['geometry'].apply(json.loads)
            precios_data = gpd.GeoDataFrame(precios_data, geometry=precios_data['geometry'].apply(shape))

            min_price = int(precios_data['precio_2022_euros_m2'].min())
            max_price = int(precios_data['precio_2022_euros_m2'].max())
            
            min_selected, max_selected = st.sidebar.slider(
                "Selecciona el rango de precios (€ por m²):",
                min_value=min_price,
                max_value=max_price,
                value=(min_price, max_price)
            )

            filtered_precios = precios_data[
                (precios_data['precio_2022_euros_m2'] >= min_selected) & 
                (precios_data['precio_2022_euros_m2'] <= max_selected)
            ]

            if not filtered_precios.empty:
                visible_zone = filtered_precios.unary_union

                filtered_precios['color'] = filtered_precios['precio_2022_euros_m2'].apply(
                    lambda x: calculate_price_color(x, min_price, max_price)
                )

                precios_layer = pdk.Layer(
                    "GeoJsonLayer",
                    data=filtered_precios,
                    get_fill_color="color",
                    get_line_color=[0, 0, 0],
                    pickable=True,
                    get_tooltip=True
                )
                layers.append(precios_layer)

    # 🗂️ 2️⃣ Cargar los datos de Ruido (solo en la zona de precios)
    if incluir_ruido and visible_zone:
        ruido_data = load_ruido_data()
        if not ruido_data.empty:
            ruido_data['geometry'] = ruido_data['geometry'].apply(json.loads)
            ruido_data = gpd.GeoDataFrame(ruido_data, geometry=ruido_data['geometry'].apply(shape))
            
            ruido_data = ruido_data[ruido_data.geometry.intersects(visible_zone)]

            ruido_data['color'] = ruido_data['gridcode'].apply(get_ruido_color)

            ruido_layer = pdk.Layer(
                "GeoJsonLayer",
                data=ruido_data,
                get_fill_color="color",
                get_line_color=[0, 0, 0],
                pickable=True,
                opacity=0.5 
            )
            layers.append(ruido_layer)

    # 🗂️ 3️⃣ Cargar los datos de Colegios
    if incluir_colegios and visible_zone:
        colegios_data = load_colegios_data()
        if not colegios_data.empty:
            colegios_data = gpd.GeoDataFrame(colegios_data, geometry=[Point(xy) for xy in zip(colegios_data['lon'], colegios_data['lat'])])
            colegios_data = colegios_data[colegios_data.geometry.within(visible_zone)]

            colegios_layer = pdk.Layer(
                "ScatterplotLayer",
                data=colegios_data,
                get_position=["lon", "lat"],
                get_color=[0, 0, 255], 
                radius_min_pixels=6,
                pickable=True,
                get_tooltip=True
            )
            layers.append(colegios_layer)

    # 🗂️ 4️⃣ Cargar los datos de Centros de Discapacidad
    if incluir_discapacidad and visible_zone:
        discapacidad_data = load_discapacidad_data()
        if not discapacidad_data.empty:
            discapacidad_data = gpd.GeoDataFrame(discapacidad_data, geometry=[Point(xy) for xy in zip(discapacidad_data['lon'], discapacidad_data['lat'])])
            discapacidad_data = discapacidad_data[discapacidad_data.geometry.within(visible_zone)]

            discapacidad_layer = pdk.Layer(
                "ScatterplotLayer",
                data=discapacidad_data,
                get_position=["lon", "lat"],
                get_color=[128, 0, 128], 
                radius_min_pixels=6,
                pickable=True,
                get_tooltip=True
            )
            layers.append(discapacidad_layer)

    view_state = pdk.ViewState(
        latitude=39.46975,
        longitude=-0.37739,
        zoom=12,
        pitch=0
    )

    tooltip = {
        "html": """
        <b>Nombre del centro:</b> {nombre}<br>
        <b>Dirección:</b> {direccion}<br>
        <b>Tipo de centro:</b> {tipo_centro}<br>
        """,
        "style": {"backgroundColor": "steelblue", "color": "white", "fontSize": "12px"}
    }

    r = pdk.Deck(
        layers=layers,
        initial_view_state=view_state,
        map_style="mapbox://styles/mapbox/streets-v11",
        tooltip=tooltip
    )

    st.pydeck_chart(r)

if __name__ == "__main__":
    main()