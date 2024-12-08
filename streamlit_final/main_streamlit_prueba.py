import streamlit as st
import pydeck as pdk
import geopandas as gpd
import pandas as pd
from shapely.geometry import Point, shape
from idealista import load_idealista_data
from vulnerabilidad_barrios import load_vulnerabilidad_barrios_data
from colegios import load_data as load_colegios_data, assign_colors
from discapacidad import load_discapacidad_data  # Asegúrate de tener esta función
import json

def main():
    st.title("Mapa Interactivo Valencia")

    # Panel izquierdo: Selección de visualización
    st.sidebar.title("Opciones de Visualización")
    opciones_visualizacion = st.sidebar.multiselect(
        "Selecciona las capas que deseas visualizar:",
        options=["Precios por Zonas", "Vulnerabilidad de Barrios", "Colegios", "Centros de Discapacidad"],
        default=["Precios por Zonas", "Vulnerabilidad de Barrios", "Colegios"]
    )

    # Elegir qué factor tendrá más peso (Precios o Vulnerabilidad)
    factor_color = st.sidebar.radio("¿Qué factor prefieres para colorear el mapa?", ("Precios", "Vulnerabilidad"))
    
    # Peso para cada factor (se ajusta entre 0 y 1)
    if factor_color == "Precios":
        peso_precios = st.sidebar.slider("¿Qué peso tienen los precios? (1 es el máximo)", 0.0, 1.0, 1.0)
        peso_vulnerabilidad = 1.0 - peso_precios
    else:
        peso_vulnerabilidad = st.sidebar.slider("¿Qué peso tiene la vulnerabilidad?", 0.0, 1.0, 1.0)
        peso_precios = 1.0 - peso_vulnerabilidad

    layers = []
    visible_geometries = []

    # --- Lógica para Precios por Zonas ---
    if "Precios por Zonas" in opciones_visualizacion:
        precios_data = load_idealista_data()
        if not precios_data.empty:
            precios_data["geometry"] = precios_data["geometry"].apply(json.loads)
            precios_data = gpd.GeoDataFrame(precios_data, geometry=precios_data["geometry"].apply(shape))
            min_price = int(precios_data["precio_2022_euros_m2"].min())
            max_price = int(precios_data["precio_2022_euros_m2"].max())
            min_selected, max_selected = st.sidebar.slider(
                "Selecciona el rango de precios (€ por m²):",
                min_value=min_price,
                max_value=max_price,
                value=(min_price, max_price)
            )
            filtered_precios = precios_data[
                (precios_data["precio_2022_euros_m2"] >= min_selected) & 
                (precios_data["precio_2022_euros_m2"] <= max_selected)
            ]
            visible_geometries.append(filtered_precios.geometry)
            def calculate_price_color(price, vulnerabilidad=None):
                ratio = (price - min_price) / (max_price - min_price) if max_price > min_price else 0
                red = int(255 * ratio)
                green = int(255 * (1 - ratio))
                return [red, green, 0, 150]
            
            filtered_precios["color"] = filtered_precios["precio_2022_euros_m2"].apply(
                lambda x: calculate_price_color(x)
            )
            precios_layer = pdk.Layer(
                "GeoJsonLayer",
                data=filtered_precios,
                get_fill_color="color",
                get_line_color=[0, 0, 0],
                pickable=True,
            )
            layers.append(precios_layer)

    # --- Lógica para Vulnerabilidad de Barrios ---
    if "Vulnerabilidad de Barrios" in opciones_visualizacion:
        vulnerabilidad_data = load_vulnerabilidad_barrios_data()
        if not vulnerabilidad_data.empty:
            vulnerabilidad_data["geometry"] = vulnerabilidad_data["geometry"].apply(json.loads)
            vulnerabilidad_data = gpd.GeoDataFrame(vulnerabilidad_data, geometry=vulnerabilidad_data["geometry"].apply(shape))
            considerar_vulnerabilidad = st.sidebar.radio(
                "¿Quieres tener en cuenta la vulnerabilidad del barrio?",
                ("No", "Sí")
            )
            if considerar_vulnerabilidad == "Sí":
                min_vulnerability = float(vulnerabilidad_data["ind_global"].min())
                max_vulnerability = float(vulnerabilidad_data["ind_global"].max())
                min_selected_vul, max_selected_vul = st.sidebar.slider(
                    "Selecciona el rango de vulnerabilidad:",
                    min_value=round(min_vulnerability, 2),
                    max_value=round(max_vulnerability, 2),
                    value=(round(min_vulnerability, 2), round(max_vulnerability, 2)),
                    step=0.01
                )
                filtered_vulnerabilidad = vulnerabilidad_data[
                    (vulnerabilidad_data["ind_global"] >= min_selected_vul) & 
                    (vulnerabilidad_data["ind_global"] <= max_selected_vul)
                ]
                visible_geometries.append(filtered_vulnerabilidad.geometry)
                def calculate_vulnerability_color(index, price=None):
                    ratio = (index - min_vulnerability) / (max_vulnerability - min_vulnerability)
                    red = int(255 * ratio)
                    green = int(255 * (1 - ratio))
                    return [red, green, 0, 150]
                
                filtered_vulnerabilidad["color"] = filtered_vulnerabilidad["ind_global"].apply(
                    lambda x: calculate_vulnerability_color(x)
                )
                vulnerabilidad_layer = pdk.Layer(
                    "GeoJsonLayer",
                    data=filtered_vulnerabilidad,
                    get_fill_color="color",
                    get_line_color=[0, 0, 0],
                    pickable=True,
                )
                layers.append(vulnerabilidad_layer)

    # Fusionar geometrías visibles
    if visible_geometries:
        visible_geometries = gpd.GeoSeries(pd.concat(visible_geometries, ignore_index=True)).unary_union

    # --- Lógica para Centros de Discapacidad ---
    if "Centros de Discapacidad" in opciones_visualizacion:
        discapacidad_familiar = st.sidebar.radio("¿Tienes algún discapacitado en la familia?", ("No", "Sí"))
        if discapacidad_familiar == "Sí":
            discapacidad_data = load_discapacidad_data()
            if discapacidad_data is not None and not discapacidad_data.empty:
                discapacidad_data = gpd.GeoDataFrame(
                    discapacidad_data, 
                    geometry=[Point(xy) for xy in zip(discapacidad_data["lon"], discapacidad_data["lat"])]
                )
                # Filtrar los centros de discapacidad que están dentro de las zonas visibles
                if visible_geometries:
                    discapacidad_data = discapacidad_data[discapacidad_data.geometry.intersects(visible_geometries)]
                if discapacidad_data.empty:
                    st.warning("No hay centros de discapacidad disponibles en las zonas visibles.")
                else:
                    discapacidad_layer = pdk.Layer(
                        "ScatterplotLayer",
                        data=discapacidad_data,
                        get_position=["lon", "lat"],
                        get_color=[128, 0, 128],  # Morado
                        radius_min_pixels=4,
                        pickable=True,
                    )
                    layers.append(discapacidad_layer)

    # Cargar y procesar los datos de Colegios
    if "Colegios" in opciones_visualizacion:
        tiene_hijos = st.sidebar.radio("¿Tiene hijos en edad de ir al colegio?", ("No", "Sí"))
        if tiene_hijos == "Sí":
            colegios_data = load_colegios_data()
            if colegios_data.empty:
                st.warning("No se encontraron datos de colegios.")
            else:
                colegios_data = gpd.GeoDataFrame(
                    colegios_data, geometry=[Point(xy) for xy in zip(colegios_data["lon"], colegios_data["lat"])]
                )
                tipo_colegio = st.sidebar.selectbox(
                    "¿Qué tipo de colegio le interesa?",
                    ("No importa el colegio", "CONCERTADO", "PÚBLICO", "PRIVADO")
                )
                if tipo_colegio != "No importa el colegio":
                    colegios_data = colegios_data[colegios_data["regimen"] == tipo_colegio]
                if visible_geometries:
                    colegios_data = colegios_data[colegios_data.geometry.intersects(visible_geometries)]
                if colegios_data.empty:
                    st.warning(f"No hay colegios disponibles en las zonas visibles para el tipo seleccionado: {tipo_colegio}")
                else:
                    colegios_data = assign_colors(colegios_data)
                    scatter_layer = pdk.Layer(
                        "ScatterplotLayer",
                        data=colegios_data,
                        get_position=["lon", "lat"],
                        get_color="color",
                        radius_min_pixels=4,
                        pickable=True,
                    )
                    layers.append(scatter_layer)

    # Configuración del mapa
    view_state = pdk.ViewState(
        latitude=39.46975,
        longitude=-0.37739,
        zoom=12,
        pitch=0
    )

    tooltip = {
        "html": """
        <b>Centro:</b> {nombre_centro}<br>
        <b>Dirección:</b> {direccion}<br>
        <b>Tipo:</b> {regimen}<br>
        """,
        "style": {"backgroundColor": "steelblue", "color": "white"}
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
