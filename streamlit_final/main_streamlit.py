import streamlit as st
import pydeck as pdk
import geopandas as gpd
import pandas as pd
from shapely.geometry import Point, shape
import json

# 🔄 Importar funciones desde los archivos correspondientes
from idealista import load_idealista_data
from colegios import load_data as load_colegios_data
from discapacidad import load_discapacidad_data
from hospitales import load_hospitales_data

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
    incluir_colegios = st.sidebar.radio("¿Incluir colegios?", ("No", "Sí")) == "Sí"
    incluir_discapacidad = st.sidebar.radio("¿Incluir centros de discapacidad?", ("No", "Sí")) == "Sí"
    incluir_hospitales = st.sidebar.radio("¿Incluir hospitales?", ("No", "Sí")) == "Sí"

    indispensable_colegios = st.sidebar.checkbox("Colegios: Indispensable")
    indispensable_discapacidad = st.sidebar.checkbox("Discapacidad: Indispensable")
    indispensable_hospitales = st.sidebar.checkbox("Hospitales: Indispensable")

    # Mostrar desplegable de tipos de colegios si está activada la capa de colegios
    tipo_colegio = None
    if incluir_colegios:
        tipo_colegio = st.sidebar.selectbox(
            "Selecciona el tipo de colegio a visualizar:",
            ["Todos", "PÚBLICO", "CONCERTADO", "PRIVADO"]
        )

    # Dividir la página en columnas con proporciones ajustadas
    col1, col2 = st.columns([6, 2])  # 6/7 para el mapa y 1/7 para la leyenda

    with col1:
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
                    # Crear una columna para identificar zonas filtradas con puntos
                    filtered_precios["has_points"] = True

                    # Crear lista para acumular puntos de las capas activadas
                    all_points = []

                    # Colegios
                    if incluir_colegios:
                        colegios_data = load_colegios_data()
                        if not colegios_data.empty:
                            colegios_data = gpd.GeoDataFrame(
                                colegios_data, geometry=[Point(xy) for xy in zip(colegios_data['lon'], colegios_data['lat'])]
                            )
                            colegios_data["regimen"] = colegios_data["regimen"].str.strip().str.upper()
                            if tipo_colegio and tipo_colegio != "Todos":
                                colegios_data = colegios_data[colegios_data["regimen"] == tipo_colegio]
                            all_points.append(colegios_data)

                    # Centros de discapacidad
                    if incluir_discapacidad:
                        discapacidad_data = load_discapacidad_data()
                        if not discapacidad_data.empty:
                            discapacidad_data = gpd.GeoDataFrame(
                                discapacidad_data, geometry=[Point(xy) for xy in zip(discapacidad_data['lon'], discapacidad_data['lat'])]
                            )
                            all_points.append(discapacidad_data)

                    # Hospitales
                    if incluir_hospitales:
                        hospitales_data = load_hospitales_data()
                        if not hospitales_data.empty:
                            hospitales_data = gpd.GeoDataFrame(
                                hospitales_data, geometry=[Point(xy) for xy in zip(hospitales_data['lon'], hospitales_data['lat'])]
                            )
                            all_points.append(hospitales_data)

                    # Si no hay puntos seleccionados, mostrar todas las zonas coloreadas
                    if not all_points:
                        visible_zone = filtered_precios.unary_union
                    else:
                        # Unir todos los puntos activados
                        all_points_gdf = gpd.GeoDataFrame(pd.concat(all_points, ignore_index=True))

                        # Verificar intersección de zonas con los puntos
                        for idx, zone in filtered_precios.iterrows():
                            if all_points_gdf.geometry.intersects(zone.geometry).any():
                                filtered_precios.at[idx, "has_points"] = True
                            else:
                                filtered_precios.at[idx, "has_points"] = False

                        # Filtrar solo las zonas que tienen puntos
                        filtered_precios = filtered_precios[filtered_precios["has_points"]]
                        visible_zone = filtered_precios.unary_union

                    if not filtered_precios.empty:
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

        # 🗂️ 2️⃣ Añadir puntos como capas
        def filter_and_add_layer(data, color, layer_name, indispensable):
            """
            Filtra puntos dentro de las zonas visibles y los añade como una capa.
            """
            if visible_zone and not data.empty:
                filtered_data = data[data.geometry.within(visible_zone)]

                if not filtered_data.empty:
                    layer = pdk.Layer(
                        "ScatterplotLayer",
                        data=filtered_data,
                        get_position=["lon", "lat"],
                        get_color=color,
                        radius_min_pixels=6,
                        pickable=True
                    )
                    layers.append(layer)
                elif indispensable:
                    st.warning(f"No hay {layer_name} disponibles en la zona seleccionada con el filtro aplicado.")
                    layers.clear()  # Borra las capas si es indispensable
                    return False
            return True

        # Añadir capa de colegios
        if incluir_colegios:
            success = filter_and_add_layer(colegios_data, [0, 0, 255], "colegios", indispensable_colegios)
            if not success:
                return

        # Añadir capa de discapacidad
        if incluir_discapacidad:
            success = filter_and_add_layer(discapacidad_data, [128, 0, 128], "centros de discapacidad", indispensable_discapacidad)
            if not success:
                return

        # Añadir capa de hospitales
        if incluir_hospitales:
            success = filter_and_add_layer(hospitales_data, [255, 0, 0], "hospitales", indispensable_hospitales)
            if not success:
                return

        # Configuración del mapa
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

        # Mostrar el mapa
        st.pydeck_chart(r)

    # Leyenda en la columna derecha
    with col2:
        st.markdown("### Leyenda")
        st.markdown(
            """
            <style>
            .legend ul {
                list-style-type: none;
                padding: 0;
                margin: 0;
                font-size: 16px;
                line-height: 1.8;
            }
            .legend li {
                display: flex;
                align-items: center;
                margin-bottom: 8px;
            }
            .legend span {
                display: inline-block;
                width: 16px;
                height: 16px;
                margin-right: 8px;
                border-radius: 50%;
            }
            </style>
            <div class="legend">
                <ul>
                    <li><span style="background: rgb(255, 0, 0);"></span> Hospitales</li>
                    <li><span style="background: rgb(128, 0, 128);"></span> Centros de Discapacidad</li>
                    <li><span style="background: rgb(0, 0, 255);"></span> Colegios</li>
                    <li><span style="background: rgba(255, 255, 0, 0.8);"></span> Zonas de Precios</li>
                </ul>
            </div>
            """,
            unsafe_allow_html=True
        )

# Al final del bloque principal del `main()` añadimos:
    if incluir_precios:
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
            for i, row in resultados.iterrows():
                st.markdown(
                    f"**{i + 1}. Barrio:** {row['Barrio']} (Distrito: {row['Distrito']}) - "
                    f"**{row['Colegios']} colegios**, **{row['Hospitales']} hospitales**, "
                    f"**{row['Centros de Discapacidad']} centros de discapacidad**."
                )

            # Mostrar la tabla completa sin el índice
            st.markdown("### Tabla de los mejores barrios:")
            st.dataframe(resultados[["Barrio", "Distrito", "Colegios", "Hospitales", "Centros de Discapacidad"]])


if __name__ == "__main__":
    main()
