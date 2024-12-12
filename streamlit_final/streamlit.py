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
from ruido import load_ruido_data, get_ruido_color  
from hospitales import load_hospitales_data
from fgv_estaciones import load_fgv_estaciones_data 

# 🌈 Función para calcular el color del precio
def calculate_price_color(price, min_price, max_price):
    norm = (price - min_price) / (max_price - min_price)
    r = int(255 * norm)
    g = int(255 * (1 - norm))
    return [r, g, 0, 150]  # Transparencia de 150

# 🌈 Función para calcular el color de la vulnerabilidad
def calculate_vulnerability_color(index, min_val, max_val):
    norm = (index - min_val) / (max_val - min_val)
    r = int(255 * norm)
    g = int(255 * (1 - norm))
    return [r, g, 0, 150]  # Transparencia de 150



# 🚀 Función principal
def main():
    st.title("Mapa Interactivo de Valencia 🗺️")

    # 🔧 Opciones de Visualización
    st.sidebar.title("🔧 Incluir las siguientes capas:")
    incluir_precios = True
    incluir_vulnerabilidad = st.sidebar.radio("¿Incluir vulnerabilidad de barrios?", ("No", "Sí")) == "Sí"
    incluir_ruido = st.sidebar.radio("¿Incluir ruido?", ("No", "Sí")) == "Sí"

    incluir_colegios = st.sidebar.radio("¿Incluir colegios?", ("No", "Sí")) == "Sí"
    indispensable_colegios = st.sidebar.checkbox("Colegios: Indispensable")

    incluir_discapacidad = st.sidebar.radio("¿Incluir centros de discapacidad?", ("No", "Sí")) == "Sí"
    indispensable_discapacidad = st.sidebar.checkbox("Discapacidad: Indispensable")

    incluir_hospitales = st.sidebar.radio("¿Incluir hospitales?", ("No", "Sí")) == "Sí"
    indispensable_hospitales = st.sidebar.checkbox("Hospitales: Indispensable")

    incluir_estaciones_fgv = st.sidebar.radio("¿Incluir estaciones FGV?", ("No", "Sí")) == "Sí"
    indispensable_estaciones_fgv = st.sidebar.checkbox("Estaciones FGV: Indispensable")

    # 🔧 Filtro de tipo de colegio
    tipo_colegio = st.sidebar.selectbox(
        "Selecciona el tipo de colegio a visualizar:",
        ["Indiferente", "PÚBLICO", "CONCERTADO", "PRIVADO"]
    )

    layers = []
    visible_zone = None

    # 🗂️ 1️⃣ Cargar los datos de Precios de Idealista
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
                pickable=True
            )
            layers.append(precios_layer)

    # 🗂️ 2️⃣ Cargar los datos de vulnerabilidad
    if incluir_vulnerabilidad and visible_zone:
        vulnerabilidad_data = load_vulnerabilidad_barrios_data()
        if not vulnerabilidad_data.empty:
            vulnerabilidad_data['geometry'] = vulnerabilidad_data['geometry'].apply(json.loads)
            vulnerabilidad_data = gpd.GeoDataFrame(vulnerabilidad_data, geometry=vulnerabilidad_data['geometry'].apply(shape))
            
            vulnerabilidad_data = vulnerabilidad_data[vulnerabilidad_data.geometry.intersects(visible_zone)]

            min_val = vulnerabilidad_data['ind_global'].min()
            max_val = vulnerabilidad_data['ind_global'].max()

            vulnerabilidad_data['color'] = vulnerabilidad_data['ind_global'].apply(
                lambda x: calculate_vulnerability_color(x, min_val, max_val)
            )

            vulnerabilidad_layer = pdk.Layer(
                "GeoJsonLayer",
                data=vulnerabilidad_data,
                get_fill_color="color",
                get_line_color=[0, 0, 0],
                pickable=True
            )
            layers.append(vulnerabilidad_layer)


    # 🗂️ 3️⃣ Cargar los datos de Ruido
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


    # 🗂️ 3️⃣ Cargar los datos de Hospitales
    if incluir_hospitales and visible_zone:
        hospitales_data = load_hospitales_data()
        if not hospitales_data.empty:
            hospitales_data = gpd.GeoDataFrame(hospitales_data, geometry=[Point(xy) for xy in zip(hospitales_data['lon'], hospitales_data['lat'])])
            hospitales_data = hospitales_data[hospitales_data.geometry.within(visible_zone)]

            hospitales_layer = pdk.Layer(
                "ScatterplotLayer",
                data=hospitales_data,
                get_position=["lon", "lat"],
                get_color=[255, 0, 0], 
                radius_min_pixels=10,
                pickable=True
            )
            layers.append(hospitales_layer)

    # Si hospitales es indispensable y no hay datos
    if indispensable_hospitales and (not incluir_hospitales or visible_zone is None):
        layers = []
        st.warning("Debes seleccionar una capa de hospitales para continuar.")
        return

    # 🗂️ 2️⃣ Cargar los datos de Colegios
    if incluir_colegios and visible_zone:
        colegios_data = load_colegios_data()
        if not colegios_data.empty:
            colegios_data = gpd.GeoDataFrame(
                colegios_data, geometry=[Point(xy) for xy in zip(colegios_data['lon'], colegios_data['lat'])]
            )
            colegios_data = colegios_data[colegios_data.geometry.within(visible_zone)]

            # ✅ Filtro por tipo de colegio en la columna `regimen`
            if tipo_colegio != "Indiferente":
                colegios_data = colegios_data[colegios_data['regimen'].str.strip().str.upper() == tipo_colegio]

            if not colegios_data.empty:
                colegios_layer = pdk.Layer(
                    "ScatterplotLayer",
                    data=colegios_data,
                    get_position=["lon", "lat"],
                    get_color=[0, 0, 255],  # Azul para todos los colegios
                    radius_min_pixels=6,
                    pickable=True
                )
                layers.append(colegios_layer)
    
        # Si colegios es indispensable y no hay datos
    if indispensable_colegios and (not incluir_colegios or visible_zone is None):
        layers = []
        st.warning("Debes seleccionar una capa de colegios para continuar.")
        return

    # 🗂️ 5️⃣ Cargar los datos de Centros de Discapacidad
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
                pickable=True
            )
            layers.append(discapacidad_layer)

     # 🗂️ 2️⃣ Cargar los datos de estaciones FGV
    if incluir_estaciones_fgv and visible_zone:
        estaciones_data = load_fgv_estaciones_data()
        if not estaciones_data.empty:
            # Convertir a GeoDataFrame y crear geometrías de puntos
            estaciones_gdf = gpd.GeoDataFrame(
                estaciones_data,
                geometry=[Point(xy) for xy in zip(estaciones_data['lon'], estaciones_data['lat'])],
                crs="EPSG:4326"
            )

            # Filtrar las estaciones que están dentro de la zona visible (visible_zone)
            estaciones_filtradas = estaciones_gdf[estaciones_gdf.geometry.within(visible_zone)]

            if not estaciones_filtradas.empty:
                estaciones_layer = pdk.Layer(
                    "ScatterplotLayer",
                    data=estaciones_filtradas,
                    get_position=["lon", "lat"],
                    get_color=[255, 223, 0],  # Color amarillo
                    radius_min_pixels=8,
                    pickable=True
                )
                layers.append(estaciones_layer)

            # Si las estaciones son indispensables pero no hay datos
            elif indispensable_estaciones_fgv:
                st.warning("No hay estaciones FGV disponibles en la zona seleccionada con el filtro de precios.")
                layers = []
                return

    # Si discapacidad  es indispensable y no hay datos
    if indispensable_discapacidad and (not incluir_discapacidad or visible_zone is None):
        layers = []
        st.warning("Debes seleccionar una capa de discapacidad para continuar.")
        return

    view_state = pdk.ViewState(
        latitude=39.46975,
        longitude=-0.37739,
        zoom=12,
        pitch=0
    )

    r = pdk.Deck(
        layers=layers,
        initial_view_state=view_state,
        map_style="mapbox://styles/mapbox/streets-v11"
    )

    st.pydeck_chart(r)

        # 🔎 Agregar leyenda
    st.markdown("""
    🟢 **Precios bajos** 🔵 **Colegios** 🟣 **Centros de discapacidad** 🔴 **Hospitales** 🟡 **Estaciones FGV**
    """)
# Al final del bloque principal del `main()` añadimos:
    if incluir_colegios or incluir_discapacidad or incluir_hospitales:
        # Inicializar conteo de puntos por barrio y categorías
        puntos_por_zona = {
            barrio: {"Colegios": 0, "Hospitales": 0, "Centros de Discapacidad": 0}
            for barrio in filtered_precios["barrio"]
        }

        # Calcular puntos por categoría (si hay capas activadas)
        for _, zona in filtered_precios.iterrows():
            zona_geom = shape(zona["geometry"])

            # Contar colegios
            if incluir_colegios and 'colegios_data' in locals() and not colegios_data.empty:
                colegios_en_zona = colegios_data[colegios_data.geometry.within(zona_geom)]
                puntos_por_zona[zona["barrio"]]["Colegios"] += len(colegios_en_zona)

            # Contar hospitales
            if incluir_hospitales and 'hospitales_data' in locals() and not hospitales_data.empty:
                hospitales_en_zona = hospitales_data[hospitales_data.geometry.within(zona_geom)]
                puntos_por_zona[zona["barrio"]]["Hospitales"] += len(hospitales_en_zona)

            # Contar centros de discapacidad
            if incluir_discapacidad and 'discapacidad_data' in locals() and not discapacidad_data.empty:
                discapacidad_en_zona = discapacidad_data[discapacidad_data.geometry.within(zona_geom)]
                puntos_por_zona[zona["barrio"]]["Centros de Discapacidad"] += len(discapacidad_en_zona)

        # Crear tabla con los resultados
        resultados = pd.DataFrame([
            {
                "Barrio": barrio,
                "Distrito": filtered_precios[filtered_precios["barrio"] == barrio]["distrito"].iloc[0],
                **puntos,
                "Total": sum(puntos.values())
            }
            for barrio, puntos in puntos_por_zona.items()
        ])

        # Ordenar los resultados y quedarnos con los 3 mejores por el total
        resultados = resultados.sort_values(by="Total", ascending=False).head(3)

        # Mostrar los resultados
        if not resultados.empty:
            st.markdown("### 🏆 Los 3 mejores barrios según tus preferencias:")
            for _, row in resultados.iterrows():
                st.markdown(
                    f"El mejor barrio para vivir es {row['Barrio']}, situado en el distrito de {row['Distrito']} con "
                    f"{row['Colegios']} colegios, {row['Hospitales']} hospitales, "
                    f"{row['Centros de Discapacidad']} centros de discapacidad."
                )

            # Mostrar la tabla completa sin el índice
            st.markdown("### Tabla de los mejores barrios:")
            st.dataframe(resultados[["Barrio", "Distrito", "Colegios", "Hospitales", "Centros de Discapacidad"]])
            


if __name__ == "__main__":
    main()
