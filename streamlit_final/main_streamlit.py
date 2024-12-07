import streamlit as st
import pydeck as pdk
from colegios import load_data as load_colegios_data, assign_colors
from centros_mayores import load_centros_mayores_data
from discapacidad import load_discapacidad_data
from fgv_estaciones import load_fgv_estaciones_data
from hospitales import load_hospitales_data
from valenbisi import load_valenbisi_data
from idealista import load_idealista_data
from vulnerabilidad_barrios import load_vulnerabilidad_barrios_data
import pandas as pd
import json

# Configuración de colores para la leyenda
def color_legend(capas_seleccionadas):
    legend_html = ""
    colores = {
        "Colegios": "blue",
        "Centros de Mayores": "black",
        "Discapacidad": "purple",
        "Estaciones FGV": "yellow",
        "Hospitales": "red",
        "Valenbisi": "green",
        "Precios por Zonas": "orange",
        "Vulnerabilidad de Barrios": "pink"
    }
    for capa in capas_seleccionadas:
        if capa in colores:
            legend_html += f"""
            <div style="display: flex; align-items: center; margin-bottom: 8px;">
                <div style="height: 12px; width: 12px; background-color: {colores[capa]}; border-radius: 50%; margin-right: 8px;"></div>
                <span>{capa}</span>
            </div>
            """
    return legend_html

# Aplicación principal
def main():
    st.title("Mapa Interactivo: Servicios y Vulnerabilidad de Barrios en Valencia")

    # Panel izquierdo: Configuración general
    st.sidebar.title("Opciones Generales")
    capas = st.sidebar.multiselect(
        "Selecciona las capas que deseas ver:",
        options=[
            "Colegios",
            "Centros de Mayores",
            "Discapacidad",
            "Estaciones FGV",
            "Hospitales",
            "Valenbisi",
            "Precios por Zonas",
            "Vulnerabilidad de Barrios"
        ],
        default=[
            "Colegios",
            "Centros de Mayores",
            "Discapacidad",
            "Estaciones FGV",
            "Hospitales",
            "Valenbisi",
            "Precios por Zonas",
            "Vulnerabilidad de Barrios"
        ]
    )

    # Panel izquierdo: Opciones para colegios
    st.sidebar.title("Opciones para Colegios")
    tiene_hijos = st.sidebar.radio(
        "¿Tiene hijos en edad de ir al colegio?",
        ("No", "Sí")
    )

    regimen_opcion = None
    if tiene_hijos == "Sí":
        regimen_opcion = st.sidebar.selectbox(
            "¿A qué tipo de colegio le gustaría llevar a su hijo?",
            ("Todos los tipos", "CONCERTADO", "PÚBLICO", "PRIVADO")
        )

    # Panel izquierdo: Opciones para hospitales
    st.sidebar.title("Opciones para Hospitales")
    tipo_hospital = st.sidebar.selectbox(
        "¿Qué tipo de hospital desea visualizar?",
        ("Todos los tipos", "Publico", "Concertado", "Privado")
    )

    # Cargar los datos de todas las capas seleccionadas
    colegios_data = load_colegios_data() if "Colegios" in capas else None
    centros_mayores_data = load_centros_mayores_data() if "Centros de Mayores" in capas else None
    discapacidad_data = load_discapacidad_data() if "Discapacidad" in capas else None
    fgv_estaciones_data = load_fgv_estaciones_data() if "Estaciones FGV" in capas else None
    hospitales_data = load_hospitales_data() if "Hospitales" in capas else None
    valenbisi_data = load_valenbisi_data() if "Valenbisi" in capas else None
    precios_data = load_idealista_data() if "Precios por Zonas" in capas else None
    vulnerabilidad_data = load_vulnerabilidad_barrios_data() if "Vulnerabilidad de Barrios" in capas else None

    # Configurar el estado inicial del mapa
    view_state = pdk.ViewState(
        latitude=39.4699,
        longitude=-0.3763,
        zoom=13,
        pitch=0
    )

    layers = []

    # Capa de colegios (con filtro por tipo de régimen)
    if colegios_data is not None and not colegios_data.empty:
        if regimen_opcion and regimen_opcion != "Todos los tipos":
            colegios_data = colegios_data[colegios_data["regimen"].str.upper() == regimen_opcion.upper()]
        colegios_data = assign_colors(colegios_data)

        colegios_layer = pdk.Layer(
            "ScatterplotLayer",
            data=colegios_data,
            get_position=["lon", "lat"],
            get_color=[0, 0, 255],  # Azul
            radius_min_pixels=8,
            pickable=True
        )
        layers.append(colegios_layer)

    # Capa de hospitales (con filtro por tipo de financiación)
    if hospitales_data is not None and not hospitales_data.empty:
        if tipo_hospital and tipo_hospital != "Todos los tipos":
            hospitales_data = hospitales_data[hospitales_data["financiacion"].str.upper() == tipo_hospital.upper()]

        hospitales_layer = pdk.Layer(
            "ScatterplotLayer",
            data=hospitales_data,
            get_position=["lon", "lat"],
            get_color=[255, 0, 0],  # Rojo
            radius_min_pixels=8,
            pickable=True
        )
        layers.append(hospitales_layer)

    # Capa de vulnerabilidad de barrios (con barra deslizante)
    if vulnerabilidad_data is not None and not vulnerabilidad_data.empty:
        min_vulnerability = round(vulnerabilidad_data["ind_global"].min(), 2)
        max_vulnerability = round(vulnerabilidad_data["ind_global"].max(), 2)

        max_vulnerability_slider = st.sidebar.slider(
            "Selecciona el nivel máximo de vulnerabilidad:",
            min_value=min_vulnerability,
            max_value=max_vulnerability,
            value=max_vulnerability,
            step=0.01
        )

        # Filtrar las zonas por el nivel máximo de vulnerabilidad
        vulnerabilidad_data = vulnerabilidad_data[vulnerabilidad_data["ind_global"] <= max_vulnerability_slider]

        def get_color(vulnerability):
            if vulnerability == "Vulnerabilidad Alta":
                return [255, 0, 0, 150]  # Rojo
            elif vulnerability == "Vulnerabilidad Media":
                return [255, 165, 0, 150]  # Naranja
            elif vulnerability == "Vulnerabilidad Baja":
                return [0, 255, 0, 150]  # Verde
            else:
                return [200, 200, 200, 150]  # Gris para valores desconocidos

        vulnerabilidad_data["color"] = vulnerabilidad_data["ind_global_txt"].apply(get_color)
        vulnerabilidad_data["geometry"] = vulnerabilidad_data["geometry"].apply(json.loads)

        vulnerabilidad_layer = pdk.Layer(
            "GeoJsonLayer",
            data=vulnerabilidad_data,
            get_fill_color="color",
            get_line_color=[0, 0, 0],  # Bordes negros
            pickable=True,
        )
        layers.append(vulnerabilidad_layer)

    # Capa de precios por zonas (con barra deslizante)
    if precios_data is not None and not precios_data.empty:
        max_price = st.sidebar.slider(
            "Selecciona tu presupuesto máximo (€ por m²):",
            min_value=int(precios_data["precio_2022_euros_m2"].min()),
            max_value=int(precios_data["precio_2022_euros_m2"].max()),
            value=int(precios_data["precio_2022_euros_m2"].max())
        )

        filtered_precios = precios_data[precios_data["precio_2022_euros_m2"] <= max_price]
        filtered_precios["geometry"] = filtered_precios["geometry"].apply(json.loads)

        precios_layer = pdk.Layer(
            "GeoJsonLayer",
            data=filtered_precios,
            get_fill_color="[255, 165, 0, 150]",  # Naranja
            get_line_color=[0, 0, 0],  # Bordes negros
            pickable=True
        )
        layers.append(precios_layer)

    # Capa de centros de mayores
    if centros_mayores_data is not None and not centros_mayores_data.empty:
        centros_mayores_layer = pdk.Layer(
            "ScatterplotLayer",
            data=centros_mayores_data,
            get_position=["lon", "lat"],
            get_color=[0, 0, 0],  # Negro
            radius_min_pixels=8,
            pickable=True
        )
        layers.append(centros_mayores_layer)

    # Capa de discapacidad
    if discapacidad_data is not None and not discapacidad_data.empty:
        discapacidad_layer = pdk.Layer(
            "ScatterplotLayer",
            data=discapacidad_data,
            get_position=["lon", "lat"],
            get_color=[128, 0, 128],  # Morado
            radius_min_pixels=8,
            pickable=True
        )
        layers.append(discapacidad_layer)

    # Capa de estaciones FGV
    if fgv_estaciones_data is not None and not fgv_estaciones_data.empty:
        fgv_layer = pdk.Layer(
            "ScatterplotLayer",
            data=fgv_estaciones_data,
            get_position=["lon", "lat"],
            get_color=[255, 223, 0],  # Amarillo
            radius_min_pixels=8,
            pickable=True
        )
        layers.append(fgv_layer)

    # Capa de Valenbisi
    if valenbisi_data is not None and not valenbisi_data.empty:
        valenbisi_layer = pdk.Layer(
            "ScatterplotLayer",
            data=valenbisi_data,
            get_position=["lon", "lat"],
            get_color=[0, 255, 0],  # Verde
            radius_min_pixels=8,
            pickable=True
        )
        layers.append(valenbisi_layer)

    # Crear y mostrar el mapa con las capas seleccionadas
    r = pdk.Deck(
        layers=layers,
        initial_view_state=view_state,
        map_style="mapbox://styles/mapbox/streets-v11"
    )

    st.pydeck_chart(r)

    # Mostrar la leyenda
    st.markdown("<h3>Capas Seleccionadas</h3>", unsafe_allow_html=True)
    legend = color_legend(capas)
    st.markdown(legend, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
