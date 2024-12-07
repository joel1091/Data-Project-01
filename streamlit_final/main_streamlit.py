import streamlit as st
import pydeck as pdk
from colegios import load_data as load_colegios_data, assign_colors
from cajeros import load_atm_data

# Función para generar un indicador de color
def color_legend(capas_seleccionadas):
    legend_html = ""
    colores = {
        "Colegios": "blue",  # Color azul para colegios
        "Cajeros": "pink"    # Color rosa para cajeros
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
    st.title("Mapa Interactivo: Colegios y Cajeros en Valencia")

    # Panel izquierdo: Configuración general
    st.sidebar.title("Opciones Generales")
    capas = st.sidebar.multiselect(
        "Selecciona las capas que deseas ver:",
        options=["Colegios", "Cajeros"],
        default=["Colegios", "Cajeros"]
    )

    # Panel derecho: Configuración para colegios
    st.sidebar.title("Opciones para Colegios")
    tiene_hijos = st.sidebar.radio(
        "¿Tiene hijos en edad de ir al colegio?",
        ("No", "Sí")
    )

    regimen_opcion = None
    if tiene_hijos == "Sí":
        regimen_opcion = st.sidebar.selectbox(
            "¿A qué tipo de colegio le gustaría llevar a su hijo?",
            ("CONCERTADO", "PÚBLICO", "PRIVADO")
        )

    # Cargar datos
    colegios_data = load_colegios_data() if "Colegios" in capas and tiene_hijos == "Sí" else None
    cajeros_data = load_atm_data() if "Cajeros" in capas else None

    # Filtrar datos de colegios si se selecciona "Sí" en la pregunta inicial
    if colegios_data is not None:
        colegios_data = colegios_data[colegios_data["regimen"] == regimen_opcion]
        colegios_data = assign_colors(colegios_data)

    # Configurar el estado inicial del mapa
    view_state = pdk.ViewState(
        latitude=39.4699,  # Coordenadas aproximadas de Valencia
        longitude=-0.3763,
        zoom=13,
        pitch=0  # Sin inclinación (2D)
    )

    layers = []

    # Crear capa de colegios
    if colegios_data is not None and not colegios_data.empty:
        colegios_layer = pdk.Layer(
            "ScatterplotLayer",
            data=colegios_data,
            get_position=["lon", "lat"],
            get_color="color",  # Usar la columna de colores asignados
            radius_min_pixels=5,  # Tamaño constante de los puntos
            radius_max_pixels=5,
            pickable=True
        )
        layers.append(colegios_layer)

    # Crear capa de cajeros
    if cajeros_data is not None and not cajeros_data.empty:
        cajeros_layer = pdk.Layer(
            "ScatterplotLayer",
            data=cajeros_data,
            get_position=["lon", "lat"],
            get_color=[255, 105, 180, 160],  # Rosa con transparencia
            get_radius=20,  # Tamaño de los puntos
            pickable=True
        )
        layers.append(cajeros_layer)

    # Configurar el tooltip dinámico
    tooltip = {
        "html": """
        <b>Nombre o Modelo:</b> {nombre_centro}{modelo}<br>
        <b>Dirección:</b> {direccion}<br>
        <b>Barrio o Municipio:</b> {barrio}{municipio}<br>
        <b>Régimen:</b> {regimen}
        """,
        "style": {"backgroundColor": "black", "color": "white"}
    }

    # Crear y mostrar el mapa con las capas seleccionadas
    r = pdk.Deck(
        layers=layers,
        initial_view_state=view_state,
        map_style="mapbox://styles/mapbox/streets-v11",
        tooltip=tooltip
    )

    st.pydeck_chart(r)

    # Mostrar la leyenda a la derecha
    st.markdown("<h3>Capas Seleccionadas</h3>", unsafe_allow_html=True)
    legend = color_legend(capas)
    st.markdown(legend, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
